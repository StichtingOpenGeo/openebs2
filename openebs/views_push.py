from utils.views import ExternalMessagePushMixin


class Kv15PushMixin(ExternalMessagePushMixin):
    message_type = 'KV15'
    dossier = 'KV15messages'
    namespace = 'http://bison.connekt.nl/tmi8/kv15/msg'


class Kv17PushMixin(ExternalMessagePushMixin):
    message_type = 'KV17'
    namespace = 'http://bison.connekt.nl/tmi8/kv17/msg'
    dossier = 'KV17cvlinfo'


class Kv6PushMixin(ExternalMessagePushMixin):
    message_type = 'KV6'
    namespace = 'http://bison.connekt.nl/tmi8/kv6/msg'
    dossier = 'KV6posinfo'

