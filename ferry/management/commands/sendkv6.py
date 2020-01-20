import logging
from datetime import datetime, time, timedelta
from django.core.management import BaseCommand
from django.db.models import F

from ferry.models import FerryLine, FerryKv6Messages
from openebs.views_push import Kv6PushMixin
from utils.time import get_operator_date

class Command(BaseCommand):

    help = 'Send KV6 messages as per schedule. Should be scheduled once a minute for correct accuracy'

    logger = logging.getLogger('openebs.sendkv6')
    pusher = Kv6PushMixin()
    debug = True

    def handle(self, *args, **options):
        for ferry in FerryLine.objects.filter(enable_auto_messages=True):
            self.handle_ferry(ferry)

    def handle_ferry(self, ferry):
        date = get_operator_date()
        journeys = ferry.line.journeys.filter(dates__date=date).order_by('departuretime')
        print("Checking ferry: %s" % ferry.line)
        ## READY: Init + Arrive
        init_target = self.get_target_time(5)
        for journey in journeys.filter(departuretime__lte=init_target):
            msg, created = FerryKv6Messages.objects.get_or_create(operatingday=date, ferry=ferry,
                                                                  journeynumber=journey.journeynumber)
            if created or (msg.status == FerryKv6Messages.Status.INITIALIZED and not msg.cancelled and (msg.delay is None or
                                   journey.departuretime+msg.delay <= init_target)):
                msg.status = FerryKv6Messages.Status.READY
                msg.save()
                if self.pusher.push_message(msg.to_kv6_ready(journey.direction)):
                    self.log('info', "Sent KV6 init & arrival message for %s" % msg)
                else:
                    self.log('error', "Failed to send KV6 init & arrival message for %s" % msg)
            else:
                self.log('debug', "Already sent for %s" % journey.departuretime_as_time())

        ## DEPARTED: Depart
        depart_target = self.get_target_time(0)
        for journey in journeys.filter(departuretime__lte=depart_target):
            try:
                msg = FerryKv6Messages.objects.get(operatingday=date, ferry=ferry, journeynumber=journey.journeynumber,
                                                   status=FerryKv6Messages.Status.READY, cancelled=False)
                if msg.delay > 0 and journey.departuretime+msg.delay > depart_target:
                    continue

                msg.status = FerryKv6Messages.Status.DEPARTED
                msg.save()

                if self.pusher.push_message(msg.to_kv6_departed(journey.direction)):
                    self.log('info', "Sent KV6 depart message for %s" % msg)
                else:
                    self.log('error', "Failed to send KV6 depart message for %s" % msg)

            except FerryKv6Messages.DoesNotExist:
                self.log('debug', "Skip for departed")

        ## ARRIVED: Arrive
        arrival_target = self.get_target_time(-20)
        for journey in journeys.filter(departuretime__lte=arrival_target):
            try:
                msg = FerryKv6Messages.objects.get(operatingday=date, ferry=ferry, journeynumber=journey.journeynumber,
                                                   status=FerryKv6Messages.Status.DEPARTED, cancelled=False)
                if msg.delay > 0 and journey.departuretime+msg.delay > arrival_target:
                    continue

                msg.status = FerryKv6Messages.Status.ARRIVED
                msg.save()

                if self.pusher.push_message(msg.to_kv6_arrived(journey.direction)):
                    self.log('info', "Sent KV6 arrival message for %s" % msg)
                else:
                    self.log('error', "Failed to send KV6 arrival message for %s" % msg)

            except FerryKv6Messages.DoesNotExist:
                self.log('debug', "Skip for arrived")

    @staticmethod
    def get_target_time(minutes):
        time = (datetime.now() + timedelta(minutes=minutes)).time()
        target_time = (time.hour * 60 + time.minute) * 60
        return target_time

    def log(self, level, text):
        if self.debug:
            print("%s: %s" % (level, text))
        else:
            self.log(level, text)
