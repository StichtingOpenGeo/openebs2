__author__ = 'joel'
from datetime import timedelta
from openebs.models import Kv15Stopmessage
from django.utils.timezone import now


class TestUtils:

    @staticmethod
    def create_message_default(user):
        msg = Kv15Stopmessage()
        msg.user = user
        msg.messagecodedate = now().date().isoformat()
        msg.messageendtime = msg.messagestarttime + timedelta(1)
        msg.measurecontent = "This is a test message"
        return msg