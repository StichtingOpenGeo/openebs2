import csv

from datetime import date
from django.core.management import BaseCommand

from kv1.models import Kv1Journey
from openebs.models import Kv17Change
from openebs.views_push import Kv17PushMixin
from utils.time import get_operator_date

#TODO Merge with batch_restore
class Command(BaseCommand):

    # TODO: This defines a default timeout, we may want to/need to change this for batch operations
    pusher = Kv17PushMixin()

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
                    cancelled = Kv17Change.objects.filter(dataownercode=dataowner, operatingday=self.date, line__lineplanningnumber=lineplanningnumber, journey__journeynumber=journeynumber)
                    if cancelled.count() == 1:
                        print ("Deleted: %s:%s:%s on %s" % (cancelled[0].dataownercode, cancelled[0].line.lineplanningnumber,
                                                             cancelled[0].journey.journeynumber, cancelled[0].operatingday))
                        cancelled[0].force_delete()
                    else:
                        print ("Not found: %s on %s" % (row[0], self.date))
                    self.last_row_date = row[1]