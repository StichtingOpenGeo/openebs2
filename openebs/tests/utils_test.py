__author__ = 'joel'
from datetime import timedelta
from openebs.models import Kv15Stopmessage
from django.utils.timezone import now


class TestUtils:

    def __init__(self):
        pass

    @staticmethod
    def create_message_default(user):
        msg = Kv15Stopmessage()
        msg.user = user
        msg.dataownercode = 'HTM'
        msg.messagecodedate = now().date().isoformat()
        msg.messagestarttime = now()
        msg.messageendtime = now() + timedelta(hours=3)
        msg.measurecontent = "This is a test message"
        return msg