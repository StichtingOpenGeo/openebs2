from datetime import timedelta
from unittest import TestCase
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.utils.timezone import now
from kv1.models import Kv1Stop
from kv15.enum import *
from openebs.models import Kv15Scenario, Kv15ScenarioMessage, Kv15ScenarioStop, Kv15Stopmessage

__author__ = 'joel'


class Kv15ScenarioModel(TestCase):
    haltes = []
    user = None

    def setUp(self):
        # Haltes
        h1 = Kv1Stop(pk=10, userstopcode='111', name="Om de hoek", location=Point(1, 1))
        h2 = Kv1Stop(pk=11, userstopcode='112', name="Hier", location=Point(1, 1))
        h3 = Kv1Stop(pk=12, userstopcode='113', name="Daar", location=Point(2, 2))
        h4 = Kv1Stop(pk=14, userstopcode='114', name="Overal", location=Point(3, 3))
        h5 = Kv1Stop(pk=15, userstopcode='115', name="Nergens", location=Point(4, 4))
        h1.save()
        h2.save()
        h3.save()
        h4.save()
        h5.save()
        self.haltes.append(h1)
        self.haltes.append(h2)
        self.haltes.append(h3)
        self.haltes.append(h4)
        self.haltes.append(h5)

        # User
        self.user = User.objects.filter(username="test_scenario")
        if self.user.count() < 1:
            self.user = User.objects.create_user("test_scenario")
        else:
            self.user = self.user[0]

    def test_plan_scenario_multiple(self):
        self.assertEqual(0, Kv15Stopmessage.objects.filter(dataownercode='HTM').count())

        a = Kv15Scenario(name="Just a test")
        a.save()

        m1 = Kv15ScenarioMessage(scenario=a, dataownercode='HTM', messagecontent='Blah!')
        m1.save()

        Kv15ScenarioStop(message=m1, stop=self.haltes[0]).save()
        Kv15ScenarioStop(message=m1, stop=self.haltes[1]).save()

        m2 = Kv15ScenarioMessage(scenario=a, dataownercode='HTM', messagecontent='We rijden niet!')
        m2.save()

        Kv15ScenarioStop(message=m2, stop=self.haltes[2]).save()

        m3 = Kv15ScenarioMessage(scenario=a, dataownercode='HTM', messagecontent='We rijden toch misschien wel hier niet!')
        m3.save()

        Kv15ScenarioStop(message=m3, stop=self.haltes[3]).save()
        Kv15ScenarioStop(message=m3, stop=self.haltes[4]).save()

        a.plan_messages(self.user, now(), now()+timedelta(hours=3))

        msgs = Kv15Stopmessage.objects.filter(dataownercode='HTM')
        self.assertEqual(3, msgs.count())
        self.assertEqual(msgs[0].messagecodenumber, 1)
        self.assertEqual(msgs[0].dataownercode, 'HTM')
        self.assertEqual(msgs[0].messagecodedate, now().date())
        self.assertEqual(msgs[0].messagecontent, m1.messagecontent)
        self.assertEqual(msgs[0].stops.all()[0].userstopcode, self.haltes[0].userstopcode)
        self.assertEqual(msgs[0].stops.all()[1].userstopcode, self.haltes[1].userstopcode)
        self.assertEqual(msgs[1].messagecodenumber, 2)
        self.assertEqual(msgs[1].dataownercode, 'HTM')
        self.assertEqual(msgs[1].messagecodedate, now().date())
        self.assertEqual(msgs[1].messagecontent, m2.messagecontent)
        self.assertEqual(msgs[1].stops.all()[0].userstopcode, self.haltes[2].userstopcode)
        self.assertEqual(msgs[2].messagecodenumber, 3)
        self.assertEqual(msgs[2].dataownercode, 'HTM')
        self.assertEqual(msgs[2].messagecodedate, now().date())
        self.assertEqual(msgs[2].messagecontent, m3.messagecontent)
        self.assertEqual(msgs[2].stops.all()[0].userstopcode, self.haltes[3].userstopcode)
        self.assertEqual(msgs[2].stops.all()[1].userstopcode, self.haltes[4].userstopcode)


    def test_plan_scenario_complete(self):
        a = Kv15Scenario(name="Test complete scenario with all fields")
        a.save()

        m1 = Kv15ScenarioMessage(scenario=a, dataownercode='CXX', messagecontent='This trip will not operate')
        m1.messagepriority = MESSAGEPRIORITY[0][0]
        m1.messagetype = MESSAGETYPE[0][0]
        m1.messagedurationtype = MESSAGEDURATIONTYPE[0][0]
        m1.reasontype = REASONTYPE[0][0]
        m1.subreasontype = SUBREASONTYPE[0][0]
        m1.reasoncontent = "Oorzaak uitgelegd"
        m1.effecttype = EFFECTTYPE[0][0]
        m1.subeffecttype = SUBEFFECTTYPE[0][0]
        m1.effectcontent = "Gevolg uitgelegd"
        m1.measuretype = MEASURETYPE[0][0]
        m1.submeasuretype = SUBMEASURETYPE[0][0]
        m1.measurecontent = "Aanpassing uitgelegd"
        m1.advicetype = ADVICETYPE[0][0]
        m1.subadvicetype = SUBADVICETYPE[0][0]
        m1.advicecontent = "Advies uitgelegd"
        m1.save()

        Kv15ScenarioStop(message=m1, stop=self.haltes[0]).save()

        start = now()
        a.plan_messages(self.user, start, start+timedelta(hours=5))
        msgs = Kv15Stopmessage.objects.filter(dataownercode='CXX')
        self.assertEqual(msgs[0].messagepriority, m1.messagepriority)