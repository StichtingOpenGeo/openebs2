from datetime import datetime
from unittest import mock

from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.test import TestCase, override_settings
from django.utils.timezone import make_aware, get_default_timezone
from lxml import etree

from kv1.models import Kv1Line, Kv1Stop
from openebs.models import Kv15Stopmessage, Kv15MessageStop
from openebs.views_push import Kv15PushMixin, Kv17PushMixin, Kv6PushMixin
from utils.push import Push, SiriSxPush
from utils.siri_sx import SIRI_NAMESPACE, RefLookup, _alert_cause, convert, to_siri_sx

NS = {'s': SIRI_NAMESPACE}


def get_fixture(name):
    """ The test output files are wrapped in a DOSSIER for comparing, the pushed content isn't """
    with open('openebs/tests/output/%s' % name) as f:
        return f.read().replace('<DOSSIER>', '').replace('</DOSSIER>', '')


def values(element, path):
    return [e.text for e in element.xpath(path, namespaces=NS)]


class TestSiriSxKv15(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestSiriSxKv15, cls).setUpClass()
        cls.user = User.objects.create_user("test")
        cls.haltes = [Kv1Stop(userstopcode=100, dataownercode='HTM', name="Om de hoek", location=Point(1, 1)),
                      Kv1Stop(userstopcode=101, dataownercode='HTM', name="De andere hoek", location=Point(1, 10))]
        for halte in cls.haltes:
            halte.save()

    def create_message(self):
        m1 = Kv15Stopmessage(dataownercode='HTM', user=self.user)
        m1.messagecodedate = datetime.strptime("2013-11-16", "%Y-%m-%d").date()
        m1.messagecodenumber = 4
        m1.messagestarttime = make_aware(datetime(2013, 11, 16, 14, 9, 35), get_default_timezone())
        m1.messageendtime = make_aware(datetime(2013, 11, 17, 3, 0, 0), get_default_timezone())
        m1.messagecontent = "Bla!"
        m1.messagepriority = 'CALAMITY'
        m1.reasontype = 3
        m1.reasoncontent = "Defecte tram"
        m1.advicetype = 1
        m1.subadvicetype = '2'
        m1.advicecontent = "Neem de bus"
        m1.save()
        for halte in self.haltes:
            Kv15MessageStop(stopmessage=m1, stop=halte).save()
        return m1

    def test_stopmessage(self):
        situations = convert('KV15messages', self.create_message().to_xml())
        self.assertEqual(1, len(situations))
        situation = situations[0]
        self.assertEqual(['NL:BISON:Codespace:HTM'], values(situation, 's:ParticipantRef'))
        self.assertEqual(['nl'], values(situation, 's:CountryRef'))
        self.assertEqual(['KV15:HTM:2013-11-16:4'], values(situation, 's:SituationNumber'))
        self.assertEqual(['open'], values(situation, 's:Progress'))
        self.assertEqual(['2013-11-16T14:09:35+01:00'], values(situation, 's:ValidityPeriod/s:StartTime'))
        self.assertEqual(['2013-11-17T03:00:00+01:00'], values(situation, 's:ValidityPeriod/s:EndTime'))
        # Materieel, without a subreasontype
        self.assertEqual(['technicalProblem'], values(situation, 's:AlertCause'))
        self.assertEqual(['Defecte tram'], values(situation, 's:ReasonName'))
        self.assertEqual(['severe'], values(situation, 's:Severity'))
        self.assertEqual(['1'], values(situation, 's:Priority'))
        self.assertEqual(['incident'], values(situation, 's:ReportType'))
        self.assertEqual(['false'], values(situation, 's:Planned'))
        self.assertEqual(['2013-11-17T03:00:00+01:00'], values(situation, 's:PublicationWindow/s:EndTime'))
        self.assertEqual(['Bla!'], values(situation, 's:Summary'))
        self.assertEqual(['Neem de bus'], values(situation, 's:Advice'))
        self.assertEqual(['100', '101'],
                         values(situation, 's:Affects/s:StopPoints/s:AffectedStopPoint/s:StopPointRef'))

    def test_delete(self):
        situations = convert('KV15messages', self.create_message().to_xml_delete())
        self.assertEqual(1, len(situations))
        self.assertEqual(['KV15:HTM:2013-11-16:4'], values(situations[0], 's:SituationNumber'))
        self.assertEqual(['closed'], values(situations[0], 's:Progress'))
        # Nothing more to show
        self.assertEqual(values(situations[0], 's:PublicationWindow/s:StartTime'),
                         values(situations[0], 's:PublicationWindow/s:EndTime'))

    def test_update(self):
        """ An update is a delete of the old and a new message in one push """
        situations = convert('KV15messages', get_fixture('update.xml'))
        self.assertEqual(['closed', 'open'], [values(s, 's:Progress')[0] for s in situations])
        self.assertEqual(['KV15:HTM:2013-11-16:5012', 'KV15:HTM:2013-11-16:5013'],
                         [values(s, 's:SituationNumber')[0] for s in situations])

    def test_lines(self):
        situation = convert('KV15messages', get_fixture('message_complete.xml'))[0]
        stop = situation.xpath('s:Affects/s:StopPoints/s:AffectedStopPoint', namespaces=NS)[0]
        self.assertEqual(['100'], values(stop, 's:StopPointRef'))


class TestSiriSxStopRefs(TestCase):
    """
    Stops use the CHB quay when we have one, the userstopcode if we don't. Lines use the NeTEx ref from RID, or one
    made from the lineplanningnumber
    """
    def setUp(self):
        Kv1Stop(userstopcode='100', dataownercode='HTM', name="Om de hoek", location=Point(1, 1),
                quaycoderef='NL:Q:32000100', original_ref='NL:HTM:ScheduledStopPoint:R100').save()
        Kv1Stop(userstopcode='101', dataownercode='HTM', name="De andere hoek", location=Point(1, 10),
                original_ref='NL:HTM:ScheduledStopPoint:R101').save()
        Kv1Stop(userstopcode='100', dataownercode='GVB', name="Elders", location=Point(2, 2),
                quaycoderef='NL:Q:57000100').save()
        Kv1Line(dataownercode='HTM', lineplanningnumber='1001', publiclinenumber='1', headsign="Lijn 1", stop_map=[],
                original_ref='NL:HTM:Line:1').save()

    def test_kv15(self):
        xml = get_fixture('message_basic.xml').replace('<messagetimestamp>...</messagetimestamp>', '')
        with self.assertNumQueries(1):
            situation = convert('KV15messages', xml)[0]
        self.assertEqual(['NL:CHB:Quay:32000100', '101'],
                         values(situation, 's:Affects/s:StopPoints/s:AffectedStopPoint/s:StopPointRef'))

    def test_kv15_lines(self):
        xml = get_fixture('message_basic.xml').replace('<messagetimestamp>...</messagetimestamp>', '') \
            .replace('</userstopcodes>', '</userstopcodes><lineplanningnumbers><lineplanningnumber>1001'
                                         '</lineplanningnumber><lineplanningnumber>1002</lineplanningnumber>'
                                         '</lineplanningnumbers>')
        with self.assertNumQueries(2):
            situation = convert('KV15messages', xml)[0]
        stop = situation.xpath('s:Affects/s:StopPoints/s:AffectedStopPoint', namespaces=NS)[0]
        # 1002 isn't in RID
        self.assertEqual(['NL:HTM:Line:1', 'NL:HTM:Line:1002'], values(stop, 's:Lines/s:AffectedLine/s:LineRef'))

    def test_kv17(self):
        situation = convert('KV17cvlinfo', get_fixture('kv17_mutationmessage.xml'))[0]
        journey = situation.xpath('s:Affects/s:VehicleJourneys/s:AffectedVehicleJourney', namespaces=NS)[0]
        self.assertEqual(['NL:HTM:Line:1'], values(journey, 's:LineRef'))
        self.assertEqual(['NL:CHB:Quay:32000100'], values(journey, 's:Calls/s:Call/s:StopPointRef'))
        self.assertEqual(['101'], values(journey, 's:FramedVehicleJourneyRef/s:DatedVehicleJourneyRef'))

    def test_quay_ref(self):
        self.assertEqual('NL:CHB:Quay:32000100', RefLookup.quay_ref('NL:Q:32000100'))
        # Foreign stops aren't in the CHB
        self.assertEqual('DE:Q:44140030', RefLookup.quay_ref('DE:Q:44140030'))


class TestSiriSxKv17(TestCase):
    def test_cancel(self):
        situations = convert('KV17cvlinfo', get_fixture('kv17_cancel.xml'))
        self.assertEqual(1, len(situations))
        situation = situations[0]
        self.assertEqual(['KV17:HTM:2016-04-01:1001:100'], values(situation, 's:SituationNumber'))
        self.assertEqual(['open'], values(situation, 's:Progress'))
        self.assertEqual(['Rit vervalt'], values(situation, 's:Summary'))
        journey = situation.xpath('s:Affects/s:VehicleJourneys/s:AffectedVehicleJourney', namespaces=NS)[0]
        self.assertEqual(['2016-04-01'], values(journey, 's:FramedVehicleJourneyRef/s:DataFrameRef'))
        self.assertEqual(['100'], values(journey, 's:FramedVehicleJourneyRef/s:DatedVehicleJourneyRef'))
        self.assertEqual(['NL:HTM:Line:1001'], values(journey, 's:LineRef'))
        self.assertEqual([], values(journey, 's:Calls/s:Call/s:StopPointRef'))
        consequence = situation.xpath('s:Consequences/s:Consequence', namespaces=NS)[0]
        self.assertEqual(['tripCancellation'], values(consequence, 's:Condition'))
        self.assertEqual(['100'], values(consequence, 's:Affects/s:VehicleJourneys/s:AffectedVehicleJourney/'
                                                      's:FramedVehicleJourneyRef/s:DatedVehicleJourneyRef'))

    def test_recover_closes_same_situation(self):
        cancel = convert('KV17cvlinfo', get_fixture('kv17_cancel.xml'))[0]
        recover = convert('KV17cvlinfo', get_fixture('kv17_recover.xml'))[0]
        self.assertEqual(values(cancel, 's:SituationNumber'), values(recover, 's:SituationNumber'))
        self.assertEqual(['closed'], values(recover, 's:Progress'))
        self.assertEqual([], recover.xpath('s:Consequences', namespaces=NS))

    def test_mutation_message(self):
        situation = convert('KV17cvlinfo', get_fixture('kv17_mutationmessage.xml'))[0]
        self.assertEqual(['open'], values(situation, 's:Progress'))
        self.assertEqual(['100'], values(situation, 's:Affects/s:VehicleJourneys/s:AffectedVehicleJourney/'
                                                        's:Calls/s:Call/s:StopPointRef'))
        # The journey still runs
        self.assertEqual([], situation.xpath('s:Consequences', namespaces=NS))

    def test_shorten(self):
        xml = """<KV17JOURNEY><dataownercode>HTM</dataownercode><lineplanningnumber>1001</lineplanningnumber>
        <operatingday>2016-04-01</operatingday><journeynumber>100</journeynumber><reinforcementnumber>0</reinforcementnumber>
        </KV17JOURNEY><KV17MUTATEJOURNEYSTOP><timestamp>2016-04-01T10:00:00+02:00</timestamp>
        <SHORTEN><userstopcode>100</userstopcode><passagesequencenumber>0</passagesequencenumber>
        <showcancelledtrip>true</showcancelledtrip></SHORTEN>
        <SHORTEN><userstopcode>101</userstopcode><passagesequencenumber>0</passagesequencenumber>
        <showcancelledtrip>true</showcancelledtrip></SHORTEN></KV17MUTATEJOURNEYSTOP>"""
        situation = convert('KV17cvlinfo', xml)[0]
        self.assertEqual(['Rit rijdt niet langs alle haltes'], values(situation, 's:Summary'))
        self.assertEqual(['2016-04-01T10:00:00+02:00'], values(situation, 's:CreationTime'))
        self.assertEqual(['100', '101'], values(situation, 's:Affects/s:VehicleJourneys/'
                                                                   's:AffectedVehicleJourney/s:Calls/s:Call/s:StopPointRef'))
        consequence = situation.xpath('s:Consequences/s:Consequence', namespaces=NS)[0]
        self.assertEqual(['stopCancelled'], values(consequence, 's:Condition'))
        self.assertEqual(['100', '101'], values(consequence, 's:Affects/s:VehicleJourneys/'
                                                                     's:AffectedVehicleJourney/s:Calls/s:Call/s:StopPointRef'))

    def test_shorten_and_mutation_message(self):
        """ Only the skipped stop is cancelled, the stop with a message is still served """
        xml = """<KV17JOURNEY><dataownercode>HTM</dataownercode><lineplanningnumber>1001</lineplanningnumber>
        <operatingday>2016-04-01</operatingday><journeynumber>100</journeynumber><reinforcementnumber>0</reinforcementnumber>
        </KV17JOURNEY><KV17MUTATEJOURNEYSTOP><timestamp>2016-04-01T10:00:00+02:00</timestamp>
        <SHORTEN><userstopcode>100</userstopcode><passagesequencenumber>0</passagesequencenumber>
        <showcancelledtrip>true</showcancelledtrip></SHORTEN>
        <MUTATIONMESSAGE><userstopcode>101</userstopcode><passagesequencenumber>0</passagesequencenumber>
        <reasontype>3</reasontype><subreasontype>7</subreasontype></MUTATIONMESSAGE></KV17MUTATEJOURNEYSTOP>"""
        situation = convert('KV17cvlinfo', xml)[0]
        self.assertEqual(['100', '101'], values(situation, 's:Affects/s:VehicleJourneys/'
                                                                   's:AffectedVehicleJourney/s:Calls/s:Call/s:StopPointRef'))
        self.assertEqual(['100'], values(situation, 's:Consequences/s:Consequence/s:Affects/s:VehicleJourneys/'
                                                         's:AffectedVehicleJourney/s:Calls/s:Call/s:StopPointRef'))

    def test_all_journeys_of_line(self):
        xml = """<KV17JOURNEY><dataownercode>HTM</dataownercode><allJourneysOfLine/>
        <lineplanningnumber>1001</lineplanningnumber><operatingday>2016-04-01</operatingday>
        <begintime>23:00:00</begintime><endtime>26:30:00</endtime></KV17JOURNEY>
        <KV17MUTATEJOURNEY><timestamp>2016-04-01T10:00:00+02:00</timestamp><CANCEL>
        <showcancelledtrip>true</showcancelledtrip><autorecover>false</autorecover></CANCEL></KV17MUTATEJOURNEY>"""
        situation = convert('KV17cvlinfo', xml)[0]
        self.assertEqual(['KV17:HTM:2016-04-01:1001:ALL:23:00:00'], values(situation, 's:SituationNumber'))
        self.assertEqual(['2016-04-01T23:00:00+02:00'], values(situation, 's:ValidityPeriod/s:StartTime'))
        self.assertEqual(['2016-04-02T02:30:00+02:00'], values(situation, 's:ValidityPeriod/s:EndTime'))
        self.assertEqual(['NL:HTM:Line:1001'], values(situation, 's:Affects/s:Networks/s:AffectedNetwork/'
                                                                     's:AffectedLine/s:LineRef'))
        self.assertEqual(['NL:HTM:Line:1001'], values(situation, 's:Consequences/s:Consequence/s:Affects/s:Networks/'
                                                                     's:AffectedNetwork/s:AffectedLine/s:LineRef'))
        self.assertEqual(['lineCancellation'], values(situation, 's:Consequences/s:Consequence/s:Condition'))

    def test_all_lines(self):
        xml = """<KV17JOURNEY><dataownercode>HTM</dataownercode><allLines/><operatingday>2016-04-01</operatingday>
        </KV17JOURNEY><KV17MUTATEJOURNEY><timestamp>2016-04-01T10:00:00+02:00</timestamp><CANCEL>
        <showcancelledtrip>true</showcancelledtrip><autorecover>false</autorecover></CANCEL></KV17MUTATEJOURNEY>"""
        situation = convert('KV17cvlinfo', xml)[0]
        self.assertEqual(['KV17:HTM:2016-04-01:ALL'], values(situation, 's:SituationNumber'))
        self.assertEqual(['discontinuedOperation'], values(situation, 's:Consequences/s:Consequence/s:Condition'))
        self.assertEqual(['NL:BISON:Codespace:HTM'], values(situation, 's:Affects/s:Operators/s:AffectedOperator/'
                                                                           's:OperatorRef'))
        self.assertEqual(['NL:BISON:Codespace:HTM'], values(situation, 's:Consequences/s:Consequence/s:Affects/'
                                                                           's:Operators/s:AffectedOperator/s:OperatorRef'))

    def test_multiple_journeys(self):
        """ Batch commands send a list of changes in one push """
        situations = convert('KV17cvlinfo', [get_fixture('kv17_cancel.xml'), get_fixture('kv17_reason_basic.xml')])
        self.assertEqual(2, len(situations))

    def test_not_monitored(self):
        xml = """<KV17JOURNEY><dataownercode>HTM</dataownercode><lineplanningnumber>1001</lineplanningnumber>
        <operatingday>2016-04-01</operatingday><journeynumber>100</journeynumber><reinforcementnumber>0</reinforcementnumber>
        </KV17JOURNEY><KV17MUTATEJOURNEY><timestamp>2016-04-01T10:00:00+02:00</timestamp>
        <NOTMONITORED><monitoringerror>GPS</monitoringerror></NOTMONITORED></KV17MUTATEJOURNEY>"""
        self.assertIsNone(to_siri_sx('KV17cvlinfo', xml, 'openebs'))

    def test_delivery(self):
        siri = etree.fromstring(to_siri_sx('KV17cvlinfo', get_fixture('kv17_cancel.xml'), 'openebs'))
        self.assertEqual(['NL:HTM'], values(siri, 's:ServiceDelivery/s:ProducerRef'))
        self.assertEqual(1, len(siri.xpath('s:ServiceDelivery/s:SituationExchangeDelivery/s:Situations/'
                                           's:PtSituationElement', namespaces=NS)))

    def test_delivery_several_operators(self):
        """ There's no one producer, so use the configured one """
        other = get_fixture('kv17_reason_basic.xml').replace('>HTM<', '>GVB<')
        siri = etree.fromstring(to_siri_sx('KV17cvlinfo', [get_fixture('kv17_cancel.xml'), other], 'openebs'))
        self.assertEqual(['openebs'], values(siri, 's:ServiceDelivery/s:ProducerRef'))



class TestSiriSxReasons(TestCase):
    """ The KV subreasontype gives the AlertCause, and the reasontype only where a code means several things """
    def test_alert_cause(self):
        self.assertEqual('roadworks', _alert_cause('1', '23_2'))
        # The UI has one list of subreasons, so a code with one meaning doesn't depend on the reasontype
        self.assertEqual('congestion', _alert_cause('3', '15'))
        # 4 is Brand, Tekort aan personeel or Seinstoring
        self.assertEqual('fire', _alert_cause('1', '4'))
        self.assertEqual('staffAbsence', _alert_cause('2', '4'))
        self.assertEqual('signalFailure', _alert_cause('3', '4'))
        # 255 is Onbekend, or Weersomstandigheden for the environment
        self.assertEqual('poorWeather', _alert_cause('4', '255'))
        self.assertEqual('unknown', _alert_cause('2', '255'))
        # Events without a PublicEventReason are still events
        self.assertEqual('specialEvent', _alert_cause('1', '24_99'))
        # Unknown codes fall back on the reasontype, without the deprecated undefined...Problem values
        self.assertEqual('miscellaneous', _alert_cause('1', '99'))
        self.assertEqual('technicalProblem', _alert_cause('3', None))
        self.assertEqual('unknown', _alert_cause('2', None))
        self.assertEqual('unknown', _alert_cause(None, None))

    def test_event(self):
        """ Wielerronde """
        situation = convert('KV17cvlinfo', get_fixture('kv17_reason_basic.xml'))[0]
        self.assertEqual(['specialEvent'], values(situation, 's:AlertCause'))
        self.assertEqual(['bicycleRace'], values(situation, 's:PublicEventReason'))
        self.assertEqual(['true'], values(situation, 's:Planned'))

    def test_mutation_message(self):
        """ Defect materieel """
        situation = convert('KV17cvlinfo', get_fixture('kv17_mutationmessage.xml'))[0]
        self.assertEqual(['breakDown'], values(situation, 's:AlertCause'))
        self.assertEqual([], values(situation, 's:PublicEventReason'))
        self.assertEqual(['false'], values(situation, 's:Planned'))


PUSH_SETTINGS_SIRI_SX = [
    {'alias': 'first',
     'enabled': True,
     'priority': 1,
     'failOnFailure': False,
     'host': 'localhost',
     'subscriberName': 'openov',
     'endpoints': {
         'KV6': {'path': '/KV6'},
         'KV15': {'path': '/KV15'},
         'KV17': {'path': '/KV17'},
         'SIRI-SX': {},
     }},
    {'alias': 'second',
     'enabled': True,
     'priority': 2,
     'failOnFailure': False,
     'host': 'localhost',
     'subscriberName': 'openov',
     'endpoints': {
         'KV6': {'path': '/KV6'},
         'KV15': {'path': '/KV15'},
         'KV17': {'path': '/KV17'},
     }},
]

KV_OK = (200, '<tmi8:ResponseCode>OK</tmi8:ResponseCode>')


@override_settings(PUSH_SETTINGS=PUSH_SETTINGS_SIRI_SX)
class TestSiriSxPush(TestCase):
    def push(self, mixin, responses):
        """ Push the cancel fixture, answering each post in turn, and return the posted endpoints """
        posted = []

        def post(pusher, content):
            posted.append(pusher.endpoint)
            return responses.pop(0)

        with mock.patch.object(Push, 'post', autospec=True, side_effect=post):
            success = mixin.push_message(get_fixture('kv17_cancel.xml'))
        return success, posted

    def test_pushers(self):
        pushers = Kv17PushMixin().pushers
        self.assertIsInstance(pushers[0].siri_sx, SiriSxPush)
        self.assertEqual('/OPENOV/SituationExchangeDelivery', pushers[0].siri_sx.endpoint)
        self.assertIsNone(pushers[1].siri_sx)
        self.assertIsNotNone(Kv15PushMixin().pushers[0].siri_sx)
        self.assertIsNone(Kv6PushMixin().pushers[0].siri_sx)

    def test_push(self):
        success, posted = self.push(Kv17PushMixin(), [KV_OK, (200, ''), KV_OK])
        self.assertTrue(success)
        self.assertEqual(['/KV17', '/OPENOV/SituationExchangeDelivery', '/KV17'], posted)

    def test_push_siri_sx_failure_continues(self):
        success, posted = self.push(Kv17PushMixin(), [KV_OK, (500, 'Error'), KV_OK])
        self.assertTrue(success)
        self.assertEqual(['/KV17', '/OPENOV/SituationExchangeDelivery', '/KV17'], posted)

    def test_push_siri_sx_status_false(self):
        mixin = Kv17PushMixin()
        mixin.pushers[0].siri_sx.fail_on_failure = True
        success, posted = self.push(mixin, [KV_OK, (200, '<siri:Status>false</siri:Status>')])
        self.assertFalse(success)
        self.assertEqual(['/KV17', '/OPENOV/SituationExchangeDelivery'], posted)

    def test_push_siri_sx_conversion_error(self):
        mixin = Kv17PushMixin()
        with mock.patch('utils.push.to_siri_sx', side_effect=ValueError("Broken")):
            success, posted = self.push(mixin, [KV_OK, KV_OK])
        self.assertTrue(success)
        self.assertEqual(['/KV17', '/KV17'], posted)
