# Create your views here.
from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.views.generic import ListView, UpdateView
from django.views.generic.edit import CreateView, DeleteView
from django.utils.timezone import now
from kv1.models import Kv1Stop
from utils.client import get_client_ip
from openebs.models import Kv15Stopmessage, Kv15Log, Kv15Scenario, Kv15ScenarioMessage
from openebs.form import Kv15StopMessageForm, Kv15ScenarioForm, Kv15ScenarioMessageForm

class OpenEbsUserMixin(LoginRequiredMixin, PermissionRequiredMixin):
    raise_exception = True

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

        # Save and then log
        ret = super(MessageCreateView, self).form_valid(form)
        Kv15Log.create_log_entry(form.instance, get_client_ip(self.request))

        haltes = self.request.POST.get('haltes', None)
        if haltes:
            self.handle_haltes(form.instance, haltes)

        # TODO Push to GOVI

        return ret

    def handle_haltes(self, msg, haltes):
        for halte in haltes.split(','):
            halte_split = halte.split('_')
            if len(halte_split) == 2:
                stop = Kv1Stop.find_stop(halte_split[0], halte_split[1])
                if stop:
                    msg.kv15messagestop_set.create(stopmessage=msg, stop=stop)

class MessageUpdateView(OpenEbsUserMixin, UpdateView):
    permission_required = 'openebs.add_messages'
    model = Kv15Stopmessage
    form_class = Kv15StopMessageForm
    template_name_suffix = '_update'
    success_url = reverse_lazy('msg_index')

class MessageDeleteView(OpenEbsUserMixin, DeleteView):
    permission_required = 'openebs.add_messages'
    model = Kv15Stopmessage
    success_url = reverse_lazy('msg_index')

class ScenarioListView(OpenEbsUserMixin, ListView):
    permission_required = 'openebs.view_scenario'
    model = Kv15Scenario

class ScenarioCreateView(OpenEbsUserMixin, CreateView):
    permission_required = 'openebs.add_scenario'
    model = Kv15Scenario
    form_class = Kv15ScenarioForm
    success_url = reverse_lazy('scenario_index')

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

class ScenarioMessageCreateView(OpenEbsUserMixin, CreateView):
    permission_required = 'openebs.add_scenario'
    model = Kv15ScenarioMessage
    form_class = Kv15ScenarioMessageForm
    success_url = reverse_lazy('scenario_index')

    def get_context_data(self, **kwargs):
        """ Add data about the scenario we're adding to """
        data = super(ScenarioMessageCreateView, self).get_context_data(**kwargs)
        if self.kwargs.get('pk', None):
            data['scenario'] = Kv15Scenario.objects.get(pk=self.kwargs.get('pk', None))
        return data

    def form_valid(self, form):
        if self.request.user:
            form.instance.dataownercode = self.request.user.userprofile.company

        if self.kwargs.get('pk', None): # This ensures the scenario can never be spoofed
            form.instance.scenario = Kv15Scenario.objects.get(pk=self.kwargs.get('pk', None))

        ret = super(CreateView, self).form_valid(form)

        # After saving, set the haltes and save them
        haltes = self.request.POST.get('haltes', None)
        if haltes:
            self.handle_haltes(form.instance, haltes)

        return ret

    def handle_haltes(self, msg, haltes):
        for halte in haltes.split(','):
                halte_split = halte.split('_')
                if len(halte_split) == 2:
                    stop = Kv1Stop.find_stop(halte_split[0], halte_split[1])
                    if stop:
                        msg.kv15scenariostop_set.create(message=msg, stop=stop)

class ScenarioMessageDeleteView(OpenEbsUserMixin, DeleteView):
    permission_required = 'openebs.add_scenario'
    model = Kv15ScenarioMessage
    success_url = reverse_lazy('scenario_index')