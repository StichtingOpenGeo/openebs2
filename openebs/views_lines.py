import logging
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.utils.timezone import now
from django.views.generic import ListView, FormView, CreateView, DeleteView
from openebs.form import CancelLinesForm, Kv17ChangeForm
from openebs.models import Kv17Change
from openebs.views import FilterDataownerMixin
from utils.views import AccessMixin, GoviPushMixin

log = logging.getLogger('openebs.views.changes')


class ChangeListView(AccessMixin, ListView):
    permission_required = 'openebs.view_changes'
    model = Kv17Change

    def get_context_data(self, **kwargs):
        context = super(ChangeListView, self).get_context_data(**kwargs)

        # Get the currently active changes
        context['active_list'] = self.model.objects.filter(operatingday=now().date, is_recovered=False,
                                                           dataownercode=self.request.user.userprofile.company)
        context['active_list'] = context['active_list'].order_by('-created')

        # Add the no longer active changes
        context['archive_list'] = self.model.objects.filter(Q(operatingday__lt=now) | Q(is_recovered=True),
                                                            dataownercode=self.request.user.userprofile.company)
        context['archive_list'] = context['archive_list'].order_by('-created')
        return context


class ChangeCreateView(AccessMixin, CreateView):
    permission_required = 'openebs.view_changes'
    model = Kv17Change
    form_class = Kv17ChangeForm
    success_url = reverse_lazy('change_index')

    def form_valid(self, form):
        form.instance.dataownercode = self.request.user.userprofile.company
        return super(ChangeCreateView, self).form_valid(form)

class ChangeDeleteView(AccessMixin, FilterDataownerMixin, DeleteView):
    permission_required = 'openebs.view_changes'
    model = Kv17Change
    success_url = reverse_lazy('change_index')

class CancelLinesView(AccessMixin, GoviPushMixin, FormView):
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
