# Create your views here.
from datetime import datetime
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from openebs.models import Kv15Stopmessage
from openebs.form import Kv15StopMessageForm

class MessageListView(ListView):
    model = Kv15Stopmessage
    # Get the currently active messages
    context_object_name = 'active_list'
    queryset = model.objects.filter(messagestarttime__lt=datetime.now, messageendtime__gt=datetime.now)

    def get_context_data(self, **kwargs):
        context = super(MessageListView, self).get_context_data(**kwargs)
        # Add the no longer active messages
        context['archive_list'] = self.model.objects.filter(messageendtime__lt=datetime.now)
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
        return super(MessageCreateView, self).form_valid(form)

    # Require logged in
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MessageCreateView, self).dispatch(*args, **kwargs)