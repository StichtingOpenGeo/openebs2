from builtins import str
import logging
from django.urls import reverse_lazy
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import FormView, ListView, CreateView, UpdateView, DeleteView, DetailView
from djgeojson.views import GeoJSONLayerView
from kv1.models import Kv1Stop
from openebs.form import PlanScenarioForm, Kv15ScenarioForm
from openebs.models import Kv15Scenario, MessageStatus, Kv15ScenarioMessage, Kv15ScenarioStop
from openebs.views_push import Kv15PushMixin
from openebs.views_utils import FilterDataownerMixin, FilterDataownerListMixin
from utils.views import AccessMixin, AccessJsonMixin, JSONListResponseMixin

log = logging.getLogger('openebs.views.scenario')


# SCENARIO VIEWS
class PlanScenarioView(AccessMixin, Kv15PushMixin, FormView):
    permission_required = 'openebs.view_scenario'  # TODO Also add message!
    form_class = PlanScenarioForm
    template_name = 'openebs/kv15scenario_plan.html'
    success_url = reverse_lazy('msg_index')

    def get_context_data(self, **kwargs):
        """ Add data about the scenario we're adding to """
        data = super(PlanScenarioView, self).get_context_data(**kwargs)
        if self.kwargs.get('scenario', None):
            data['scenario'] = get_object_or_404(Kv15Scenario,
                                                 pk=self.kwargs.get('scenario', None),
                                                 dataownercode=self.request.user.userprofile.company)
        return data

    def form_valid(self, form):
        ret = super(PlanScenarioView, self).form_valid(form)
        if self.kwargs.get('scenario', None):
            # Find our scenario
            scenario = get_object_or_404(Kv15Scenario, pk=self.kwargs.get('scenario', None),
                                         dataownercode=self.request.user.userprofile.company)
            # Plan messages
            saved = scenario.plan_messages(self.request.user, form.cleaned_data['messagestarttime'],
                                           form.cleaned_data['messageendtime'])
            # Concatenate XML for a single request
            message_string = "".join([msg.to_xml() for msg in saved])
            if self.push_message(message_string):
                for msg in saved:
                    msg.set_status(MessageStatus.SENT)
                log.error("Planned messages sent to subscribers: %s" % ",".join([str(msg.messagecodenumber) for msg in saved]))
            else:
                for msg in saved:
                    msg.set_status(MessageStatus.ERROR_SEND)
                ids = ",".join([str(msg.messagecodenumber) for msg in saved])
                log.error("Failed to communicate planned messages to subscribers: %s" % ids)
        return ret


class ScenarioListView(AccessMixin, FilterDataownerListMixin, ListView):
    permission_required = 'openebs.view_scenario'
    model = Kv15Scenario

    def get_queryset(self):
        return super(ScenarioListView, self).get_queryset().order_by('name').annotate(Count('messages'))


class ScenarioCreateView(AccessMixin, CreateView):
    permission_required = 'openebs.add_scenario'
    model = Kv15Scenario
    form_class = Kv15ScenarioForm

    def form_valid(self, form):
        if self.request.user:  # TODO Improve this construct
            form.instance.dataownercode = self.request.user.userprofile.company

        return super(ScenarioCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('scenario_edit', args=[self.object.id])


class ScenarioUpdateView(AccessMixin, FilterDataownerMixin, UpdateView):
    permission_required = 'openebs.add_scenario'
    model = Kv15Scenario
    form_class = Kv15ScenarioForm
    template_name_suffix = '_update'
    success_url = reverse_lazy('scenario_index')

    def get_queryset(self):
        return super(ScenarioUpdateView, self).get_queryset().prefetch_related('messages', 'messages__stops', 'messages__stops__stop')


class ScenarioDeleteView(AccessMixin, FilterDataownerMixin, DeleteView):
    permission_required = 'openebs.add_scenario'
    model = Kv15Scenario
    success_url = reverse_lazy('scenario_index')


class ScenarioStopsAjaxView(AccessJsonMixin, GeoJSONLayerView):
    permission_required = 'openebs.view_scenario'
    model = Kv1Stop
    geometry_field = 'location'
    properties = ['name', 'userstopcode', 'dataownercode', 'messages']

    def get_queryset(self):
        qry = super(ScenarioStopsAjaxView, self).get_queryset()
        qry = qry.filter(kv15scenariostop__message__scenario=self.kwargs.get('scenario', None),
                         kv15scenariostop__message__scenario__dataownercode=self.request.user.userprofile.company)
        return qry


class ScenarioMessageAjaxView(AccessJsonMixin, JSONListResponseMixin, DetailView):
    permission_required = 'openebs.view_scenario'
    model = Kv15ScenarioMessage
    render_object = 'object'

    def get_object(self):
        queryset = self.model.objects.filter(scenario=self.kwargs.get('scenario', None),
                                             dataownercode=self.request.user.userprofile.company).distinct()
        return list(queryset.values('id', 'messagedurationtype'))


class ScenarioCloneView(AccessMixin, FilterDataownerMixin, View):
    permission_required = 'openebs.add_scenario'
    model = Kv15Scenario
    form_class = Kv15ScenarioForm

    def get(self, request, pk):
        duplicate = Kv15Scenario.objects.filter(id=pk)[0]
        duplicate.id = None
        duplicate.name += ' - KOPIE'
        duplicate.save()
        # find related messages
        scenario_details = Kv15ScenarioMessage.objects.filter(scenario_id=pk)
        for related_message in scenario_details:
            # find related stops for the message and duplicate these first while a message_id is still known
            message_id = related_message.id
            related_message.pk = None
            related_message.scenario = duplicate
            related_message.save()
            stop_details = Kv15ScenarioStop.objects.filter(message_id=message_id)
            for related_stop in stop_details:
                related_stop.pk = None
                related_stop.message = related_message
                related_stop.save()

        return redirect("scenario_edit", pk=duplicate.pk)
