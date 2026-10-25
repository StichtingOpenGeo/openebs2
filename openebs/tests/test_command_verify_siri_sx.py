from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.test import TestCase, override_settings

from kv1.models import Kv1Stop
from openebs.management.commands.verify_messages import Command as VerifyCommand
from openebs.models import Kv15Stopmessage, Kv15MessageStop
from utils.siri_sx import SIRI_NAMESPACE, convert
from utils.views import ExternalMessagePushMixin

NS = {'s': SIRI_NAMESPACE}

COLUMNS = ['DataOwnerCode', 'MessageCodeDate', 'MessageCodeNumber', 'TimingPointDataOwnerCode', 'TimingPointCode',
           'QuayCode', 'OriginalMessageCodeDate', 'OriginalMessageCodeNumber', 'MessageType', 'MessageDurationType',
           'MessageStartTime', 'MessageEndTime', 'MessageContent', 'MessageTimeStamp', 'ReasonType', 'SubReasonType',
           'ReasonContent', 'EffectType', 'SubEffectType', 'EffectContent', 'MeasureType', 'SubMeasureType',
           'MeasureContent', 'AdviceType', 'SubAdviceType', 'AdviceContent']


def packet(message_type, rows):
    """ A KV78turbo packet as it comes from the feed, with a row per stop of a message """
    lines = ["\\GKV8turbo_generalmessages|KV8turbo_generalmessages|openOV|||UTF-8|0.1|2026-10-25T10:00:00+01:00|",
             "\\T%s|%s|start object" % (message_type, message_type),
             "\\L" + "|".join(COLUMNS)]
    for row in rows:
        lines.append("|".join(row.get(column, '\\0') for column in COLUMNS))
    return "\r\n".join(lines) + "\r\n"


def row(quay, number='5001', kv8_number='9001'):
    return {'DataOwnerCode': 'HTM', 'MessageCodeDate': '2026-10-25', 'MessageCodeNumber': kv8_number,
            'TimingPointDataOwnerCode': 'ALGEMEEN', 'TimingPointCode': '32000100', 'QuayCode': quay,
            'OriginalMessageCodeDate': '2026-10-25', 'OriginalMessageCodeNumber': number, 'MessageType': 'GENERAL',
            'MessageDurationType': 'ENDTIME', 'MessageStartTime': '2026-10-25T10:00:00+01:00',
            'MessageEndTime': '2026-10-25T18:00:00+01:00', 'MessageContent': "Halte verplaatst",
            'MessageTimeStamp': '2026-10-25T09:59:00+01:00', 'ReasonType': '1', 'SubReasonType': '23_2',
            'ReasonContent': "Wegwerkzaamheden"}


class TestVerifySiriSx(TestCase):
    """ Messages imported from the KV78turbo feed are pushed as SIRI-SX, once per packet """
    def setUp(self):
        Kv1Stop(userstopcode='100', dataownercode='HTM', name="Om de hoek", location=Point(1, 1),
                quaycoderef='NL:Q:32000100').save()
        Kv1Stop(userstopcode='101', dataownercode='HTM', name="De andere hoek", location=Point(1, 10),
                quaycoderef='NL:Q:32000101').save()
        self.command = VerifyCommand()
        self.command.siri_sx_pushers = [Mock(alias='mock')]

    def receive(self, message_type, rows):
        with patch.object(ExternalMessagePushMixin, 'push_siri_sx', return_value=True) as push:
            self.command.parse_message(packet(message_type, rows))
            self.command.push_imported()
        return push

    def test_imported_message(self):
        push = self.receive('GENERALMESSAGEUPDATE', [row('NL:Q:32000100'), row('NL:Q:32000101')])
        # Once for the whole message, not per stop
        self.assertEqual(1, push.call_count)
        situation = convert('KV15messages', push.call_args[0][1])[0]
        self.assertEqual(['KV15:HTM:2026-10-25:5001'], [e.text for e in situation.xpath('s:SituationNumber',
                                                                                         namespaces=NS)])
        self.assertEqual(['NL:CHB:Quay:32000100', 'NL:CHB:Quay:32000101'],
                         [e.text for e in situation.xpath('s:Affects/s:StopPoints/s:AffectedStopPoint/s:StopPointRef',
                                                          namespaces=NS)])
        self.assertEqual(['roadworks'], [e.text for e in situation.xpath('s:AlertCause', namespaces=NS)])

    def test_own_message(self):
        """ Made in OpenEBS, so already pushed as SIRI-SX """
        message = Kv15Stopmessage(dataownercode='HTM', user=User.objects.create_user("test"),
                                  messagecodedate='2026-10-25', messagecodenumber=5001, messagecontent="Eigen bericht")
        message.save()
        Kv15MessageStop(stopmessage=message, stop=Kv1Stop.objects.get(userstopcode='100')).save()
        push = self.receive('GENERALMESSAGEUPDATE', [row('NL:Q:32000100')])
        self.assertEqual(0, push.call_count)

    def test_delete(self):
        self.receive('GENERALMESSAGEUPDATE', [row('NL:Q:32000100')])
        push = self.receive('GENERALMESSAGEDELETE', [row('NL:Q:32000100')])
        self.assertEqual(1, push.call_count)
        situation = convert('KV15messages', push.call_args[0][1])[0]
        self.assertEqual(['KV15:HTM:2026-10-25:5001'], [e.text for e in situation.xpath('s:SituationNumber',
                                                                                         namespaces=NS)])
        self.assertEqual(['closed'], [e.text for e in situation.xpath('s:Progress', namespaces=NS)])

    def test_delete_unknown(self):
        """ Nothing to close if we never had it """
        push = self.receive('GENERALMESSAGEDELETE', [row('NL:Q:32000100')])
        self.assertEqual(0, push.call_count)

    def test_unknown_stops(self):
        push = self.receive('GENERALMESSAGEUPDATE', [row('NL:Q:99999999')])
        self.assertEqual(0, push.call_count)

    def test_off(self):
        """ Without SIRI-SX pushers nothing is remembered or pushed """
        self.command.siri_sx_pushers = []
        push = self.receive('GENERALMESSAGEUPDATE', [row('NL:Q:32000100')])
        self.assertEqual(0, push.call_count)
        self.assertEqual({}, self.command.imported)

    @override_settings(PUSH_SETTINGS=[
        {'alias': 'with', 'enabled': True, 'priority': 1, 'host': 'localhost', 'subscriberName': 'openov',
         'endpoints': {'KV15': {'path': '/KV15'}, 'SIRI-SX': {}}},
        {'alias': 'without', 'enabled': True, 'priority': 2, 'host': 'localhost', 'subscriberName': 'openov',
         'endpoints': {'KV15': {'path': '/KV15'}}},
    ])
    def test_pushers(self):
        """ Only the SIRI-SX endpoints, we don't push the KV15 back """
        pushers = VerifyCommand.get_siri_sx_pushers()
        self.assertEqual(['with (SIRI-SX)'], [p.alias for p in pushers])
