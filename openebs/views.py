# Create your views here.
import re
from braces.views import AccessMixin, LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Q
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, UpdateView, FormView, DetailView
from django.views.generic.edit import CreateView, DeleteView, BaseFormView
from django.utils.timezone import now
from djgeojson.views import GeoJSONLayerView
from kv1.models import Kv1Stop
from utils.client import get_client_ip
from openebs.models import Kv15Stopmessage, Kv15Log, Kv15Scenario, Kv15ScenarioMessage, MessageStatus
from openebs.form import Kv15StopMessageForm, Kv15ScenarioForm, Kv15ScenarioMessageForm, PlanScenarioForm

import logging
from utils.push import Push
from utils.views import JSONListResponseMixin

log = logging.getLogger('openebs.views')

class OpenEbsUserMixin(AccessMixin):
    """
    This is based on the braces LoginRequiredMixin and PermissionRequiredMixin but will only raise the exception
    if the user is logged in
    """
    permission_required = None  # Default required perms to none

    def dispatch(self, request, *args, **kwargs):
        # Make sure that the permission_required attribute is set on the
        # view, or raise a configuration error.
        if self.permission_required is None:
            raise ImproperlyConfigured(
                "'PermissionRequiredMixin' requires "
                "'permission_required' attribute to be set.")

        # Check to see if the request's user has the required permission.
        has_permission = request.user.has_perm(self.permission_required)

        if request.user.is_authenticated():
            if not has_permission:  # If the user lacks the permission
                log.info("User %s requested %s but doesn't have permission" % (self.request.user, request.get_full_path()))
                return redirect(reverse('app_nopermission'))
        else:
            return redirect_to_login(request.get_full_path(),
                                     self.get_login_url(),
                                     self.get_redirect_field_name())

        return super(OpenEbsUserMixin, self).dispatch(
            request, *args, **kwargs)

class GoviPushEnabled(object):
    pusher = Push(settings.GOVI_SUBSCRIBER, settings.GOVI_DOSSIER, settings.GOVI_NAMESPACE)

    def push_govi(self, msg):
        """
        Push message _msg_ to GOVI, and return if it was succesfull
        """
        success = False
        code, content = self.pusher.push(settings.GOVI_HOST, settings.GOVI_PATH, msg)
        if code == 200 and '>OK</' in content:
            success = True
        else:
            log.error("Push to GOVI failed with code %s: %s" %(code, self.parse_error(content)))
        return success

    def parse_error(self, content):
        regex = re.compile("<tmi8:ResponseError>(.*)</tmi8:ResponseError>",re.MULTILINE|re.LOCALE|re.DOTALL)
        r = regex.search(content)
        return r.groups()[0]

# MESSAGE VIEWS

class MessageListView(OpenEbsUserMixin, ListView):
    permission_required = 'openebs.view_messages'
    model = Kv15Stopmessage

    def get_context_data(self, **kwargs):
        context = super(MessageListView, self).get_context_data(**kwargs)

        # Get the currently active messages
        context['active_list'] = self.model.objects.filter(messageendtime__gt=now,
                                                           isdeleted=False,
                                                           dataownercode=self.request.user.userprofile.company)
        context['active_list'] = context['active_list'].order_by('-messagecodedate', '-messagecodenumber')

        # Add the no longer active messages
        context['archive_list'] = self.model.objects.filter(Q(messageendtime__lt=now) | Q(isdeleted=True), dataownercode=self.request.user.userprofile.company)
        context['archive_list'] = context['archive_list'].order_by('-messagecodedate', '-messagecodenumber')
        return context

class MessageCreateView(OpenEbsUserMixin, GoviPushEnabled, CreateView):
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
        if self.push_govi(form.instance.to_xml()):
            form.instance.set_status(MessageStatus.SENT)
            log.info("Sent message to GOVI: %s" % (form.instance))
        else:
            form.instance.set_status(MessageStatus.ERROR_SEND)
            log.error("Failed to send message to GOVI: %s" % (form.instance))

        return ret

class MessageUpdateView(OpenEbsUserMixin, GoviPushEnabled, UpdateView):
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

        # Push a delete, then a create, but we can use the same message id
        if self.push_govi(form.instance.to_xml_delete()+form.instance.to_xml()):
            form.instance.set_status(MessageStatus.SENT)
            log.info("Sent message to GOVI: %s" % (form.instance))
        else:
            form.instance.set_status(MessageStatus.ERROR_SEND)
            log.error("Failed to send updated message to GOVI: %s" % (form.instance))

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


class MessageDeleteView(OpenEbsUserMixin, GoviPushEnabled, DeleteView):
    permission_required = 'openebs.add_messages'
    model = Kv15Stopmessage
    success_url = reverse_lazy('msg_index')

    def delete(self, request, *args, **kwargs):
        ret = super(MessageDeleteView, self).delete(request, *args, **kwargs)
        obj = self.get_object()
        if self.push_govi(obj.to_xml_delete()):
            obj.set_status(MessageStatus.DELETED)
            log.error("Deleted message succesfully communicated to GOVI: %s" % obj)
        else:
            obj.set_status(MessageStatus.ERROR_SEND_DELETE)
            log.error("Failed to send delete request to GOVI: %s" % obj)
        return ret

# SCENARIO VIEWS
class PlanScenarioView(OpenEbsUserMixin, GoviPushEnabled, FormView):
    permission_required = 'openebs.view_scenario' # TODO Also add message!
    form_class = PlanScenarioForm
    template_name = 'openebs/kv15scenario_plan.html'
    success_url = reverse_lazy('msg_index')

    def get_context_data(self, **kwargs):
        """ Add data about the scenario we're adding to """
        data = super(PlanScenarioView, self).get_context_data(**kwargs)
        if self.kwargs.get('scenario', None):
            data['scenario'] = Kv15Scenario.objects.get(pk=self.kwargs.get('scenario', None))
        return data

    def form_valid(self, form):
        ret = super(PlanScenarioView, self).form_valid(form)
        if self.kwargs.get('scenario', None):
            scenario = Kv15Scenario.objects.get(pk=self.kwargs.get('scenario', None))
            saved = scenario.plan_messages(self.request.user, form.cleaned_data['messagestarttime'],
                                   form.cleaned_data['messageendtime'])
            message_string = "".join([msg.to_xml() for msg in saved])
            if self.push_govi(message_string):
                for msg in saved:
                    msg.set_status(MessageStatus.SENT)
                log.error("Planned messages sent to GOVI: %s" % ",".join([str(msg.messagecodenumber) for msg in saved]))
            else:
                for msg in saved:
                    msg.set_status(MessageStatus.ERROR_SEND)
                log.error("Failed to communicate planned messages to GOVI: %s" % ",".join([str(msg.messagecodenumber) for msg in saved]))
        return ret


class ScenarioListView(OpenEbsUserMixin, ListView):
    permission_required = 'openebs.view_scenario'
    model = Kv15Scenario

    def get_context_data(self, **kwargs):
        context = super(ScenarioListView, self).get_context_data(**kwargs)
        context['object_list'] = self.model.objects.filter(dataownercode=self.request.user.userprofile.company)
        return context


class ScenarioCreateView(OpenEbsUserMixin, CreateView):
    permission_required = 'openebs.add_scenario'
    model = Kv15Scenario
    form_class = Kv15ScenarioForm

    def form_valid(self, form):
        if self.request.user:
            form.instance.dataownercode = self.request.user.userprofile.company

        ret = super(CreateView, self).form_valid(form)

        return ret

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

class ScenarioContentMixin(BaseFormView):
    """  Overide a few defaults used by scenario messages  """
    def get_context_data(self, **kwargs):
        """ Add data about the scenario we're adding to """
        data = super(ScenarioContentMixin, self).get_context_data(**kwargs)
        if self.kwargs.get('scenario', None):
            data['scenario'] = Kv15Scenario.objects.get(pk=self.kwargs.get('scenario', None))
        return data

    def get_success_url(self):
        if self.kwargs.get('scenario', None):
            return reverse_lazy('scenario_edit', args=[self.kwargs.get('scenario')])
        else:
            return reverse_lazy('scenario_index')

class ScenarioMessageCreateView(OpenEbsUserMixin, ScenarioContentMixin, CreateView):
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


class ScenarioMessageUpdateView(OpenEbsUserMixin, ScenarioContentMixin, UpdateView):
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

class ScenarioMessageDeleteView(OpenEbsUserMixin, ScenarioContentMixin, DeleteView):
    permission_required = 'openebs.add_scenario'
    model = Kv15ScenarioMessage

# AJAX Views

class ScenarioStopsAjaxView(LoginRequiredMixin, GeoJSONLayerView):
    model = Kv1Stop
    geometry_field = 'location'
    properties = ['name', 'userstopcode', 'dataownercode', 'messages']

    def get_queryset(self):
        qry = super(ScenarioStopsAjaxView, self).get_queryset()
        qry = qry.filter(kv15scenariostop__message__scenario=self.kwargs.get('scenario', None))
        return qry

class ActiveStopsAjaxView(LoginRequiredMixin, JSONListResponseMixin, DetailView):
    model = Kv1Stop
    render_object = 'object'

    def get_object(self):
        # Note, can't set this on the view, because it triggers the queryset cache
        queryset = self.model.objects.filter(messages__stopmessage__messagestarttime__lte=now(),
                                    messages__stopmessage__messageendtime__gte=now(),
                                    dataownercode=self.request.user.userprofile.company)
        return list(queryset.values('dataownercode', 'userstopcode'))
