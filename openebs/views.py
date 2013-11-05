# Create your views here.
from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Q
from django.conf import settings
from django.views.generic import ListView, UpdateView
from django.views.generic.edit import CreateView, DeleteView, BaseFormView
from django.utils.timezone import now
from kv1.models import Kv1Stop
from utils.client import get_client_ip
from openebs.models import Kv15Stopmessage, Kv15Log, Kv15Scenario, Kv15ScenarioMessage
from openebs.form import Kv15StopMessageForm, Kv15ScenarioForm, Kv15ScenarioMessageForm

import logging
from utils.push import Push

log = logging.getLogger(__name__)

class OpenEbsUserMixin(LoginRequiredMixin, PermissionRequiredMixin):
    raise_exception = True

# MESSAGE VIEWS

class MessageListView(OpenEbsUserMixin, ListView):
    permission_required = 'openebs.view_messages'
    model = Kv15Stopmessage
    # Get the currently active messages
    context_object_name = 'active_list'
    queryset = model.objects.filter(messageendtime__gt=now, isdeleted=False)

    def get_context_data(self, **kwargs):
        context = super(MessageListView, self).get_context_data(**kwargs)
        # Add the no longer active messages
        context['archive_list'] = self.model.objects.filter(Q(messageendtime__lt=now) | Q(isdeleted=True)).order_by('-messagecodedate', '-messagecodenumber')
        return context

class MessageCreateView(OpenEbsUserMixin, CreateView):
    permission_required = 'openebs.add_messages'
    model = Kv15Stopmessage
    form_class = Kv15StopMessageForm
    success_url = reverse_lazy('msg_index')

    def form_valid(self, form):
        if self.request.user:
            form.instance.user = self.request.user
            form.instance.dataownercode = self.request.user.userprofile.company

        haltes = self.request.POST.get('haltes', None)
        stops = []
        if haltes:
            stops = Kv1Stop.find_stops_from_haltes(haltes)

        # TODO Push to GOVI (see if we can without saving)
        msg = form.instance.to_xml_with_stops(stops)
        code, content = Push(settings.GOVI_SUBSCRIBER, settings.GOVI_DOSSIER, msg, settings.GOVI_NAMESPACE).push(settings.GOVI_HOST, settings.GOVI_PATH)

        # Save and then log
        ret = super(MessageCreateView, self).form_valid(form)
        Kv15Log.create_log_entry(form.instance, get_client_ip(self.request))

        for stop in stops:
            form.instance.kv15messagestop_set.create(stopmessage=form.instance, stop=stop)

        return ret

class MessageUpdateView(OpenEbsUserMixin, UpdateView):
    permission_required = 'openebs.add_messages'
    model = Kv15Stopmessage
    form_class = Kv15StopMessageForm
    template_name_suffix = '_update'
    success_url = reverse_lazy('msg_index')

    def form_valid(self, form):
        # Save and then log
        ret = super(MessageUpdateView, self).form_valid(form)
        # TODO figure out edit logs
        # Kv15Log.create_log_entry(form.instance, get_client_ip(self.request))

        # Get our new stops, and always determine if we need to get rid of any!
        haltes = self.request.POST.get('haltes', None)
        self.process_new_old_haltes(form.instance, form.instance.kv15messagestop_set, haltes if haltes else "")

        # TODO Push to GOVI
        # Push a delete, then a create, but we can use the same message id

        return ret

    def process_new_old_haltes(self, msg, set, haltes):
        """ Add new stops to the set, and then check if we've deleted any stops from the old list """
        new_stops = Kv1Stop.find_stops_from_haltes(haltes)
        for stop in new_stops:
            # TODO Improve this to not be n-queries
            if set.filter(stop=stop).count() == 0: # New stop, add it
                set.create(stopmessage=msg, stop=stop)
        for old_msg_stop in set.all():
            if old_msg_stop.stop not in new_stops: # Removed stop, delete it
                old_msg_stop.delete()


class MessageDeleteView(OpenEbsUserMixin, DeleteView):
    permission_required = 'openebs.add_messages'
    model = Kv15Stopmessage
    success_url = reverse_lazy('msg_index')


# SCENARIO VIEWS

class ScenarioListView(OpenEbsUserMixin, ListView):
    permission_required = 'openebs.view_scenario'
    model = Kv15Scenario

class ScenarioCreateView(OpenEbsUserMixin, CreateView):
    permission_required = 'openebs.add_scenario'
    model = Kv15Scenario
    form_class = Kv15ScenarioForm

    def get_success_url(self):
        return reverse_lazy('scenario_edit', args=[self.object.id])

class ScenarioUpdateView(OpenEbsUserMixin, UpdateView):
    permission_required = 'openebs.add_scenario'
    model = Kv15Scenario
    form_class = Kv15ScenarioForm
    template_name_suffix = '_update'
    success_url = reverse_lazy('scenario_index')

class ScenarioDeleteView(OpenEbsUserMixin, DeleteView):
    permission_required = 'openebs.add_scenario'
    model = Kv15Scenario
    success_url = reverse_lazy('scenario_index')

# SCENARIO MESSAGE VIEWS

class ScenarioMessageContentMixin(BaseFormView):
    """  Overide a few defaults used by scenario messages  """
    def get_context_data(self, **kwargs):
        """ Add data about the scenario we're adding to """
        data = super(ScenarioMessageContentMixin, self).get_context_data(**kwargs)
        if self.kwargs.get('scenario', None):
            data['scenario'] = Kv15Scenario.objects.get(pk=self.kwargs.get('scenario', None))
        return data

    def get_success_url(self):
        if self.kwargs.get('scenario', None):
            return reverse_lazy('scenario_edit', args=[self.kwargs.get('scenario')])
        else:
            return reverse_lazy('scenario_index')

class ScenarioMessageCreateView(OpenEbsUserMixin, ScenarioMessageContentMixin, CreateView):
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

        if self.kwargs.get('scenario', None): # This ensures the scenario can never be spoofed
            # TODO Register difference between this and the scenario we've validated on
            form.instance.scenario = Kv15Scenario.objects.get(pk=self.kwargs.get('scenario', None))

        ret = super(CreateView, self).form_valid(form)

        # After saving, set the haltes and save them
        haltes = self.request.POST.get('haltes', None)
        if haltes:
            for stop in Kv1Stop.find_stops_from_haltes(haltes):
                form.instance.kv15scenariostop_set.create(message=form.instance, stop=stop)

        return ret


class ScenarioMessageUpdateView(OpenEbsUserMixin, ScenarioMessageContentMixin, UpdateView):
    permission_required = 'openebs.add_scenario'
    model = Kv15ScenarioMessage
    form_class = Kv15ScenarioMessageForm
    template_name_suffix = '_update'

    def form_valid(self, form):
        ret = super(ScenarioMessageUpdateView, self).form_valid(form)

        haltes = self.request.POST.get('haltes', None)
        self.process_new_old_haltes(form.instance, form.instance.kv15scenariostop_set, haltes if haltes else "")

        return ret

    def process_new_old_haltes(self, msg, set, haltes):
        """ Add new stops to the set, and then check if we've deleted any stops from the old list """
        new_stops = Kv1Stop.find_stops_from_haltes(haltes)
        for stop in new_stops:
            # TODO Improve this to not be n-queries
            if set.filter(stop=stop).count() == 0: # New stop, add it
                set.create(message=msg, stop=stop)
        for old_msg_stop in set.all():
            if old_msg_stop.stop not in new_stops: # Removed stop, delete it
                old_msg_stop.delete()

class ScenarioMessageDeleteView(OpenEbsUserMixin, ScenarioMessageContentMixin, DeleteView):
    permission_required = 'openebs.add_scenario'
    model = Kv15ScenarioMessage