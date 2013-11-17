from datetime import timedelta, datetime
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils.unittest.case import TestCase
from openebs.management.commands.verify_messages import Command as VerifyCommand
from openebs.models import Kv15Stopmessage, MessageStatus


class TestKv8Verify(TestCase):

    @classmethod
    def setUpClass(self):
        self.testClass = VerifyCommand()
        self.user = User.objects.create_user("test_kv8")

    def test_message_verify_basic(self):
        """
        Test whether updating an existing message from KV8 works - the status must be updated
        """
        a = Kv15Stopmessage(dataownercode='HTM', user=self.user, messagecodedate=datetime(2013, 11, 17), messagecodenumber=24 )
        a.save()
        self.assertEqual(a.status, MessageStatus.SAVED)

        count = Kv15Stopmessage.objects.count()

        row = {
            'DataOwnerCode' : 'HTM',
            'MessageCodeDate' : '2013-11-17',
            'MessageCodeNumber' : '24'
        }

        # Method under test
        self.testClass.processMessage(row)

        a = Kv15Stopmessage.objects.get(pk=a.pk) # Get latest from db
        self.assertEqual(a.status, MessageStatus.CONFIRMED)
        self.assertEqual(a.user.username, self.user.username)
        # No new messages created - check count
        self.assertEqual(Kv15Stopmessage.objects.count(), count)

    def test_message_add_basic(self):
        """
        Test whether adding a message from KV8 works - all the fields must be transferred across
        """
        count = Kv15Stopmessage.objects.count()
        row = {
            'DataOwnerCode' : 'HTM',
            'MessageCodeDate' : now().date().isoformat(),
            'MessageCodeNumber' : '25',
            'MessageContent' : "Test content",
            'MessageStartTime' : now(),
            'MessageEndTime' : now()+timedelta(hours=2),
            'MessageTimeStamp' : now(),
            'MessageType' : 'GENERAL',
            'MessageDurationType' : 'ENDTIME',
            'ReasonType' : 1,
            'SubReasonType': '11',
            'ReasonContent' : "uitleg reden",
            'EffectType' : 1,
            'SubEffectType': '11',
            'EffectContent' : "uitleg effect",
            'MeasureType' : 1,
            'SubMeasureType' : '1',
            'MeasureContent' : "uitleg maatregel",
            'AdviceType' : 1,
            'SubAdviceType' : '1',
            'AdviceContent' : "uitleg afvies"
        }

        # Method under test
        self.testClass.processMessage(row)

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

    def test_message_deleted(self):
        """
        Test an already deleted message is marked as such, and the end time is about now
        """
        a = Kv15Stopmessage(dataownercode='HTM', user=self.user, messagecodedate=datetime(2013, 11, 17), messagecodenumber=30 )
        a.save()
        a.delete()
        a.set_status(MessageStatus.DELETED)
        a = Kv15Stopmessage.objects.get(pk=a.pk) # Get latest from db
        self.assertEqual(a.status, MessageStatus.DELETED)
        self.assertEqual(a.isdeleted, True)

        count = Kv15Stopmessage.objects.count()

        row = {
            'DataOwnerCode' : 'HTM',
            'MessageCodeDate' : '2013-11-17',
            'MessageCodeNumber' : '30'
        }
        # Method under test
        self.testClass.processDelMessage(row)

        a = Kv15Stopmessage.objects.get(pk=a.pk) # Get latest from db
        self.assertEqual(a.status, MessageStatus.DELETE_CONFIRMED)
        self.assertLess((now() - a.messageendtime), timedelta(seconds=30), "Time wasn't set right")

    def test_message_deletion(self):
        """
        Test a message that wasn't deleted, but now is (not sure this is possible...)
        """
        a = Kv15Stopmessage(dataownercode='HTM', user=self.user, messagecodedate=datetime(2013, 11, 17), messagecodenumber=31)
        a.save()
        self.assertEqual(a.status, MessageStatus.SAVED)
        self.assertEqual(a.isdeleted, False)

        count = Kv15Stopmessage.objects.count()

        row = {
            'DataOwnerCode' : 'HTM',
            'MessageCodeDate' : '2013-11-17',
            'MessageCodeNumber' : '31'
        }
        # Method under test
        self.testClass.processDelMessage(row)

        a = Kv15Stopmessage.objects.get(pk=a.pk) # Get latest from db
        self.assertEqual(a.status, MessageStatus.DELETE_CONFIRMED)
        self.assertEqual(a.isdeleted, True)
        self.assertLess((now() - a.messageendtime), timedelta(seconds=30), "Time wasn't set right")


    def test_message_update(self):
        """
        TODO Make a test which does an update: delete + add
        """