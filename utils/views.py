import logging, re
from braces.views import JSONResponseMixin
from django.conf import settings
from push import Push
from django.db.models.query import QuerySet

log = logging.getLogger('openebs.views.mixin')

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
            log.error("Push to GOVI failed with code %s: %s" % (code, self.parse_error(content)))
        return success

    @staticmethod
    def parse_error(content):
        if content is not None and content != "":
            regex = re.compile("<tmi8:ResponseError>(.*)</tmi8:ResponseError>", re.MULTILINE | re.LOCALE | re.DOTALL)
            r = regex.search(content)
            return r.groups()[0]
        return "?"
