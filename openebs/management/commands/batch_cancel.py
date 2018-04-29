import csv

from datetime import date
from django.core.management import BaseCommand

from kv1.models import Kv1Journey
from openebs.models import Kv17Change
from openebs.views_push import Kv17PushMixin
from utils.time import get_operator_date


class Command(BaseCommand):

    pusher = Kv17PushMixin() # TODO: This defines a default timeout, we may want to/need to change this for batch operations
    BATCH_SIZE = 50

    last_row_date = ""
    date = get_operator_date()


    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)

    def handle(self, *args, **options):
        with open(options['filename'][0], 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            first = True
            to_send = []
            to_send_trips = []
            for row in reader:
                if first:
                    first = False
                else:
                    dataowner, lineplanningnumber, journeynumber = row[0].split(':')
                    if self.last_row_date != row[1]:
                        split = row[1].split('-')
                        self.date = date(int(split[0]), int(split[1]), int(split[2]))
                    trips = Kv1Journey.find_from_realtime(dataowner, row[0], date=self.date)
                    if trips is None:
                        self.stdout.write("Not found: %s on %s " % (row[0], row[1]))
                    else:
                        res = self.cancel_trip(trips, self.date)
                        if res is not None:
                            to_send.append(res)
                            to_send_trips.append(row[0])
                    if len(to_send) > 0 and len(to_send) % self.BATCH_SIZE == 0:
                        self.stdout.write("Sending batch of %s" % self.BATCH_SIZE)
                        success = self.pusher.push_message(to_send)
                        if not success:
                            self.stdout.write("Failed to send batch! %s" % to_send_trips)
                        to_send = []
                        to_send_trips = []

                    self.last_row_date = row[1]

    def cancel_trip(self, journey, date):
        if Kv17Change.objects.filter(dataownercode=journey.dataownercode,
                                     operatingday=date,
                                     line=journey.line,
                                     journey=journey).count() == 0:
            self.stdout.write("Cancelling: %s:%s:%s on %s " % (journey.dataownercode, journey.line.lineplanningnumber, journey.journeynumber, date))
            modification = Kv17Change(dataownercode=journey.dataownercode, operatingday=date, line=journey.line, journey=journey)
            modification.save()
            return modification.to_xml()
        else:
            self.stdout.write("Already cancelled: %s:%s:%s on %s " % (journey.dataownercode, journey.line.lineplanningnumber, journey.journeynumber, date))
            return None
