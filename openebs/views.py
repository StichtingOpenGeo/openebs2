# Create your views here.
import logging
from braces.views import LoginRequiredMixin
from datetime import timedelta
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.views.generic import ListView, UpdateView, DetailView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView, DeleteView
from django.utils.timezone import now
from django.views.generic.list import MultipleObjectMixin
from djgeojson.views import GeoJSONLayerView
from kv1.models import Kv1Stop
from utils.client import get_client_ip
from utils.views import ExternalMessagePushMixin, JSONListResponseMixin, AccessMixin
from openebs.models import Kv15Stopmessage, Kv15Log, MessageStatus
from openebs.form import Kv15StopMessageForm

log = logging.getLogger('openebs.views')

class FilterDataownerMixin(SingleObjectMixin):

    def get_queryset(self):
        company = self.request.user.userprofile.company
        if company is None:
            raise PermissionDenied("Je account is nog niet gelinkt aan een vervoerder")
        return super(FilterDataownerMixin, self).get_queryset().filter(dataownercode=company)

class FilterDataownerListMixin(MultipleObjectMixin):

    def get_queryset(self):
        company = self.request.user.userprofile.company
        if company is None:
            raise PermissionDenied("Je account is nog niet gelinkt aan een vervoerder")
        return super(FilterDataownerListMixin, self).get_queryset().filter(dataownercode=company)

class Kv15PushMixin(ExternalMessagePushMixin):
    message_type = 'KV15'
    dossier = 'KV15messages'
    namespace = 'http://bison.connekt.nl/tmi8/kv15/msg'

# MESSAGE VIEWS

class MessageListView(AccessMixin, ListView):
    permission_required = 'openebs.view_messages'
    model = Kv15Stopmessage

    def get_context_data(self, **kwargs):
        context = super(MessageListView, self).get_context_data(**kwargs)

        # Get the currently active messages
        context['active_list'] = self.model.objects.filter(messageendtime__gt=now, isdeleted=False,
                                                           dataownercode=self.request.user.userprofile.company)
        context['active_list'] = context['active_list'].order_by('-messagecodedate', '-messagecodenumber')

        # Add the no longer active messages
        context['archive_list'] = self.model.objects.filter(Q(messageendtime__lt=now) | Q(isdeleted=True),
                                                            dataownercode=self.request.user.userprofile.company,
                                                            messagestarttime__gt=now()-timedelta(days=3))
        context['archive_list'] = context['archive_list'].order_by('-messagecodedate', '-messagecodenumber')
        return context


class MessageCreateView(AccessMixin, Kv15PushMixin, CreateView):
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

        # Save and then log
        ret = super(MessageCreateView, self).form_valid(form)

        # Add stop data
        for stop in stops:
            form.instance.kv15messagestop_set.create(stopmessage=form.instance, stop=stop)
        Kv15Log.create_log_entry(form.instance, get_client_ip(self.request))

        # Send to GOVI
        if self.push_message(form.instance.to_xml()):
            form.instance.set_status(MessageStatus.SENT)
            log.info("Sent message to subscribers: %s" % (form.instance))
        else:
            form.instance.set_status(MessageStatus.ERROR_SEND)
            log.error("Failed to send message to subscribers: %s" % (form.instance))

        return ret


class MessageUpdateView(AccessMixin, Kv15PushMixin, FilterDataownerMixin, UpdateView):
    permission_required = 'openebs.add_messages'
    model = Kv15Stopmessage
    form_class = Kv15StopMessageForm
    template_name_suffix = '_update'
    success_url = reverse_lazy('msg_index')

    def form_valid(self, form):
        if self.request.user:
            form.instance.user = self.request.user

        # Save and then log
        ret = super(MessageUpdateView, self).form_valid(form)
        # TODO figure out edit logs
        # Kv15Log.create_log_entry(form.instance, get_client_ip(self.request))

        # Get our new stops, and always determine if we need to get rid of any!
        haltes = self.request.POST.get('haltes', None)
        self.process_new_old_haltes(form.instance, form.instance.kv15messagestop_set, haltes if haltes else "")

        # Push a delete, then a create, but we can use the same message id
        if self.push_message(form.instance.to_xml_delete()+form.instance.to_xml()):
            form.instance.set_status(MessageStatus.SENT)
            log.info("Sent message to subscribers: %s" % (form.instance))
        else:
            form.instance.set_status(MessageStatus.ERROR_SEND)
            log.error("Failed to send updated message to subscribers: %s" % (form.instance))

        return ret

    @staticmethod
    def process_new_old_haltes(msg, stop_set, haltes):
        """ Add new stops to the set, and then check if we've deleted any stops from the old list """
        new_stops = Kv1Stop.find_stops_from_haltes(haltes)
        for stop in new_stops:
            # TODO Improve this to not be n-queries
            if stop_set.filter(stop=stop).count() == 0: # New stop, add it
                stop_set.create(stopmessage=msg, stop=stop)
        for old_msg_stop in stop_set.all():
            if old_msg_stop.stop not in new_stops: # Removed stop, delete it
                old_msg_stop.delete()


class MessageDeleteView(AccessMixin, Kv15PushMixin, FilterDataownerMixin, DeleteView):
    permission_required = 'openebs.add_messages'
    model = Kv15Stopmessage
    success_url = reverse_lazy('msg_index')

    def delete(self, request, *args, **kwargs):
        # Ensure we update the user
        msg = self.get_object()
        msg.user = request.user
        msg.save()

        ret = super(MessageDeleteView, self).delete(request, *args, **kwargs)
        msg = self.get_object()
        if self.push_message(msg.to_xml_delete()):
            msg.set_status(MessageStatus.DELETED)
            log.error("Deleted message succesfully communicated to subscribers: %s" % msg)
        else:
            msg.set_status(MessageStatus.ERROR_SEND_DELETE)
            log.error("Failed to send delete request to subscribers: %s" % msg)
        return ret

class MessageDetailsView(AccessMixin, FilterDataownerMixin, DetailView):
    permission_required = 'openebs.view_messages'
    model = Kv15Stopmessage

# AJAX Views
class ActiveStopsAjaxView(LoginRequiredMixin, JSONListResponseMixin, DetailView):
    model = Kv1Stop
    render_object = 'object'

    def get_object(self):
        # Note, can't set this on the view, because it triggers the queryset cache
        queryset = self.model.objects.filter(messages__stopmessage__messagestarttime__lte=now(),
                                             messages__stopmessage__messageendtime__gte=now(),
                                             messages__stopmessage__isdeleted=False,
                                             # These two are double, but just in case
                                             messages__stopmessage__dataownercode=self.request.user.userprofile.company,
                                             dataownercode=self.request.user.userprofile.company).distinct()
        print queryset.count()
        return list(queryset.values('dataownercode', 'userstopcode'))

class MessageStopsAjaxView(LoginRequiredMixin, GeoJSONLayerView):
    model = Kv1Stop
    geometry_field = 'location'
    properties = ['name', 'userstopcode', 'dataownercode']

    def get_queryset(self):
        qry = super(MessageStopsAjaxView, self).get_queryset()
        qry = qry.filter(kv15stopmessage__id=self.kwargs.get('pk', None),
                         kv15stopmessage__dataownercode=self.request.user.userprofile.company)
        return qry
