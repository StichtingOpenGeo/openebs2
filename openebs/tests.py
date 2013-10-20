"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from datetime import timedelta
from django.test import TestCase
from django.utils.timezone import now
from django.contrib.auth.models import User
from models import Kv15Stopmessage

class TestKv15MessageModel(TestCase):
    user = None

    def setUp(self):
        self.user = User.objects.create_user("test")

    def create_message_default(self):
        msg = Kv15Stopmessage()
        msg.user = self.user
        msg.messagecodedate = now().date().isoformat()
        msg.messageendtime = msg.messagestarttime + timedelta(1)
        msg.measurecontent = "This is a test message"
        return msg

    def test_new_message_twice(self):
        msg = self.create_message_default()
        msg.save()
        self.assertEqual(msg.messagecodenumber, 1)

        msg = self.create_message_default()
        msg.save()

        self.assertEqual(msg.messagecodenumber, 2)

    def test_new_message_per_day(self):
        msg = self.create_message_default()
        msg.save()
        self.assertEqual(msg.messagecodenumber, 1)

        # Create another message and add a day
        msg = self.create_message_default()
        date = now() + timedelta(1)
        msg.messagecodedate = date.date().isoformat()
        msg.save()

        self.assertEqual(msg.messagecodenumber, 1)

    def test_delete(self):
        msg = self.create_message_default()
        msg.save()
        self.assertFalse(msg.isdeleted)
        msg_pk = msg.pk
        msg.delete()

        # Delete should be nothing more than triggering our flag
        self.assertTrue(msg.isdeleted)
        self.assertEqual(msg_pk, msg.pk)
