import logging
from braces.views import LoginRequiredMixin
from django.conf import settings
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils.timezone import now
from django.views.generic import ListView, FormView, CreateView, DeleteView, DetailView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import ModelFormMixin
from kv1.models import Kv1Journey
from openebs.form import CancelLinesForm, Kv17ChangeForm
from openebs.models import Kv17Change
from openebs.views import FilterDataownerMixin
from utils.views import AccessMixin, GoviPushMixin, JSONListResponseMixin

log = logging.getLogger('openebs.views.changes')

class GoviKv17PushMixin(GoviPushMixin):
    dossier = settings.GOVI_KV17_DOSSIER
    path = settings.GOVI_KV17_PATH
    namespace = settings.GOVI_KV17_NAMESPACE

class ChangeListView(AccessMixin, ListView):
    permission_required = 'openebs.view_change'
    model = Kv17Change

    def get_context_data(self, **kwargs):
        context = super(ChangeListView, self).get_context_data(**kwargs)

        # Get the currently active changes
        context['active_list'] = self.model.objects.filter(operatingday=now().date, is_recovered=False,
                                                           dataownercode=self.request.user.userprofile.company)
        context['active_list'] = context['active_list'].order_by('line__publiclinenumber', 'created')

        # Add the no longer active changes
        context['archive_list'] = self.model.objects.filter(Q(operatingday__lt=now) | Q(is_recovered=True),
                                                            dataownercode=self.request.user.userprofile.company)
        context['archive_list'] = context['archive_list'].order_by('-created')
        return context


class ChangeCreateView(AccessMixin, GoviKv17PushMixin, CreateView):
    permission_required = 'openebs.add_change'
    model = Kv17Change
    form_class = Kv17ChangeForm
    success_url = reverse_lazy('change_index')

    def form_valid(self, form):
        form.instance.dataownercode = self.request.user.userprofile.company

        # TODO this is a bad solution - totally gets rid of any benefit of Django's CBV and Forms
        xml = form.save()

        # Push message to GOVI
        if self.push_govi(xml):
            log.info("Sent KV17 line change to GOVI: %s" % self.request.POST.get('journeys', "<unknown>"))
        else:
            log.error("Failed to communicate KV17 line change to GOVI: %s" % xml)

        # Another hack to redirect correctly
        return HttpResponseRedirect(self.success_url)


class ChangeDeleteView(AccessMixin, GoviKv17PushMixin, FilterDataownerMixin, DeleteView):
    permission_required = 'openebs.add_change'
    model = Kv17Change
    success_url = reverse_lazy('change_index')

    def delete(self, request, *args, **kwargs):
        ret = super(ChangeDeleteView, self).delete(request, *args, **kwargs)
        obj = self.get_object()
        if self.push_govi(obj.to_xml()):
            log.error("Recovered line succesfully communicated to GOVI: %s" % obj)
        else:
            log.error("Failed to send recover request to GOVI: %s" % obj)
            # We failed to push, recover our delete operation
            obj.is_recovered = False
            obj.recovered = None
            obj.save() # Note, this won't work locally!
        return ret

class ChangeUpdateView(AccessMixin, GoviKv17PushMixin, FilterDataownerMixin, DeleteView):
    """ This is a really weird view - it's redoing a change that you deleted   """
    permission_required = 'openebs.add_change'
    model = Kv17Change
    success_url = reverse_lazy('change_index')

    def update_object(self):
        obj = self.get_object()
        obj.is_recovered = False
        obj.recovered = None
        obj.save()
        return obj

    def delete(self, request, *args, **kwargs):
        orig = self.get_object() # Store an original to undo our redo
        obj = self.update_object()
        if self.push_govi(obj.to_xml()):
            log.error("Redo line cancel succesfully communicated to GOVI: %s" % obj)
        else:
            log.error("Failed to send redo request to GOVI: %s" % obj)
            # We failed to push, recover our redo operation by restoring previous state
            obj.is_recovered = orig.is_recovered
            obj.recovered = orig.recovered
            obj.save() # Note, this won't work locally!
        return HttpResponseRedirect(self.get_success_url())

class CancelLinesView(AccessMixin, GoviKv17PushMixin, FormView):
    permission_required = 'openebs.add_change'
    form_class = CancelLinesForm
    template_name = 'openebs/kv17change_redbutton.html'
    success_url = reverse_lazy('change_index')

    def get_context_data(self, **kwargs):
        """ Add data about the trips we'd be cancelling """
        data = super(CancelLinesView, self).get_context_data(**kwargs)
        data['trips'] = Kv17Change.objects.filter(dataownercode=self.request.user.userprofile.company)
        return data

    def form_valid(self, form):
        ret = super(CancelLinesView, self).form_valid(form)
        # Find our scenario
        # Plan messages

        # Concatenate XML for a single request
        message_string = ""
        if self.push_govi(message_string):
            log.error("Planned messages sent to GOVI: %s" % "")
        else:
            log.error("Failed to communicate planned messages to GOVI: %s")
        return ret

class ActiveJourneysAjaxView(LoginRequiredMixin, JSONListResponseMixin, DetailView):
    model = Kv1Journey
    render_object = 'object'

    def get_object(self):
        # Note, can't set this on the view, because it triggers the queryset cache
        queryset = self.model.objects.filter(changes__operatingday=now(),
                                             changes__is_recovered=False,
                                             # These two are double, but just in case
                                             changes__dataownercode=self.request.user.userprofile.company,
                                             dataownercode=self.request.user.userprofile.company).distinct()
        print queryset.count()
        return list(queryset.values('id', 'dataownercode'))