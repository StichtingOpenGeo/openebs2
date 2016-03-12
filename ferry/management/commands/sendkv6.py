from datetime import datetime, time, timedelta
from django.core.management import BaseCommand

from ferry.models import FerryLine
from utils.time import get_operator_date


class Command(BaseCommand):

    help = 'Send KV6 messages as per schedule. Should be scheduled once a minute for correct accuracy'

    def handle(self, *args, **options):
        for ferry in FerryLine.objects.all():
            self.handle_ferry(ferry)

    def handle_ferry(self, ferry):
        print "Checking ferry: %s" % ferry.line
        time = (datetime.now() + timedelta(minutes=20)).time()
        target_time = (time.hour*60+time.minute)*60
        for journey in ferry.line.journeys.filter(dates__date=get_operator_date(), departuretime__lte=target_time).order_by('departuretime'):
            print journey.departuretime_as_time()
            # Check not cancelled
            # Check not delayed
            # Else: Send messages
            # print "%s:%02d" % (hours, minutes)