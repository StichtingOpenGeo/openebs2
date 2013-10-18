# Create your views here.
from datetime import datetime
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse_lazy
from openebs.models import Kv15Stopmessage
from openebs.form import Kv15StopMessageForm

class MessageListView(ListView):
    model = Kv15Stopmessage
    # Get the currently active messages
    context_object_name = 'current_list'
    queryset = model.objects.filter(messageendtime__gt=datetime.now)

    def get_context_data(self, **kwargs):
        context = super(MessageListView, self).get_context_data(**kwargs)
        # Add the no longer active messages
        context['archive_list'] = self.model.objects.all()
        return context

class MessageCreateView(CreateView):
    model = Kv15Stopmessage
    form_class = Kv15StopMessageForm
    success_url = reverse_lazy('msg_index')