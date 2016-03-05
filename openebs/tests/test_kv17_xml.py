from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point

from kv1.models import Kv1Stop, Kv1Line, Kv1Journey
from openebs.models import Kv17Change, Kv17StopChange
from utils.xml_test import XmlTest


class TestKv17MessageXmlModel(XmlTest):
    @classmethod
    def setUpClass(cls):
        super(TestKv17MessageXmlModel, cls).setUpClass()
        cls.user = User.objects.create_user("test")

        cls.haltes = []
        halte_a = Kv1Stop(userstopcode=100, dataownercode='HTM', name="Om de hoek", location=Point(1, 1))
        halte_b = Kv1Stop(userstopcode=101, dataownercode='HTM', name="De andere hoek", location=Point(1, 10))
        halte_a.save()
        halte_b.save()
        cls.haltes.append(halte_a)
        cls.haltes.append(halte_b)

        cls.line = Kv1Line(dataownercode='HTM', lineplanningnumber="1001", publiclinenumber="1", headsign="Naar Huis")
        cls.line.save()
        cls.journey = Kv1Journey(dataownercode='HTM', line=cls.line, journeynumber=100, scheduleref=1, departuretime=900, direction=1)
        cls.journey.save()

    def test_output_cancel_recover(self):
        change = Kv17Change(dataownercode='HTM', line=self.line, journey=self.journey, operatingday=datetime(2016, 04, 01))
        change.save()

        # Have to pad with "DOSSIER" since otherwise we have invalid XML
        self.assertXmlEqual("<DOSSIER>%s</DOSSIER>" % change.to_xml(), self.getCompareXML('openebs/tests/output/kv17_cancel.xml'))

        change.delete()
        self.assertXmlEqual("<DOSSIER>%s</DOSSIER>" % change.to_xml(), self.getCompareXML('openebs/tests/output/kv17_recover.xml'))

    def test_output_mutationmessage(self):
        journey = Kv1Journey(dataownercode='HTM', line=self.line, journeynumber=101, scheduleref=1, departuretime=905, direction=1)
        journey.save()

        change = Kv17Change(dataownercode='HTM', line=self.line, journey=journey, operatingday=datetime(2016, 04, 01),
                            is_cancel=False)
        change.save()
        stop_change = Kv17StopChange(change=change, type=5, stop=self.haltes[0], stoporder=1,
                       reasontype=3, subreasontype=7, reasoncontent="Boot is vol")
        stop_change.save()

        # Have to pad with "DOSSIER" since otherwise we have invalid XML
        self.assertXmlEqual( "<DOSSIER>%s</DOSSIER>" % change.to_xml(),
                             self.getCompareXML('openebs/tests/output/kv17_mutationmessage.xml'))
        stop_change.advicetype=1
        stop_change.subadvicetype=3
        stop_change.advicecontent="Pak de volgende boot"
        stop_change.save()

        self.assertXmlEqual( "<DOSSIER>%s</DOSSIER>" % change.to_xml(),
                             self.getCompareXML('openebs/tests/output/kv17_mutationmessage_complete.xml'))

        change.delete()
        self.assertXmlEqual( "<DOSSIER>%s</DOSSIER>" % change.to_xml(),
                             self.getCompareXML('openebs/tests/output/kv17_mutationmessage_recover.xml'))
