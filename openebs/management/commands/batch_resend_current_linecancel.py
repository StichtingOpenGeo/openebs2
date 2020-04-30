import csv

from datetime import date, datetime
from django.core.management import BaseCommand

from kv1.models import Kv1Journey
from openebs.models import Kv17ChangeLine
from openebs.views_push import Kv17PushMixin
from utils.time import get_operator_date


class Command(BaseCommand):

    pusher = Kv17PushMixin()
    BATCH_SIZE = 100

    date = get_operator_date()

    def handle(self, *args, **options):
        to_send = []
        to_send_lines = []
        changes = Kv17ChangeLine.objects.filter(operatingday=self.date) \
            .order_by('dataownercode', 'line__lineplanningnumber', 'line__publiclinenumber')
        for line in changes:
            if line.is_cancel:
                res = line.to_xml()
                if res is not None:
                    self.log("Resending: %s on %s" % (line.realtime_id(), self.date))
                    to_send.append(res)
                    to_send_lines.append(line)
                else:
                    self.log("ERROR!: %s on %s" % (line.realtime_id(), self.date))
            else:
                self.log("Not cancelled: %s on %s" % (line.realtime_id(), self.date))
            if len(to_send) > 0 and len(to_send) % self.BATCH_SIZE == 0:
                to_send, to_send_lines = self.send(to_send, to_send_lines)

        if len(to_send) > 0:
            self.send(to_send, to_send_lines)

    def send(self, to_send, to_send_lines):
        start = datetime.now()
        success = self.pusher.push_message(to_send)
        if success:
            self.log("Sending batch of %s, took %s seconds" % (len(to_send), (datetime.now() - start).seconds))
        else:
            self.log("Failed to send batch! %s" % to_send_lines)
        to_send = []
        to_send_lines = []
        return to_send, to_send_lines

    def log(self, msg):
        self.stdout.write("%s - %s" % (datetime.now().isoformat(), msg))
