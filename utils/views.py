import logging
import re
from braces.views import JSONResponseMixin, AccessMixin
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from push import Push
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


class GoviPushMixin(object):
    dossier = settings.GOVI_KV15_DOSSIER
    path = settings.GOVI_KV15_PATH
    namespace = settings.GOVI_KV15_NAMESPACE
    pusher = Push(settings.GOVI_SUBSCRIBER)

    def push_govi(self, msg):
        """
        Push message _msg_ to GOVI, and return if it was succesfull
        """
        success = False
        code, content = self.pusher.push(settings.GOVI_HOST, self.namespace, self.dossier, self.path, msg)
        if code == 200 and '>OK</' in content:
            success = True
        else:
            log.error("Push to GOVI failed with code %s: %s" % (code, self.parse_error(content)))
        return success

    @staticmethod
    def parse_error(content):
        if content is not None and content != "":
            regex = re.compile("<tmi8:ResponseError>(.*)</tmi8:ResponseError>", re.MULTILINE | re.LOCALE | re.DOTALL)
            r = regex.search(content)
            return r.groups()[0] if r is not None else ""
        return "?"


class AccessMixin(AccessMixin):
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

        return super(AccessMixin, self).dispatch(
            request, *args, **kwargs)