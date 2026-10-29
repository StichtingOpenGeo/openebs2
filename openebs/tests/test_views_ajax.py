import json
from django.contrib.auth.models import Permission, User
from django.contrib.gis.geos import Point
from django.urls import reverse
from django.test import Client, TestCase
from kv1.models import Kv1Stop
from openebs.models import Kv15Scenario, Kv15ScenarioMessage, Kv15ScenarioStop, UserProfile


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


class TestScenarioAjaxViews(TestCase):
    def setUp(self):
        user = User.objects.create_user(username="test_scenario_ajax", password="test")
        user.user_permissions.add(Permission.objects.get(content_type__app_label='openebs', codename='view_scenario'))
        UserProfile(user=user, company='HTM').save()
        self.client = Client()
        self.client.login(username="test_scenario_ajax", password="test")

        stop1 = Kv1Stop.objects.create(dataownercode='HTM', userstopcode='211', name="Eerste", location=Point(1, 1))
        stop2 = Kv1Stop.objects.create(dataownercode='HTM', userstopcode='212', name="Tweede", location=Point(2, 2))

        # A scenario first, so scenario and message ids don't line up
        other = Kv15Scenario.objects.create(name="Ander scenario", dataownercode='HTM')
        Kv15ScenarioMessage.objects.create(scenario=other, dataownercode='HTM', messagecontent='Ander')

        self.scenario = Kv15Scenario.objects.create(name="Scenario", dataownercode='HTM')
        self.msg1 = Kv15ScenarioMessage.objects.create(scenario=self.scenario, dataownercode='HTM',
                                                       messagecontent='Een', messagedurationtype='ENDTIME')
        self.msg2 = Kv15ScenarioMessage.objects.create(scenario=self.scenario, dataownercode='HTM',
                                                       messagecontent='Twee', messagedurationtype='REMOVE')
        Kv15ScenarioStop.objects.create(message=self.msg1, stop=stop1)
        Kv15ScenarioStop.objects.create(message=self.msg2, stop=stop2)

    def test_scenario_durationtypes(self):
        """ The duration types of all messages in the scenario, used when planning it """
        resp = self.client.get(reverse('scenario_durations_ajax', args=[self.scenario.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertCountEqual(json.loads(resp.content)['object'],
                              [{'id': self.msg1.pk, 'messagedurationtype': 'ENDTIME'},
                               {'id': self.msg2.pk, 'messagedurationtype': 'REMOVE'}])

    def test_scenario_message_stops(self):
        """ The stops of one scenario message, used when editing it """
        resp = self.client.get(reverse('scenario_msg_stops', args=[self.scenario.pk, self.msg2.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content)['object'], {'None/None': [['HTM_212', 'Tweede']]})
