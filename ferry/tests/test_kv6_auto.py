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
        j1 = Kv1Journey(dataownercode="WSF", line=cls.line, journeynumber=1, direction=1, scheduleref=1, departuretime=cls.calc(datetime.now()-timedelta(hours=2)), )
        j1.save()
        j2 = Kv1Journey(dataownercode="WSF", line=cls.line, journeynumber=2, direction=0, scheduleref=1, departuretime=cls.calc(datetime.now()-timedelta(minutes=19)))
        j2.save()
        j3 = Kv1Journey(dataownercode="WSF", line=cls.line, journeynumber=3, direction=1, scheduleref=1, departuretime=cls.calc(datetime.now()+timedelta(minutes=4)))
        j3.save()
        j4 = Kv1Journey(dataownercode="WSF", line=cls.line, journeynumber=4, direction=0, scheduleref=1, departuretime=cls.calc(datetime.now()+timedelta(hours=2)))
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

    def test_send_delay(self):
        self.assertEqual(0, FerryKv6Messages.objects.count())
        FerryKv6Messages(ferry=self.ferry, operatingday=datetime.now(), journeynumber=3, delay=300).save()

        call_command('sendkv6')
        self.assertEqual(2, FerryKv6Messages.objects.count())
        msgs = FerryKv6Messages.objects.all().order_by('created')
        self.assertEqual(FerryKv6Messages.Status.ARRIVED, msgs[0].status)
        self.assertEqual(FerryKv6Messages.Status.DEPARTED, msgs[1].status)


