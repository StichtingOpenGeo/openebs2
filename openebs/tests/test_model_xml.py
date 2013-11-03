from django.utils.unittest.case import TestCase
from openebs.models import Kv15Stopmessage


class TestKv15MessageXmlModel(TestCase):

    def test_output(self):
        m1 = Kv15Stopmessage(dataownercode='HTM')
        m1.save()

