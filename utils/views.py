import logging
import re
# TODO: Figure out which mixin we really need
from django.http import HttpResponseNotAllowed
from django.template import RequestContext
from django.template import loader
from django.views.generic import TemplateView

try:
    from braces.views import AccessMixin as BracesAccessMixin
except:
    from braces.views._access import AccessMixin as BracesAccessMixin

from braces.views import JSONResponseMixin
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.shortcuts import redirect, render
from utils.push import Push
from django.db.models.query import QuerySet

log = logging.getLogger('openebs.views.mixins')


class JSONListResponseMixin(JSONResponseMixin):
    render_object = None  # Name of thing to get from context object

    def render_to_response(self, context):
        contents = {}
        if self.render_object:
            if isinstance(context[self.render_object], QuerySet):
                contents[self.render_object] = list(context[self.render_object])
            else:
                contents[self.render_object] = context[self.render_object]
        return self.render_json_response(contents)


class ExternalMessagePushMixin(object):
    message_type = None  # Abstract
    namespace = ''
    dossier = ''
    pushers = []

    def __init__(self):
        self.pushers = self.get_pushers(settings.PUSH_SETTINGS, settings.PUSH_DEFAULTS)

    def push_message(self, msg):
        """
        Push message _msg_ to GOVI and other subscribers, and return if it was successful
        """
        if len(self.pushers) == 0:
            log.warning("No pushers have been defined")
            if settings.DEBUG:
                return True

        success = False
        for pusher in self.pushers:
            code, content = pusher.push(msg)
            if code == 200 and '>OK</' in content:
                success = True
            else:
                log.error("Push to %s failed with code %s: %s" % (pusher.alias, code, self.parse_error(content)))
                if pusher.fail_on_failure:
                    success = False
                    log.error("Failing after %s failed, not pushing to other subscribers" % (pusher.alias))
                    break
                else:
                    success = True
        return success

    @staticmethod
    def parse_error(content):
        if content is not None and content != "":
            regex = re.compile("<tmi8:ResponseError>(.*)</tmi8:ResponseError>", re.MULTILINE | re.DOTALL)
            r = regex.search(content)
            return r.groups()[0] if r is not None else ""
        return "?"

    def get_pushers(self, settings, defaults):
        """
        Setup the push class - storage for all things related to a specific subscriber channel (meaning an endpoint)
        """
        push_list = []
        for destination in sorted(settings, key=lambda k: k['priority']):
            if not destination['enabled']:
                continue
            if self.message_type is None or self.message_type not in destination['endpoints']:
                raise ImproperlyConfigured("Endpoint type isn't registered")
            if self.namespace == '' or self.namespace is None:
                raise ImproperlyConfigured("Namespace isn't configured")
            if self.dossier == '' or self.dossier is None:
                raise ImproperlyConfigured("Dossier isn't configured")

            endpoint = destination['endpoints'][self.message_type]

            p = Push(destination['host'], endpoint['path'],
                     self.namespace,
                     self.dossier,
                     destination['subscriberName'],
                     destination['https'] if 'https' in destination else False)
            p.alias = destination.get('alias', destination['host'])
            p.fail_on_failure = destination.get('failOnFailure', True)
            p.debug = destination.get('debug', defaults.get('debug', False))
            p.timeout = destination.get('timeout', defaults.get('timeout', False))
            push_list.append(p)
        return push_list


class AccessMixin(BracesAccessMixin):
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

        if request.user.is_authenticated:
            if not has_permission:  # If the user lacks the permission
                log.info("User %s requested %s but doesn't have permission" % (self.request.user, request.get_full_path()))
                return redirect(reverse('app_nopermission'))

            if not hasattr(request.user, 'userprofile') or \
                    not hasattr(request.user.userprofile, 'company'):
                log.info("User %s requested %s but doesn't have an userprofile or operator" % (
                self.request.user, request.get_full_path()))
                return redirect(reverse('app_nopermission'))

        else:
            return redirect_to_login(request.get_full_path(),
                                     self.get_login_url(),
                                     self.get_redirect_field_name())

        return super(AccessMixin, self).dispatch(
            request, *args, **kwargs)


def handler403(request, exception):
    response = render(request, 'openebs/nopermission.html', {})
    response.status_code = 404
    return response


def handler404(request, exception):
    response = render(request, 'openebs/notfound.html', {})
    response.status_code = 404
    return response


def handler500(request):
    response = render(request, 'openebs/servererror.html', {})
    response.status_code = 500
    return response
