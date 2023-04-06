import logging
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.views.generic.edit import BaseFormView
from kv1.models import Kv1Stop, Kv1Line
from openebs.form import Kv15ScenarioMessageForm
from openebs.models import Kv15Scenario, Kv15ScenarioMessage
from openebs.views import AccessMixin
from openebs.views_utils import FilterDataownerMixin
from braces.views import LoginRequiredMixin
from utils.views import JSONListResponseMixin

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
        if self.kwargs.get('scenario', None):  # This ensures the scenario can never be spoofed
            init['scenario'] = self.kwargs.get('scenario', None)
        return init

    def form_valid(self, form):
        if self.request.user:
            form.instance.dataownercode = self.request.user.userprofile.company

        if self.kwargs.get('scenario', None):  # This ensures the scenario can never be spoofed
            # TODO Register difference between this and the scenario we've validated on
            form.instance.scenario = get_object_or_404(Kv15Scenario, pk=self.kwargs.get('scenario', None),
                                                              dataownercode=self.request.user.userprofile.company)

        ret = super(ScenarioMessageCreateView, self).form_valid(form)

        # After saving, set the haltes and save them
        haltes = self.request.POST.get('haltes', None)
        if haltes:
            for stop in Kv1Stop.find_stops_from_haltes(haltes):
                form.instance.stops.create(message=form.instance, stop=stop)
        lines = self.request.POST.get('lines', None)
        lijnen = []
        if lines:
            for line in lines.split(','):
                if len(line) > 0:
                    result = Kv1Line.find_line(form.instance.dataownercode, line)
                    lijnen.append(result)
        for lijn in lijnen:
            form.instance.lines.create(message=form.instance, line=lijn)

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

        lijnen = self.request.POST.get('lines', None)
        self.process_new_old_lines(form.instance, form.instance.lines, lijnen if lijnen else "")
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

    @staticmethod
    def process_new_old_lines(msg, line_set, lines):
        """ Add new lines to the set, and then check if we've deleted any lines from the old list """
        new_lines = []
        old_lines = lines.split(',')
        for line in old_lines:
            if len(line) > 0:
                valid_line = Kv1Line.find_line(msg.dataownercode, line)
                if valid_line:
                    new_lines.append(valid_line)
        for lijn in new_lines:
            # TODO Improve this to not be n-queries
            if line_set.filter(line=lijn).count() == 0: # New line, add it
                line_set.create(message=msg, line=lijn)
        for old_msg_line in line_set.all():
            if old_msg_line.line not in new_lines: # Removed line, delete it
                old_msg_line.delete()


class ScenarioMessageDeleteView(AccessMixin, ScenarioContentMixin, DeleteView):
    permission_required = 'openebs.add_scenario'
    model = Kv15ScenarioMessage


class ScenarioMessageDetailsView(AccessMixin, FilterDataownerMixin, DetailView):
    permission_required = 'openebs.view_messages'
    permission_level = 'read'
    model = Kv15ScenarioMessage


class ScenarioMessageAjaxView(LoginRequiredMixin, JSONListResponseMixin, DetailView):
    model = Kv15ScenarioMessage
    render_object = 'object'

    def get_object(self, **kwargs):
        qry = self.get_queryset()
        return qry

    def get_queryset(self):
        qry = super(ScenarioMessageAjaxView, self).get_queryset()
        qry = qry.filter(id=self.kwargs.get('pk', None))
        dataownercode = qry.values('dataownercode')[0]['dataownercode']
        lines = []
        x = qry.values('lines__line_id')

        for item in qry.values('lines__line_id', 'lines__line_id__lineplanningnumber'):
            if item['lines__line_id'] is None:
                lines.append('None/None')
            else:
                lines.append(str(item['lines__line_id'])+'/'+item['lines__line_id__lineplanningnumber'])
        stops = []
        for item in qry.values('stops__stop_id__userstopcode', 'stops__stop_id__name'):
            stops.append([dataownercode+'_'+item['stops__stop_id__userstopcode'], item['stops__stop_id__name']])

        line_stops = {}
        used_stops = []
        if 'None' in lines[0]:
            line_stops[lines[0]] = stops
        else:
            for line in lines:
                line_id = line.split('/')[0]
                line_stops[line] = []
                query = Kv1Line.objects.filter(id=line_id)
                stop_map = query.values('stop_map')[0]['stop_map']
                for stop in stops:
                    if stop[0] in stop_map:
                        line_stops[line].append(stop)
                        used_stops.append(stop)
            # check if all stops are 'used'
            extra_stops = []
            for stop in stops:
                if stop not in used_stops:
                    extra_stops.append(stop)
            if len(extra_stops) > 0:
                line_stops['x/Onbekend'] = extra_stops
        return line_stops
