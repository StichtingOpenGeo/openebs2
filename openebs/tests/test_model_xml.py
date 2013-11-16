from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.utils.unittest.case import TestCase
from kv1.models import Kv1Stop
from openebs.models import Kv15Stopmessage, Kv15MessageStop


class TestKv15MessageXmlModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("test")

    def test_output(self):
        halte_a = Kv1Stop(userstopcode=100, dataownercode='HTM', name="Om de hoek", location=Point(1, 1))
        halte_b = Kv1Stop(userstopcode=101, dataownercode='HTM', name="De andere hoek", location=Point(1, 10))
        halte_a.save()
        halte_b.save()

        m1 = Kv15Stopmessage(dataownercode='HTM', user=self.user)
        m1.save()
        Kv15MessageStop(stopmessage=m1, stop=halte_a).save()
        Kv15MessageStop(stopmessage=m1, stop=halte_b).save()

        # print m1.to_xml()

