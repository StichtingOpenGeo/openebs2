import json
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.core.urlresolvers import reverse
from django.db import transaction
from django.test import Client
from django.utils.unittest.case import TestCase
from kv1.models import Kv1Stop
from openebs.models import Kv15MessageStop, UserProfile
from openebs.tests.utils import TestUtils


class TestAjaxViews(TestCase):
    haltes = []

    @classmethod
    def setUpClass(cls):
        # Setup user and assign company
        cls.user = User.objects.create_user(username="test_view", password="test")
        cls.user.save()
        p = UserProfile(user=cls.user, company='HTM')
        p.save()

        # Setup stops
        h1 = Kv1Stop(pk=10, dataownercode='HTM', userstopcode='111', name="Om de hoek", location=Point(1, 1))
        h2 = Kv1Stop(pk=11, dataownercode='HTM', userstopcode='112', name="Hier", location=Point(2, 2))
        h1.save()
        h2.save()
        cls.haltes.append(h1)
        cls.haltes.append(h2)

    def setUp(self):
        self.client = Client()

    def get_halte_list(self, scenario):
        resp = self.client.get(reverse('scenario_stops_ajax', args=[scenario]))
        return [h['userstopcode'] for h in json.loads(resp.content)['object']]

    # TODO: Fix this test
    # def test_active_stops_deleted_message(self):
    #     """
    #     Test that a deleted message doesn't show up in the list of stops that are active as per the AJAX view
    #     """
    #     msg1 = TestUtils.create_message_default(self.user)
    #     msg1.save()
    #     a = Kv15MessageStop(stopmessage=msg1, stop=self.haltes[0])
    #     a.save()
    #
    #     msg2 = TestUtils.create_message_default(self.user)
    #     msg2.save()
    #     b = Kv15MessageStop(stopmessage=msg2, stop=self.haltes[1])
    #     b.save()
    #
    #     result = self.client.login(username="test_view", password="test")
    #     self.assertTrue(result)
    #     self.assertListEqual(self.get_halte_list(0), ["111", "112"])
    #
    #     msg1.delete()
    #     self.assertListEqual(self.get_halte_list(0), ["112"])