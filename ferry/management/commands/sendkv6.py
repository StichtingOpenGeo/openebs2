import logging
from datetime import datetime, time, timedelta
from django.core.management import BaseCommand

from ferry.models import FerryLine, FerryKv6Messages
from openebs.views_push import Kv6PushMixin
from utils.time import get_operator_date
from utils.views import ExternalMessagePushMixin

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
        print "Checking ferry: %s" % ferry.line
        ## READY: Init + Arrive
        for journey in journeys.filter(departuretime__lte=self.get_target_time(5)):
            msg, created = FerryKv6Messages.objects.get_or_create(operatingday=date, ferry=ferry,
                                                                  journeynumber=journey.journeynumber)
            if created or (msg.status == FerryKv6Messages.Status.INITIALIZED and not msg.cancelled):
                msg.status = FerryKv6Messages.Status.READY
                msg.save()
                if self.pusher.push_message(msg.to_kv6_ready(journey.direction)):
                    self.log('info', "Sent KV6 init & arrival message for %s" % msg)
                else:
                    self.log('error', "Failed to send KV6 init & arrival message for %s" % msg)
            else:
                self.log('debug', "Already sent for %s" % journey.departuretime_as_time())

        ## DEPARTED: Depart
        # TODO: Fix delayed
        for journey in journeys.filter(departuretime__lte=self.get_target_time(0)):
            try:
                msg = FerryKv6Messages.objects.get(operatingday=date, ferry=ferry, journeynumber=journey.journeynumber,
                                                   status=FerryKv6Messages.Status.READY, cancelled=False)
                msg.status = FerryKv6Messages.Status.DEPARTED
                msg.save()

                if self.pusher.push_message(msg.to_kv6_departed(journey.direction)):
                    self.log('info', "Sent KV6 depart message for %s" % msg)
                else:
                    self.log('error', "Failed to send KV6 depart message for %s" % msg)

            except FerryKv6Messages.DoesNotExist:
                self.log('debug', "Skip for departed")

        ## ARRIVED: Arrive
        # TODO: Fix delayed
        for journey in journeys.filter(departuretime__lte=self.get_target_time(-20)):
            try:
                msg = FerryKv6Messages.objects.get(operatingday=date, ferry=ferry, journeynumber=journey.journeynumber,
                                                   status=FerryKv6Messages.Status.DEPARTED, cancelled=False)

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
            print "%s: %s" % (level, text)
        else:
            self.log(level, text)