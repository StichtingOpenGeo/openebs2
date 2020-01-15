import logging
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.edit import BaseFormView
from kv1.models import Kv1Stop
from openebs.form import Kv15ScenarioMessageForm
from openebs.models import Kv15Scenario, Kv15ScenarioMessage
from openebs.views import AccessMixin
from openebs.views_utils import FilterDataownerMixin

log = logging.getLogger('openebs.views.scenario_message')


class ScenarioContentMixin(BaseFormView):
    """  Overide a few defaults used by scenario messages  """
    def get_context_data(self, **kwargs):
        """ Add data about the scenario we're adding to """
        data = super(ScenarioContentMixin, self).get_context_data(**kwargs)
        if self.kwargs.get('scenario', None):
            data['scenario'] = get_object_or_404(Kv15Scenario, pk=self.kwargs.get('scenario', None),
                                                        dataownercode=self.request.user.userprofile.company)
        return data

    def get_success_url(self):
        if self.kwargs.get('scenario', None):
            return reverse_lazy('scenario_edit', args=[self.kwargs.get('scenario')])
        else:
            return reverse_lazy('scenario_index')


class ScenarioMessageCreateView(AccessMixin, ScenarioContentMixin, CreateView):
    permission_required = 'openebs.add_scenario'
    model = Kv15ScenarioMessage
    form_class = Kv15ScenarioMessageForm

    def get_initial(self):
        init = super(ScenarioMessageCreateView, self).get_initial()
        if self.kwargs.get('scenario', None): # This ensures the scenario can never be spoofed
            init['scenario'] = self.kwargs.get('scenario', None)
        return init

    def form_valid(self, form):
        if self.request.user:
            form.instance.dataownercode = self.request.user.userprofile.company

        if self.kwargs.get('scenario', None):  # This ensures the scenario can never be spoofed
            # TODO Register difference between this and the scenario we've validated on
            form.instance.scenario = get_object_or_404(Kv15Scenario, pk=self.kwargs.get('scenario', None),
                                                              dataownercode=self.request.user.userprofile.company)

        ret = super(CreateView, self).form_valid(form)

        # After saving, set the haltes and save them
        haltes = self.request.POST.get('haltes', None)
        if haltes:
            for stop in Kv1Stop.find_stops_from_haltes(haltes):
                form.instance.stops.create(message=form.instance, stop=stop)

        return ret


class ScenarioMessageUpdateView(AccessMixin, FilterDataownerMixin, ScenarioContentMixin, UpdateView):
    permission_required = 'openebs.add_scenario'
    model = Kv15ScenarioMessage
    form_class = Kv15ScenarioMessageForm
    template_name_suffix = '_update'

    def form_valid(self, form):
        ret = super(ScenarioMessageUpdateView, self).form_valid(form)

        haltes = self.request.POST.get('haltes', None)
        self.process_new_old_haltes(form.instance, form.instance.stops, haltes if haltes else "")

        return ret

    @staticmethod
    def process_new_old_haltes(msg, stop_set, haltes):
        """ Add new stops to the set, and then check if we've deleted any stops from the old list """
        new_stops = Kv1Stop.find_stops_from_haltes(haltes)
        for stop in new_stops:
            # TODO Improve this to not be n-queries
            if stop_set.filter(stop=stop).count() == 0:  # New stop, add it
                stop_set.create(message=msg, stop=stop)
        for old_msg_stop in stop_set.all():
            if old_msg_stop.stop not in new_stops:  # Removed stop, delete it
                old_msg_stop.delete()


class ScenarioMessageDeleteView(AccessMixin, ScenarioContentMixin, DeleteView):
    permission_required = 'openebs.add_scenario'
    model = Kv15ScenarioMessage
