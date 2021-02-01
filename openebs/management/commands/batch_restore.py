import csv

from datetime import date, datetime
from django.core.management import BaseCommand

from kv1.models import Kv1Journey
from openebs.models import Kv17Change
from openebs.views_push import Kv17PushMixin
from utils.time import get_operator_date


class Command(BaseCommand):

    # TODO: This defines a default timeout, we may want to/need to change this for batch operations
    pusher = Kv17PushMixin()

    last_row_date = ""
    date = get_operator_date()
    BATCH_SIZE = 100

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
                    # TODO: Fix date here
                    cancelled = Kv17Change.objects.filter(dataownercode=dataowner, operatingday=get_operator_date(), line__lineplanningnumber=lineplanningnumber, journey__journeynumber=journeynumber)
                    if cancelled.count() == 1:
                        cancelled[0].delete()
                        to_send.append(cancelled[0].to_xml())
                        to_send_trips.append(row[0])
                        print ("Restored: %s:%s:%s on %s" % (cancelled[0].dataownercode, cancelled[0].line.lineplanningnumber,
                                                             cancelled[0].journey.journeynumber, cancelled[0].operatingday))
                    else:
                        print ("Not found: %s on %s" % (row[0], row[1]))

                    if len(to_send) > 0 and len(to_send) % self.BATCH_SIZE == 0:
                        self.stdout.write("Sending batch of %s" % self.BATCH_SIZE)
                        start = datetime.now()
                        success = self.pusher.push_message(to_send)
                        self.stdout.write("Took %s seconds" % (datetime.now()-start).seconds)
                        if not success:
                            self.stdout.write("Failed to send batch! %s" % to_send_trips)
                        to_send = []
                        to_send_trips = []

                # TODO: last