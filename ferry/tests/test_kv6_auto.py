from datetime import datetime, timedelta
from django.contrib.gis.geos import Point
from django.core.management import call_command
from django.test import TestCase

from ferry.management.commands.sendkv6 import Command as SendKv6Command
from ferry.models import FerryLine, FerryKv6Messages
from kv1.models import Kv1Line, Kv1Stop, Kv1Journey, Kv1JourneyDate


class TestFerryKv6Messages(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestFerryKv6Messages, cls).setUpClass()

        # Setup data
        cls.stop_depart = Kv1Stop(dataownercode="WSF", userstopcode=1, location=Point(1, 1))
        cls.stop_depart.save()
        cls.stop_arrive = Kv1Stop(dataownercode="WSF", userstopcode=2, location=Point(1, 1))
        cls.stop_arrive.save()
        cls.line = Kv1Line(dataownercode="WSF", lineplanningnumber=101, publiclinenumber="FF", headsign="FastFerry")
        cls.line.save()
        cls.ferry = FerryLine(line=cls.line, stop_depart=cls.stop_depart, stop_arrival=cls.stop_arrive, enable_auto_messages=True)
        cls.ferry.save()

        # Going to need a few journeys
        j1 = Kv1Journey(dataownercode="WSF", line=cls.line, journeynumber=1, direction=1,
                        scheduleref=1, departuretime=cls.calc(datetime.now()-timedelta(hours=2)), )
        j1.save()
        j2 = Kv1Journey(dataownercode="WSF", line=cls.line, journeynumber=2, direction=0,
                        scheduleref=1, departuretime=cls.calc(datetime.now()-timedelta(minutes=19)))
        j2.save()
        j3 = Kv1Journey(dataownercode="WSF", line=cls.line, journeynumber=3, direction=1,
                        scheduleref=1, departuretime=cls.calc(datetime.now()+timedelta(minutes=4)))
        j3.save()
        j4 = Kv1Journey(dataownercode="WSF", line=cls.line, journeynumber=4, direction=0,
                        scheduleref=1, departuretime=cls.calc(datetime.now()+timedelta(hours=2)))
        j4.save()
        Kv1JourneyDate(journey=j1, date=datetime.now()).save()
        Kv1JourneyDate(journey=j2, date=datetime.now()).save()
        Kv1JourneyDate(journey=j3, date=datetime.now()).save()
        Kv1JourneyDate(journey=j4, date=datetime.now()).save()

    @staticmethod
    def calc(time):
        return (time.hour * 60 + time.minute) * 60

    def test_send_if_enabled(self):
        self.ferry.enable_auto_messages=False
        self.ferry.save()
        self.assertEqual(0, FerryKv6Messages.objects.count())
        call_command('sendkv6')
        self.assertEqual(0, FerryKv6Messages.objects.count())

        self.ferry.enable_auto_messages=True
        self.ferry.save()
        call_command('sendkv6')
        self.assertEqual(3, FerryKv6Messages.objects.count())

    def test_send_initial(self):
        self.assertEqual(0, FerryKv6Messages.objects.count())

        call_command('sendkv6')
        self.assertEqual(3, FerryKv6Messages.objects.count())
        msgs = FerryKv6Messages.objects.all().order_by('created')
        self.assertEqual(FerryKv6Messages.Status.ARRIVED, msgs[0].status)
        self.assertEqual(FerryKv6Messages.Status.DEPARTED, msgs[1].status)
        self.assertEqual(FerryKv6Messages.Status.READY, msgs[2].status)

        # Other messages haven't been created, verified by counting

    def test_send_delay_init(self):
        """ Test the case where we have a delay before we even get ready"""
        self.assertEqual(0, FerryKv6Messages.objects.count())
        delay_msg = FerryKv6Messages(ferry=self.ferry, operatingday=datetime.now(), journeynumber=3, delay=300)
        delay_msg.save()

        call_command('sendkv6')
        self.assertEqual(3, FerryKv6Messages.objects.count())
        msgs = FerryKv6Messages.objects.all().order_by('created')

        self.assertEqual(3, msgs[0].journeynumber)
        self.assertEqual(FerryKv6Messages.Status.INITIALIZED, msgs[0].status)  # This message is first cause it has a delay and is created above
        self.assertEqual(1, msgs[1].journeynumber)
        self.assertEqual(FerryKv6Messages.Status.ARRIVED, msgs[1].status)
        self.assertEqual(2, msgs[2].journeynumber)
        self.assertEqual(FerryKv6Messages.Status.DEPARTED, msgs[2].status)

        delay_msg.delay = 0
        delay_msg.save()

        call_command('sendkv6')
        self.assertEqual(3, FerryKv6Messages.objects.count())
        msgs = FerryKv6Messages.objects.all().order_by('created')

        self.assertEqual(3, msgs[0].journeynumber)
        self.assertEqual(FerryKv6Messages.Status.READY, msgs[0].status)
        self.assertEqual(1, msgs[1].journeynumber)
        self.assertEqual(FerryKv6Messages.Status.ARRIVED, msgs[1].status)
        self.assertEqual(2, msgs[2].journeynumber)
        self.assertEqual(FerryKv6Messages.Status.DEPARTED, msgs[2].status)

    def test_send_delay_depart(self):
        """ Test the case where we have a delay just before we depart
            journeynumber 2 was supposed to leave 19 minutes ago but is delayed by that much """
        self.assertEqual(0, FerryKv6Messages.objects.count())
        delay_msg = FerryKv6Messages(ferry=self.ferry, operatingday=datetime.now(), journeynumber=2, delay=19*60+30)
        delay_msg.save()

        call_command('sendkv6')
        self.assertEqual(3, FerryKv6Messages.objects.count())
        msgs = FerryKv6Messages.objects.all().order_by('created')

        self.assertEqual(2, msgs[0].journeynumber)
        self.assertEqual(FerryKv6Messages.Status.READY, msgs[0].status)  # This message is first cause it has a delay and is created above
        self.assertEqual(1, msgs[1].journeynumber)
        self.assertEqual(FerryKv6Messages.Status.ARRIVED, msgs[1].status)
        self.assertEqual(3, msgs[2].journeynumber)
        self.assertEqual(FerryKv6Messages.Status.READY, msgs[2].status)

    def test_send_delay_arrive(self):
        """ Test the case where we have a delay after we depart but before arriving
        Delay trip 1 by hour and 45 minutes, it was supposed to depart 2 hours ago and so hasn't yet arrived
        """
        self.assertEqual(0, FerryKv6Messages.objects.count())
        delay_msg = FerryKv6Messages(ferry=self.ferry, operatingday=datetime.now(), journeynumber=1, delay=(60+45)*60)
        delay_msg.save()

        call_command('sendkv6')
        self.assertEqual(3, FerryKv6Messages.objects.count())
        msgs = FerryKv6Messages.objects.all().order_by('created')

        self.assertEqual(1, msgs[0].journeynumber)
        self.assertEqual(FerryKv6Messages.Status.DEPARTED, msgs[0].status)
        self.assertEqual(2, msgs[1].journeynumber)
        self.assertEqual(FerryKv6Messages.Status.DEPARTED, msgs[1].status)
        self.assertEqual(3, msgs[2].journeynumber)
        self.assertEqual(FerryKv6Messages.Status.READY, msgs[2].status)

        delay_msg.delay = (60+40)*60  # 5 minutes less delay, should now have arrived
        delay_msg.save()

        call_command('sendkv6')
        msgs = FerryKv6Messages.objects.all().order_by('created')

        self.assertEqual(1, msgs[0].journeynumber)
        self.assertEqual(FerryKv6Messages.Status.ARRIVED, msgs[0].status)
        self.assertEqual(2, msgs[1].journeynumber)
        self.assertEqual(FerryKv6Messages.Status.DEPARTED, msgs[1].status)
        self.assertEqual(3, msgs[2].journeynumber)
        self.assertEqual(FerryKv6Messages.Status.READY, msgs[2].status)