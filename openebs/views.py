# Create your views here.
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.utils.decorators import method_decorator
from kv1.models import Kv1Stop
from utils.client import get_client_ip
from openebs.models import Kv15Stopmessage, Kv15Log, Kv15Scenario, Kv15MessageStop, Kv15ScenarioMessage
from openebs.form import Kv15StopMessageForm, Kv15ScenarioForm, Kv15ScenarioMessageForm


class MessageListView(ListView):
    model = Kv15Stopmessage
    # Get the currently active messages
    context_object_name = 'active_list'
    queryset = model.objects.filter(messageendtime__gt=now, isdeleted=False)

    def get_context_data(self, **kwargs):
        context = super(MessageListView, self).get_context_data(**kwargs)
        # Add the no longer active messages
        context['archive_list'] = self.model.objects.filter(Q(messageendtime__lt=now) | Q(isdeleted=True)).order_by('-messagecodedate', '-messagecodenumber')
        return context

    # Require logged in
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MessageListView, self).dispatch(*args, **kwargs)

class MessageCreateView(CreateView):
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
                    else:
                        print "Couldn't find %s" % halte_split

    # Require logged in
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MessageCreateView, self).dispatch(*args, **kwargs)

class MessageDeleteView(DeleteView):
    model = Kv15Stopmessage
    success_url = reverse_lazy('msg_index')

    # Require logged in
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MessageDeleteView, self).dispatch(*args, **kwargs)


class ScenarioListView(ListView):
    model = Kv15Scenario

    # Require logged in
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ScenarioListView, self).dispatch(*args, **kwargs)

class ScenarioCreateView(CreateView):
    model = Kv15Scenario
    form_class = Kv15ScenarioForm
    success_url = reverse_lazy('scenario_index')

class ScenarioCreateMessageView(MessageCreateView):
    model = Kv15ScenarioMessage
    form_class = Kv15ScenarioMessageForm
    success_url = reverse_lazy('scenario_index')