import logging
from braces.views import LoginRequiredMixin
from datetime import timedelta
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, DeleteView, DetailView
from kv1.models import Kv1Journey, Kv1Line
from openebs.form_kv17 import Kv17ChangeForm
from openebs.models import Kv17Change
from openebs.views_push import Kv17PushMixin
from openebs.views_utils import FilterDataownerMixin
from utils.time import get_operator_date
from utils.views import AccessMixin, ExternalMessagePushMixin, JSONListResponseMixin

log = logging.getLogger('openebs.views.changes')


class ChangeListView(AccessMixin, ListView):
    permission_required = 'openebs.view_change'
    model = Kv17Change

    def get_context_data(self, **kwargs):
        context = super(ChangeListView, self).get_context_data(**kwargs)

        # Get the currently active changes
        context['active_list'] = self.model.objects.filter(operatingday=get_operator_date(), is_recovered=False,
                                                           dataownercode=self.request.user.userprofile.company)
        context['active_list'] = context['active_list'].order_by('line__publiclinenumber', 'line__lineplanningnumber', 'journey__departuretime', 'created')

        # Add the no longer active changes
        context['archive_list'] = self.model.objects.filter(Q(operatingday__lt=get_operator_date()) | Q(is_recovered=True),
                                                            dataownercode=self.request.user.userprofile.company,
                                                            created__gt=get_operator_date()-timedelta(days=3))
        context['archive_list'] = context['archive_list'].order_by('-created')
        return context


class ChangeCreateView(AccessMixin, Kv17PushMixin, CreateView):
    permission_required = 'openebs.add_change'
    model = Kv17Change
    form_class = Kv17ChangeForm
    success_url = reverse_lazy('change_index')

    def get_context_data(self, **kwargs):
        data = super(ChangeCreateView, self).get_context_data(**kwargs)
        data['operator_date'] = get_operator_date()
        if 'journey' in self.request.GET:
            self.add_journeys_from_request(data)
        return data

    def add_journeys_from_request(self, data):
        journey_errors = 0
        journeys = []
        for journey in self.request.GET['journey'].split(','):
            if journey == "":
                continue
            log.info("Finding journey %s for '%s'" % (journey, self.request.user))
            j = Kv1Journey.find_from_realtime(self.request.user.userprofile.company, journey)
            if j:
                journeys.append(j)
            else:
                journey_errors += 1
                log.error("User '%s' (%s) failed to find journey '%s' " % (self.request.user, self.request.user.userprofile.company, journey))
        data['journeys'] = journeys
        if journey_errors > 0:
            data['journey_errors'] = journey_errors

    def form_invalid(self, form):
        log.error("Form for KV17 change invalid!")
        return super(ChangeCreateView, self).form_invalid(form)

    def form_valid(self, form):
        form.instance.dataownercode = self.request.user.userprofile.company

        # TODO this is a bad solution - totally gets rid of any benefit of Django's CBV and Forms
        xml = form.save()

        if len(xml) == 0:
            log.error("Tried to communicate KV17 empty line change, rejecting")
            # This is kinda weird, but shouldn't happen, everything has validation
            return HttpResponseRedirect(self.success_url)

        # Push message to GOVI
        if self.push_message(xml):
            log.info("Sent KV17 line change to subscribers: %s" % self.request.POST.get('journeys', "<unknown>"))
        else:
            log.error("Failed to communicate KV17 line change to subscribers")

        # Another hack to redirect correctly
        return HttpResponseRedirect(self.success_url)


class ChangeDeleteView(AccessMixin, Kv17PushMixin, FilterDataownerMixin, DeleteView):
    permission_required = 'openebs.add_change'
    model = Kv17Change
    success_url = reverse_lazy('change_index')

    def delete(self, request, *args, **kwargs):
        ret = super(ChangeDeleteView, self).delete(request, *args, **kwargs)
        obj = self.get_object()
        if self.push_message(obj.to_xml()):
            log.error("Recovered line succesfully communicated to subscribers: %s" % obj)
        else:
            log.error("Failed to send recover request to subscribers: %s" % obj)
            # We failed to push, recover our delete operation
            obj.is_recovered = False
            obj.recovered = None
            obj.save() # Note, this won't work locally!
        return ret


class ChangeUpdateView(AccessMixin, Kv17PushMixin, FilterDataownerMixin, DeleteView):
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
        self.object = self.get_object()  # Store an original to undo our redo
        obj = self.update_object()
        if self.push_message(obj.to_xml()):
            log.error("Redo line cancel succesfully communicated to subscribers: %s" % obj)
        else:
            log.error("Failed to send redo request to subscribers: %s" % obj)
            # We failed to push, recover our redo operation by restoring previous state
            obj.is_recovered = self.get_object.is_recovered
            obj.recovered = self.get_object.recovered
            obj.save()  # Note, this won't work locally!
        return HttpResponseRedirect(self.get_success_url())

"""
TODO : This is a big red button view allowing you to cancel all active trips if you so wish.
"""
# class CancelLinesView(AccessMixin, Kv17PushMixin, FormView):
#
#     permission_required = 'openebs.add_change'
#     form_class = CancelLinesForm
#     template_name = 'openebs/kv17change_redbutton.html'
#     success_url = reverse_lazy('change_index')
#
#     def get_context_data(self, **kwargs):
#         """ Add data about the trips we'd be cancelling """
#         data = super(CancelLinesView, self).get_context_data(**kwargs)
#         data['trips'] = Kv17Change.objects.filter(dataownercode=self.request.user.userprofile.company)
#         return data
#
#     def form_valid(self, form):
#         ret = super(CancelLinesView, self).form_valid(form)
#         # Find our scenario
#         # Plan messages
#
#         # Concatenate XML for a single request
#         message_string = ""
#         if self.push_message(message_string):
#             log.error("Planned messages sent to subscribers: %s" % "")
#         else:
#             log.error("Failed to communicate planned messages to subscribers: %s")
#         return ret


class ActiveJourneysAjaxView(LoginRequiredMixin, JSONListResponseMixin, DetailView):
    model = Kv17Change
    render_object = 'object'

    def get_object(self):
        # Note, can't set this on the view, because it triggers the queryset cache
        queryset = self.model.objects.filter(operatingday=get_operator_date(),
                                             is_recovered=False, # TODO Fix this - see bug #61
                                             dataownercode=self.request.user.userprofile.company).distinct()
        return list(queryset.values('journey_id', 'dataownercode'))
