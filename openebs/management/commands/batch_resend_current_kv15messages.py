import csv

from datetime import date, datetime
from django.core.management import BaseCommand

from openebs.models import Kv15Stopmessage
from openebs.views_push import Kv17PushMixin
from utils.time import get_operator_date
from django.utils.timezone import is_aware, make_aware

class Command(BaseCommand):

    pusher = Kv17PushMixin()
    BATCH_SIZE = 100

    date = get_operator_date()
    current = datetime.now()
    if not is_aware(current):
        current = make_aware(current)

    def handle(self, *args, **options):
        to_send = []
        to_send_messages = []
        message_changes = Kv15Stopmessage.objects.filter(messageendtime__gte=self.current) \
            .order_by('dataownercode', 'messagecodenumber', 'messagestarttime', 'messageendtime')
        if len(message_changes) != 0:
            for message in message_changes:
                res = message.to_xml()
                if res is not None:
                    self.log("Resending: %s on %s" % (message.realtime_id(), self.date))
                    to_send.append(res)
                    to_send_messages.append(message)
                else:
                    self.log("ERROR!: %s on %s" % (message.realtime_id(), self.date))
            else:
                self.log("Not send: %s on %s" % (message.realtime_id(), self.date))
            if len(to_send) > 0 and len(to_send) % self.BATCH_SIZE == 0:
                to_send, to_send_messages = self.send(to_send, to_send_messages)
        if len(to_send) > 0:
            self.send(to_send, to_send_messages)

    def send(self, to_send, to_send_messages):
        start = datetime.now()
        success = self.pusher.push_message(to_send)
        if success:
            self.log("Sending batch of %s, took %s seconds" % (len(to_send), (datetime.now() - start).seconds))
        else:
            self.log("Failed to send batch! %s" % to_send_messages)
        to_send = []
        to_send_messages = []
        return to_send, to_send_messages

    def log(self, msg):
        self.stdout.write("%s - %s" % (datetime.now().isoformat(), msg))
