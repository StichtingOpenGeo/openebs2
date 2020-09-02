# Create your views here.
import logging
from datetime import timedelta, datetime

from braces.views import LoginRequiredMixin
from django.contrib.gis.db.models import Extent
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.shortcuts import redirect
from django.views.generic import ListView, UpdateView, DetailView
from django.views.generic.edit import CreateView, DeleteView
from django.utils.timezone import now

from djgeojson.views import GeoJSONLayerView

from kv1.models import Kv1Stop, Kv1Line
from openebs.views_push import Kv15PushMixin
from openebs.views_utils import FilterDataownerMixin
from utils.client import get_client_ip
from utils.views import JSONListResponseMixin, AccessMixin
from openebs.models import Kv15Stopmessage, Kv15Log, MessageStatus, Kv1StopFilter, Kv15MessageStop, Kv15MessageLine, get_start_service, get_end_service
from openebs.form import Kv15StopMessageForm
from dateutil import parser


log = logging.getLogger('openebs.views')


# MESSAGE VIEWS
class MessageListView(AccessMixin, ListView):
    permission_required = 'openebs.view_messages'
    model = Kv15Stopmessage

    def get_context_data(self, **kwargs):
        # context = super(MessageListView, self).get_context_data(**kwargs)
        context = {'view_all': self.is_view_all(),
                   'edit_all': self.is_view_all() and self.request.user.has_perm("openebs.edit_all"),
                   'filters': Kv1StopFilter.get_filters(),
                   'filter': int(self.request.GET.get('filter', -1))}

        # Setup filter
        if context['filter'] != -1:
            stop_list = Kv1StopFilter.objects.get(id=context['filter']).stops.values_list('stop')

        # Get the currently active messages
        active = self.model.objects.filter(messageendtime__gt=now(), isdeleted=False) \
                                    .annotate(Count('stops'))\
                                    .order_by('-messagetimestamp')
        if context['filter'] != -1:
            active = active.filter(kv15messagestop__stop__in=stop_list)

        if not context['view_all']:
            active = active.filter(dataownercode=self.request.user.userprofile.company)
        context['active_list'] = active

        # Add the no longer active messages
        archive = self.model.objects.filter(Q(messageendtime__lt=now()) | Q(isdeleted=True),
                                            messagestarttime__gt=(now() - timedelta(days=3))) \
                                    .annotate(Count('stops'))\
                                    .order_by('-messagetimestamp')

        if context['filter'] != -1:
            archive = archive.filter(kv15messagestop__stop__in=stop_list)

        if not context['view_all']:
            archive = archive.filter(dataownercode=self.request.user.userprofile.company)
        context['archive_list'] = archive

        return context

    def is_view_all(self):
        has_query_all = "all" in self.request.GET and self.request.GET['all'] == "true"
        user = self.request.user
        return (user.is_superuser and has_query_all) or \
               (not user.is_superuser and (user.has_perm("openebs.view_all") or user.has_perm("openebs.edit_all")))


class MessageCreateView(AccessMixin, Kv15PushMixin, CreateView):
    permission_required = 'openebs.add_messages'
    model = Kv15Stopmessage
    form_class = Kv15StopMessageForm
    success_url = reverse_lazy('msg_index')

    def get_context_data(self, **kwargs):
        context = super(MessageCreateView, self).get_context_data(**kwargs)
        prefilled_id = self.request.GET.get('id', None)
        if prefilled_id and prefilled_id.isdigit():
            try:
                stop = Kv1Stop.objects.get(id=prefilled_id)
                if not self.request.user.has_perm("openebs.edit_all") and stop.dataownercode != self.request.user.userprofile.company:
                    stop = None
                context['prefilled_stop'] = stop
            except Kv1Stop.DoesNotExist:
                pass
        return context

    def form_valid(self, form):
        if self.request.user:
            form.instance.user = self.request.user
            form.instance.dataownercode = self.request.user.userprofile.company

        haltes = self.request.POST.get('haltes', None)
        stops = []
        if haltes:
            stops = Kv1Stop.find_stops_from_haltes(haltes)

        lines = self.request.POST.get('lines', None)
        lijnen = []
        if lines:
            for line in lines.split(','):
                if len(line) > 0:
                    result = Kv1Line.find_line(form.instance.dataownercode, line)
                    lijnen.append(result)

        # Save and then log
        ret = super(MessageCreateView, self).form_valid(form)

        # Add stop data
        for stop in stops:
            form.instance.kv15messagestop_set.create(stopmessage=form.instance, stop=stop)

        for lijn in lijnen:
            form.instance.kv15messageline_set.create(stopmessage=form.instance, line=lijn)

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
    permission_level = 'write'
    model = Kv15Stopmessage
    form_class = Kv15StopMessageForm
    template_name_suffix = '_update'
    success_url = reverse_lazy('msg_index')

    def form_valid(self, form):
        if self.request.user:
            form.instance.user = self.request.user

        # Save and then log -'dataownercode', 'messagecodedate', 'messagecodenumber',
        original_message = (form.instance.dataownercode, form.instance.messagecodedate, form.instance.messagecodenumber)
        ret = super(MessageUpdateView, self).form_valid(form)
        # TODO figure out edit logs
        # Kv15Log.create_log_entry(form.instance, get_client_ip(self.request))

        # Get our new stops, and always determine if we need to get rid of any!
        haltes = self.request.POST.get('haltes', None)
        self.process_new_old_haltes(form.instance, form.instance.kv15messagestop_set, haltes if haltes else "")

        # Push a delete, then a create, but the previous one has a different message id
        if self.push_message(form.instance.to_xml_delete(original_message[2])+form.instance.to_xml()):
            form.instance.set_status(MessageStatus.SENT)
            # The original instance needs to be marked deleted
            # TODO: write a test for this
            self.model.objects.get(dataownercode=original_message[0], messagecodedate=original_message[1], messagecodenumber=original_message[2])\
                .set_status(MessageStatus.DELETED)
            log.info("Sent updated message to subscribers: %s" % (form.instance))
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


class MessageResendView(AccessMixin, Kv15PushMixin, FilterDataownerMixin, DetailView):
    #http_method_names = ['POST']
    permission_required = 'openebs.add_messages'
    permission_level = 'write'
    model = Kv15Stopmessage
    template_name_suffix = '_resend'
    success_url = reverse_lazy('msg_index')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        log.info("Resent message to subscribers: %s" % (self.object))
        if MessageStatus.is_deleted(self.object.status):
            self.push_message(self.object.to_xml_delete())
        else:
            self.push_message(self.object.to_xml())
        return redirect(self.success_url)


class MessageDeleteView(AccessMixin, Kv15PushMixin, FilterDataownerMixin, DeleteView):
    permission_required = 'openebs.add_messages'
    permission_level = 'write'
    model = Kv15Stopmessage
    success_url = reverse_lazy('msg_index')

    def delete(self, request, *args, **kwargs):
        # Ensure we update the user
        msg = self.get_object()
        msg.user = request.user
        msg.save(significant=False)

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
    permission_level = 'read'
    model = Kv15Stopmessage


# AJAX Views
class ActiveStopsAjaxView(LoginRequiredMixin, JSONListResponseMixin, DetailView):
    model = Kv1Stop
    render_object = 'object'

    def get_object(self, **kwargs):
        # Note, can't set this on the view, because it triggers the queryset cache
        messagestarttime = parser.parse(self.request.GET['messagestarttime']) if 'messagestarttime' in self.request.GET else now()
        queryset = self.model.objects.filter(messages__stopmessage__messagestarttime__lte=messagestarttime,
                                             messages__stopmessage__messageendtime__gt=messagestarttime,
                                             messages__stopmessage__isdeleted=False,
                                             # These two are double, but just in case
                                             messages__stopmessage__dataownercode=self.request.user.userprofile.company,
                                             dataownercode=self.request.user.userprofile.company).distinct()
        return list({'dataownercode': x['dataownercode'],
                     'userstopcode': x['userstopcode'],
                     'line': x['messages__stopmessage__kv15messageline__line'],
                     'starttime': int(x['messages__stopmessage__messagestarttime'].timestamp()),
                     'endtime': int(x['messages__stopmessage__messageendtime'].timestamp()),
                     'message': x['messages__stopmessage__messagecontent']} for x in
                    queryset.values('dataownercode', 'userstopcode', 'messages__stopmessage__kv15messageline__line',
                                    'messages__stopmessage__messagestarttime', 'messages__stopmessage__messageendtime', 'messages__stopmessage__messagecontent'))


class MessageStopsAjaxView(LoginRequiredMixin, GeoJSONLayerView):
    model = Kv1Stop
    geometry_field = 'location'
    properties = ['name', 'userstopcode', 'dataownercode']

    def get_queryset(self):
        qry = super(MessageStopsAjaxView, self).get_queryset()
        qry = qry.filter(kv15stopmessage__id=self.kwargs.get('pk', None))

        if not (self.request.user.has_perm("openebs.view_all") or self.request.user.has_perm("openebs.edit_all")):
            qry = qry.filter(kv15stopmessage__dataownercode=self.request.user.userprofile.company)

        return qry


class MessageStopsBoundAjaxView(LoginRequiredMixin, JSONListResponseMixin, DetailView):
    model = Kv1Stop
    render_object = 'object'

    def get_object(self, **kwargs):
        qry = self.get_queryset()
        return {'extent': qry.aggregate(Extent('location')).get('location__extent')}

    def get_queryset(self):
        qry = super(MessageStopsBoundAjaxView, self).get_queryset()
        qry = qry.filter(kv15stopmessage__id=self.kwargs.get('pk', None))

        if not (self.request.user.has_perm("openebs.view_all") or self.request.user.has_perm("openebs.edit_all")):
            qry = qry.filter(kv15stopmessage__dataownercode=self.request.user.userprofile.company)

        return qry
