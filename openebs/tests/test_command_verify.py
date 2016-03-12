from datetime import timedelta, datetime
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.test import TestCase
from django.utils.timezone import now
from kv1.models import Kv1Stop
from openebs.management.commands.verify_messages import Command as VerifyCommand
from openebs.models import Kv15Stopmessage, MessageStatus, Kv15MessageStop


class TestKv8Verify(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestKv8Verify, cls).setUpClass()
        cls.testClass = VerifyCommand()
        cls.user = User.objects.create_user("test_kv8")

        # Create two fake sotps
        stop_a = Kv1Stop(userstopcode=400, dataownercode='HTM', timingpointcode=400, name="Om de ene hoek", location=Point(1, 1))
        stop_b = Kv1Stop(userstopcode=401, dataownercode='HTM', timingpointcode=401, name="Om de ander hoek", location=Point(1, 1))
        stop_c = Kv1Stop(userstopcode=402, dataownercode='HTM', timingpointcode=3000402, name="In Lutjebroek", location=Point(1, 1))
        stop_a.save()
        stop_b.save()
        stop_c.save()

    def test_message_verify_basic(self):
        """
        Test whether updating an existing message from KV8 works - the status must be updated
        """
        a = Kv15Stopmessage(dataownercode='HTM', user=self.user, messagecodedate=now().date(), messagecodenumber=24)
        a.save()
        stop = Kv15MessageStop(stopmessage=a, stop=Kv1Stop.objects.get(userstopcode=400))
        stop.save()
        self.assertEqual(a.status, MessageStatus.SAVED)
        self.assertEqual(a.stops.count(), 1)

        count = Kv15Stopmessage.objects.count()

        row = {
            'DataOwnerCode': 'HTM',
            'TimingPointCode': 400,
            'MessageCodeDate': now().date().isoformat(),
            'MessageStartTime': now(),
            'MessageEndTime': now()+timedelta(hours=2),
            'MessageCodeNumber': '24'
        }

        # Method under test
        self.testClass.process_message(row, False)

        a = Kv15Stopmessage.objects.get(pk=a.pk) # Get latest from db
        self.assertEqual(a.status, MessageStatus.CONFIRMED)
        self.assertEqual(a.user.username, self.user.username)
        self.assertEqual(a.stops.count(), 1)

        # No new messages created - check count
        self.assertEqual(Kv15Stopmessage.objects.count(), count)

    def test_message_add_basic(self):
        """
        Test whether adding a message from KV8 works - all the fields must be transferred across
        """
        count = Kv15Stopmessage.objects.count()
        row = {
            'DataOwnerCode': 'HTM',
            'TimingPointCode': 400,
            'MessageCodeDate': now().date().isoformat(),
            'MessageCodeNumber': '25',
            'MessageContent': "Test content",
            'MessageStartTime': now(),
            'MessageEndTime': now()+timedelta(hours=2),
            'MessageTimeStamp': now(),
            'MessageType': 'GENERAL',
            'MessageDurationType': 'ENDTIME',
            'ReasonType': 1,
            'SubReasonType': '11',
            'ReasonContent': "uitleg reden",
            'EffectType': 1,
            'SubEffectType': '11',
            'EffectContent': "uitleg effect",
            'MeasureType': 1,
            'SubMeasureType': '1',
            'MeasureContent': "uitleg maatregel",
            'AdviceType': 1,
            'SubAdviceType': '1',
            'AdviceContent': "uitleg afvies"
        }

        # Method under test
        self.testClass.process_message(row, False)

        self.assertEqual(Kv15Stopmessage.objects.count(), count+1)
        msg = Kv15Stopmessage.objects.get(dataownercode='HTM', messagecodedate=now().date(), messagecodenumber=25)
        self.assertEqual(msg.messagecontent, row['MessageContent'])
        self.assertEqual(msg.messagestarttime, row['MessageStartTime'])
        self.assertEqual(msg.messageendtime, row['MessageEndTime'])
        self.assertEqual(msg.messagetimestamp, row['MessageTimeStamp'])
        self.assertEqual(msg.messagetype, row['MessageType'])
        self.assertEqual(msg.messagedurationtype, row['MessageDurationType'])
        self.assertEqual(msg.reasontype, row['ReasonType'])
        self.assertEqual(msg.subreasontype, row['SubReasonType'])
        self.assertEqual(msg.reasoncontent, row['ReasonContent'])
        self.assertEqual(msg.effecttype, row['EffectType'])
        self.assertEqual(msg.subeffecttype, row['SubEffectType'])
        self.assertEqual(msg.effectcontent, row['EffectContent'])
        self.assertEqual(msg.measuretype, row['MeasureType'])
        self.assertEqual(msg.submeasuretype, row['SubMeasureType'])
        self.assertEqual(msg.measurecontent, row['MeasureContent'])
        self.assertEqual(msg.advicetype, row['AdviceType'])
        self.assertEqual(msg.subadvicetype, row['SubAdviceType'])
        self.assertEqual(msg.advicecontent, row['AdviceContent'])
        self.assertEqual(msg.status, MessageStatus.CONFIRMED)
        self.assertEqual(msg.user.username, 'kv8update')
        self.assertEqual(len(msg.stops.all()), 1)
        self.assertEqual(msg.stops.all()[0].userstopcode, '400')

    def test_message_add_multiple(self):
        """
        Test a message with lots of stops
        """
        count = Kv15Stopmessage.objects.count()
        row = {
            'DataOwnerCode': 'HTM',
            'TimingPointCode': 400,
            'MessageCodeDate': now().date().isoformat(),
            'MessageCodeNumber': '37',
            'MessageContent': "Test content",
            'MessageStartTime': now(),
            'MessageEndTime': now()+timedelta(hours=2),
            'MessageTimeStamp': now(),
            'MessageType': 'GENERAL',
            'MessageDurationType': 'ENDTIME',
            'ReasonType': 1,
            'SubReasonType': '11',
            'ReasonContent': "uitleg reden",
            'EffectType': 1,
            'SubEffectType': '11',
            'EffectContent': "uitleg effect",
            'MeasureType': 1,
            'SubMeasureType': '1',
            'MeasureContent': "uitleg maatregel",
            'AdviceType': 1,
            'SubAdviceType': '1',
            'AdviceContent': "uitleg afvies"
        }

        # Method under test
        self.testClass.process_message(row, False)
        row['TimingPointCode'] = 401
        self.testClass.process_message(row, False)
        row['TimingPointCode'] = 3000402
        self.testClass.process_message(row, False)

        self.assertEqual(Kv15Stopmessage.objects.count(), count+1)
        msg = Kv15Stopmessage.objects.get(dataownercode='HTM', messagecodedate=now().date(), messagecodenumber=37)

        self.assertEqual(len(msg.stops.all()), 3)
        self.assertEqual(msg.stops.all()[0].userstopcode, '400')
        self.assertEqual(msg.stops.all()[1].userstopcode, '401')
        self.assertEqual(msg.stops.all()[2].userstopcode, '402')

    def test_message_add_multiple_dataowners(self):
        """
        Now we have proper support for TPC, check we can have message with two linked stops
        """

        stop_d = Kv1Stop(userstopcode=403, dataownercode='HTM', timingpointcode=3000403, name="In Lutjebroek", location=Point(1, 1))
        stop_e = Kv1Stop(userstopcode=999, dataownercode='VTN', timingpointcode=3000403, name="In Lutjebrk", location=Point(1, 1))
        stop_d.save()
        stop_e.save()

        count = Kv15Stopmessage.objects.count()
        row = {
            'DataOwnerCode': 'HTM',
            'TimingPointCode': 3000403,
            'MessageCodeDate': now().date().isoformat(),
            'MessageCodeNumber': '50',
            'MessageContent': "Test content some more for two vervoerders",
            'MessageStartTime': now(),
            'MessageEndTime': now()+timedelta(hours=2),
            'MessageTimeStamp': now(),
            'MessageType': 'GENERAL',
            'MessageDurationType': 'ENDTIME',
            'ReasonType': 1,
            'SubReasonType': '11',
            'ReasonContent': "uitleg reden",
            'EffectType': 1,
            'SubEffectType': '11',
            'EffectContent': "uitleg effect",
            'MeasureType': 1,
            'SubMeasureType': '1',
            'MeasureContent': "uitleg maatregel",
            'AdviceType': 1,
            'SubAdviceType': '1',
            'AdviceContent': "uitleg afvies"
        }

        # Method under test
        self.testClass.process_message(row, False)

        self.assertEqual(Kv15Stopmessage.objects.count(), count+1)
        msg = Kv15Stopmessage.objects.get(dataownercode='HTM', messagecodedate=now().date(), messagecodenumber=50)

        self.assertEqual(len(msg.stops.all()), 2)
        self.assertEqual(msg.stops.all()[0].userstopcode, '403')
        self.assertEqual(msg.stops.all()[0].dataownercode, 'HTM')
        self.assertEqual(msg.stops.all()[1].userstopcode, '999')
        self.assertEqual(msg.stops.all()[1].dataownercode, 'VTN')


    def test_message_add_some_missing(self):
        """
        Test whether adding a message from KV8 works - all the fields must be transferred across but some are empty
        """
        count = Kv15Stopmessage.objects.count()
        row = {
            'DataOwnerCode': 'HTM',
            'TimingPointCode': 400,
            'MessageCodeDate': now().date().isoformat(),
            'MessageCodeNumber': '26',
            'MessageContent': "Test content",
            'MessageStartTime': now(),
            'MessageEndTime': now()+timedelta(hours=2),
            'MessageTimeStamp': now(),
            'MessageType': 'GENERAL',
            'MessageDurationType': 'ENDTIME',
            'ReasonType': None,
            'SubReasonType': '',
            'ReasonContent': '',
            'EffectType': 1,
            'SubEffectType': '',
            'EffectContent': '',
            'MeasureType': 1,
            'SubMeasureType': '1',
            'MeasureContent': '',
            'AdviceType': 1,
            'SubAdviceType': '1',
            'AdviceContent': "uitleg advies"
        }

        # Method under test
        self.testClass.process_message(row, False)

        self.assertEqual(Kv15Stopmessage.objects.count(), count+1)
        msg = Kv15Stopmessage.objects.get(dataownercode='HTM', messagecodedate=now().date(), messagecodenumber=26)
        self.assertEqual(msg.messagecontent, row['MessageContent'])
        self.assertEqual(msg.messagestarttime, row['MessageStartTime'])
        self.assertEqual(msg.messageendtime, row['MessageEndTime'])
        self.assertEqual(msg.messagetimestamp, row['MessageTimeStamp'])
        self.assertEqual(msg.messagetype, row['MessageType'])
        self.assertEqual(msg.messagedurationtype, row['MessageDurationType'])
        self.assertEqual(msg.reasontype, row['ReasonType'])
        self.assertEqual(msg.subreasontype, row['SubReasonType'])
        self.assertEqual(msg.reasoncontent, row['ReasonContent'])
        self.assertEqual(msg.effecttype, row['EffectType'])
        self.assertEqual(msg.subeffecttype, row['SubEffectType'])
        self.assertEqual(msg.effectcontent, row['EffectContent'])
        self.assertEqual(msg.measuretype, row['MeasureType'])
        self.assertEqual(msg.submeasuretype, row['SubMeasureType'])
        self.assertEqual(msg.measurecontent, row['MeasureContent'])
        self.assertEqual(msg.advicetype, row['AdviceType'])
        self.assertEqual(msg.subadvicetype, row['SubAdviceType'])
        self.assertEqual(msg.advicecontent, row['AdviceContent'])
        self.assertEqual(msg.status, MessageStatus.CONFIRMED)
        self.assertEqual(msg.user.username, 'kv8update')
        self.assertEqual(len(msg.stops.all()), 1)
        self.assertEqual(msg.stops.all()[0].userstopcode, '400')

    def test_message_deleted(self):
        """
        Test an already deleted message is marked as such, and the end time is about now
        """
        a = Kv15Stopmessage(dataownercode='HTM', user=self.user, messagecodedate=datetime(2013, 11, 17),
                            messagecodenumber=30)
        a.save()
        a.delete()
        a.set_status(MessageStatus.DELETED)
        a = Kv15Stopmessage.objects.get(pk=a.pk) # Get latest from db
        self.assertEqual(a.status, MessageStatus.DELETED)
        self.assertEqual(a.isdeleted, True)

        row = {
            'DataOwnerCode': 'HTM',
            'TimingPointCode': 400,
            'MessageCodeDate': '2013-11-17',
            'MessageCodeNumber': '30'
        }
        # Method under test
        self.testClass.process_message(row, True)

        a = Kv15Stopmessage.objects.get(pk=a.pk) # Get latest from db
        self.assertEqual(a.status, MessageStatus.DELETE_CONFIRMED)
        self.assertLess((now() - a.messageendtime), timedelta(seconds=30), "Time wasn't set right")
        self.assertEqual(len(a.stops.all()), 1)
        self.assertEqual(a.stops.all()[0].userstopcode, '400')

    def test_message_deletion(self):
        """
        Test a message that was deleted
        """
        a = Kv15Stopmessage(dataownercode='HTM', user=self.user, messagecodedate=datetime(2013, 11, 17), messagecodenumber=31)
        a.save()
        self.assertEqual(a.status, MessageStatus.SAVED)
        self.assertEqual(a.isdeleted, False)

        count = Kv15Stopmessage.objects.count()

        row = {
            'DataOwnerCode': 'HTM',
            'TimingPointCode': 400,
            'MessageCodeDate': '2013-11-17',
            'MessageCodeNumber': '31'
        }
        # Method under test
        self.testClass.process_message(row, True)

        a = Kv15Stopmessage.objects.get(pk=a.pk) # Get latest from db
        self.assertEqual(a.status, MessageStatus.DELETE_CONFIRMED)
        self.assertEqual(a.isdeleted, True)
        self.assertLess((now() - a.messageendtime), timedelta(seconds=30), "Time wasn't set right")
        self.assertEqual(len(a.stops.all()), 1)
        self.assertEqual(a.stops.all()[0].userstopcode, '400')


    def test_message_deletion_unknown(self):
        """
        Test a message that was previously unknown but is now deleted
        """

        count = Kv15Stopmessage.objects.count()

        row = {
            'DataOwnerCode': 'HTM',
            'TimingPointCode': 400,
            'MessageCodeDate': '2013-11-17',
            'MessageCodeNumber': '38'
        }
        # Method under test
        self.testClass.process_message(row, True)

        a = Kv15Stopmessage.objects.get(messagecodenumber=38)
        self.assertEqual(a.status, MessageStatus.DELETE_CONFIRMED)
        self.assertEqual(a.isdeleted, True)
        self.assertLess((now() - a.messageendtime), timedelta(seconds=30), "Time wasn't set right")
        self.assertEqual(len(a.stops.all()), 1)
        self.assertEqual(a.stops.all()[0].userstopcode, '400')

    def test_message_deletion_multiple(self):
        """
        Test a message that was deleted, with multiple stops (one row per stop)
        """
        messagecodenumber = 36
        a = Kv15Stopmessage(dataownercode='HTM',
                            user=self.user,
                            messagecodedate=datetime(2013, 11, 17),
                            messagecodenumber=messagecodenumber)
        a.save()
        self.assertEqual(a.status, MessageStatus.SAVED)
        self.assertEqual(a.isdeleted, False)
        self.assertEqual(len(a.stops.all()), 0)

        row = {
            'DataOwnerCode': 'HTM',
            'TimingPointCode': 400,
            'MessageCodeDate': '2013-11-17',
            'MessageCodeNumber': str(messagecodenumber)
        }
        # Method under test
        self.testClass.process_message(row, True)
        row['TimingPointCode'] = 401
        self.testClass.process_message(row, True)

        a = Kv15Stopmessage.objects.get(pk=a.pk) # Get latest from db
        self.assertEqual(a.status, MessageStatus.DELETE_CONFIRMED)
        self.assertEqual(a.isdeleted, True)
        self.assertLess((now() - a.messageendtime), timedelta(seconds=30), "Time wasn't set right")
        self.assertEqual(len(a.stops.all()), 2)
        self.assertEqual(a.stops.all()[0].userstopcode, '400')
        self.assertEqual(a.stops.all()[1].userstopcode, '401')


    def test_message_update(self):
        """
        When we update a message, it sends a delete followed by an update - check that works
        """
        a = Kv15Stopmessage(dataownercode='HTM', user=self.user, messagecodedate=now().date(), messagecodenumber=32)
        a.messagecontent = "Bla!"
        a.status = MessageStatus.CONFIRMED
        a.save()

        # Update it!
        a.messagecontent = "Bla!"
        a.save()

        delete_row = {
            'DataOwnerCode': 'HTM',
            'TimingPointCode': 400,
            'MessageCodeDate': now().date().isoformat(),
            'MessageCodeNumber': '32'
        }
        add_row = {
            'DataOwnerCode': 'HTM',
            'TimingPointCode': 401,
            'MessageCodeDate': now().date().isoformat(),
            'MessageStartTime': now(),
            'MessageEndTime': now()+timedelta(hours=2),
            'MessageCodeNumber': '32'
        }
        # Method under test
        self.testClass.process_message(delete_row, True)
        self.testClass.process_message(add_row, False)

        a = Kv15Stopmessage.objects.get(pk=a.pk) # Get latest from db
        self.assertEqual(a.status, MessageStatus.CONFIRMED)
        self.assertEqual(a.isdeleted, False)

        self.assertLess(add_row['MessageStartTime']-a.messagestarttime, timedelta(seconds=240))
        self.assertLess(add_row['MessageEndTime']-a.messageendtime, timedelta(seconds=240))

    def test_message_overrule_message(self):
        """
        Test whether adding a message from KV8 works - all the fields must be transferred across
        See bug #80
        """
        count = Kv15Stopmessage.objects.count()
        row = {
            'DataOwnerCode' : 'HTM',
            'TimingPointCode': 400,
            'MessageCodeDate': now().date().isoformat(),
            'MessageCodeNumber': '35',
            'MessageContent': None,
            'MessageStartTime': now(),
            'MessageEndTime': now()+timedelta(hours=2),
            'MessageTimeStamp': now(),
            'MessageType': 'OVERRULE',
            'MessageDurationType': 'ENDTIME',
            'ReasonType': 1,
            'SubReasonType': '11',
            'ReasonContent': "uitleg reden",
            'EffectType': 1,
            'SubEffectType': '11',
            'EffectContent': "uitleg effect",
            'MeasureType': 1,
            'SubMeasureType': '1',
            'MeasureContent': "uitleg maatregel",
            'AdviceType': 1,
            'SubAdviceType': '1',
            'AdviceContent': "uitleg afvies"
        }

        # Method under test
        self.testClass.process_message(row, False)

        self.assertEqual(Kv15Stopmessage.objects.count(), count+1)
        msg = Kv15Stopmessage.objects.get(dataownercode='HTM', messagecodedate=now().date(), messagecodenumber=35)
        self.assertEqual(msg.messagecontent, row['MessageContent'])
        self.assertEqual(msg.messagestarttime, row['MessageStartTime'])
        self.assertEqual(msg.messageendtime, row['MessageEndTime'])
        self.assertEqual(msg.messagetimestamp, row['MessageTimeStamp'])
        self.assertEqual(msg.messagetype, row['MessageType'])
        self.assertEqual(msg.messagedurationtype, row['MessageDurationType'])
        self.assertEqual(msg.reasontype, row['ReasonType'])
        self.assertEqual(msg.subreasontype, row['SubReasonType'])
        self.assertEqual(msg.reasoncontent, row['ReasonContent'])
        self.assertEqual(msg.effecttype, row['EffectType'])
        self.assertEqual(msg.subeffecttype, row['SubEffectType'])
        self.assertEqual(msg.effectcontent, row['EffectContent'])
        self.assertEqual(msg.measuretype, row['MeasureType'])
        self.assertEqual(msg.submeasuretype, row['SubMeasureType'])
        self.assertEqual(msg.measurecontent, row['MeasureContent'])
        self.assertEqual(msg.advicetype, row['AdviceType'])
        self.assertEqual(msg.subadvicetype, row['SubAdviceType'])
        self.assertEqual(msg.advicecontent, row['AdviceContent'])
        self.assertEqual(msg.status, MessageStatus.CONFIRMED)
        self.assertEqual(msg.user.username, 'kv8update')
        self.assertEqual(len(msg.stops.all()), 1)
        self.assertEqual(msg.stops.all()[0].userstopcode, '400')