import csv

from datetime import date
from django.core.management import BaseCommand

from kv1.models import Kv1Journey
from openebs.models import Kv17Change
from openebs.views_push import Kv17PushMixin
from utils.time import get_operator_date


class Command(BaseCommand):

    pusher = Kv17PushMixin() # TODO: This defines a default timeout, we may want to/need to change this for batch operations

    last_row_date = ""
    date = get_operator_date()

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)

    def handle(self, *args, **options):
        with open(options['filename'][0], 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            first = True
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
                        self.cancel_trip(trips, self.date)
                    self.last_row_date = row[1]

    def cancel_trip(self, journey, date):
        if Kv17Change.objects.filter(dataownercode=journey.dataownercode, operatingday=date, line=journey.line, journey=journey).count() == 0:
            self.stdout.write("Cancelling: %s:%s:%s on %s " % (journey.dataownercode, journey.line.lineplanningnumber, journey.journeynumber, date))
            modification = Kv17Change(dataownercode=journey.dataownercode, operatingday=date, line=journey.line, journey=journey)
            modification.save()
            self.pusher.push_message(modification.to_xml())
        else:
            self.stdout.write("Already cancelled: %s:%s:%s on %s " % (journey.dataownercode, journey.line.lineplanningnumber, journey.journeynumber, date))
