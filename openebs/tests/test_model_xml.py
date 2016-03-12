from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.utils.datetime_safe import datetime, date
from django.utils.timezone import make_aware, get_default_timezone
from kv1.models import Kv1Stop
from kv15.enum import *
from openebs.models import Kv15Stopmessage, Kv15MessageStop

from utils.xml_test import XmlTest


class TestKv15MessageXmlModel(XmlTest):
    @classmethod
    def setUpClass(cls):
        super(TestKv15MessageXmlModel, cls).setUpClass()
        cls.user = User.objects.create_user("test")

        cls.haltes = []
        halte_a = Kv1Stop(userstopcode=100, dataownercode='HTM', name="Om de hoek", location=Point(1, 1))
        halte_b = Kv1Stop(userstopcode=101, dataownercode='HTM', name="De andere hoek", location=Point(1, 10))
        halte_a.save()
        halte_b.save()
        cls.haltes.append(halte_a)
        cls.haltes.append(halte_b)

    def test_output_basic(self):


        m1 = Kv15Stopmessage(dataownercode='HTM', user=self.user)
        m1.messagecodedate = datetime.strptime("2013-11-16", "%Y-%m-%d").date()
        m1.messagecodenumber = 4
        start = make_aware(datetime.strptime("2013-11-16T14:09:35.161617", "%Y-%m-%dT%H:%M:%S.%f"), get_default_timezone())
        end = make_aware(datetime.strptime("2013-11-17T03:00:00", "%Y-%m-%dT%H:%M:%S"), get_default_timezone())
        m1.messagestarttime = start
        m1.messageendtime = end
        m1.messagecontent = "Bla!"
        m1.save()
        Kv15MessageStop(stopmessage=m1, stop=self.haltes[0]).save()
        Kv15MessageStop(stopmessage=m1, stop=self.haltes[1]).save()

        self.assertXmlEqual(m1.to_xml(), self.getCompareXML('openebs/tests/output/message_basic.xml'))

    def test_output_complete(self):
        m1 = Kv15Stopmessage(dataownercode='HTM', user=self.user)
        m1.messagecodedate = datetime.strptime("2013-11-16", "%Y-%m-%d").date()
        m1.messagecodenumber = 10
        start = make_aware(datetime.strptime("2013-11-16T14:09:35.161617", "%Y-%m-%dT%H:%M:%S.%f"), get_default_timezone())
        end = make_aware(datetime.strptime("2013-11-17T03:00:00", "%Y-%m-%dT%H:%M:%S"), get_default_timezone())
        m1.messagestarttime = start
        m1.messageendtime = end
        m1.messagecontent = "Bla!"

        m1.messagepriority = MESSAGEPRIORITY[1][0]
        m1.messagetype = MESSAGETYPE[1][0]
        m1.messagedurationtype = MESSAGEDURATIONTYPE[1][0]
        m1.reasontype = REASONTYPE[1][0]
        m1.subreasontype = SUBREASONTYPE[1][0]
        m1.reasoncontent = "Uitleg oorzaak"
        m1.effecttype = EFFECTTYPE[1][0]
        m1.subeffecttype = SUBEFFECTTYPE[1][0]
        m1.effectcontent = "Uitleg gevolg"
        m1.measuretype = MEASURETYPE[1][0]
        m1.submeasuretype = SUBMEASURETYPE[1][0]
        m1.measurecontent = "Uitleg aanpassing"
        m1.advicetype = ADVICETYPE[1][0]
        m1.subadvicetype = SUBADVICETYPE[1][0]
        m1.advicecontent = "Uitleg advies"

        m1.save()
        Kv15MessageStop(stopmessage=m1, stop=self.haltes[0]).save()

        self.assertXmlEqual(m1.to_xml(), self.getCompareXML('openebs/tests/output/message_complete.xml'))

    def test_output_delete(self):
        m1 = Kv15Stopmessage(dataownercode='HTM', user=self.user)
        m1.messagecodedate = datetime.strptime("2013-11-16", "%Y-%m-%d").date()
        m1.messagecodenumber = 11
        start = make_aware(datetime.strptime("2013-11-16T14:09:35.161617", "%Y-%m-%dT%H:%M:%S.%f"), get_default_timezone())
        end = make_aware(datetime.strptime("2013-11-17T03:00:00", "%Y-%m-%dT%H:%M:%S"), get_default_timezone())
        m1.messagestarttime = start
        m1.messageendtime = end
        m1.messagecontent = "Bla!"
        m1.save()
        Kv15MessageStop(stopmessage=m1, stop=self.haltes[0]).save()
        Kv15MessageStop(stopmessage=m1, stop=self.haltes[1]).save()

        self.assertXmlEqual(m1.to_xml_delete(), self.getCompareXML('openebs/tests/output/delete.xml'))