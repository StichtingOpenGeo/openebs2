from datetime import timedelta
from django.test import TestCase
from django.db import IntegrityError
from django.utils.timezone import now
from django.contrib.auth.models import User

from openebs.models import MessageStatus, Kv15Stopmessage
from openebs.tests.utils_test import TestUtils


class TestKv15MessageModel(TestCase):
    user = None

    def setUp(self):
        self.user = User.objects.create_user("test")

    def test_new_message_twice(self):
        msg = TestUtils.create_message_default(self.user)
        msg.save()
        self.assertEqual(msg.messagecodenumber, 5000)

        msg = TestUtils.create_message_default(self.user)
        msg.save()

        self.assertEqual(msg.messagecodenumber, 5001)

    def test_new_message_too_many(self):
        msg = TestUtils.create_message_default(self.user)
        msg.messagecodenumber = 9999
        msg.save()
        self.assertEqual(msg.messagecodenumber, 9999)

        msg = TestUtils.create_message_default(self.user)
        with self.assertRaises(IntegrityError):
            msg.save()

    def test_new_message_per_day(self):
        msg = TestUtils.create_message_default(self.user)
        msg.save()
        previous_num = msg.messagecodenumber

        # Create another message and add a day
        msg = TestUtils.create_message_default(self.user)
        date = now() + timedelta(days=1)
        msg.messagecodedate = date.date().isoformat()
        msg.save()

        self.assertEqual(msg.messagecodenumber, 5000)
        self.assertLess(1, previous_num, "On a new day, messagecodenumber wasn't one")

    def test_delete(self):
        msg = TestUtils.create_message_default(self.user)
        msg.save()
        self.assertFalse(msg.isdeleted)
        msg_pk = msg.pk
        msg_code = msg.messagecodenumber
        msg.delete()

        # Delete should be nothing more than triggering our flag
        self.assertTrue(msg.isdeleted)
        self.assertEqual(msg_pk, msg.pk)
        self.assertEqual(msg_code, msg.messagecodenumber)

    def test_force_delete(self):
        msg = TestUtils.create_message_default(self.user)
        msg.save()
        msg.force_delete()

        # Force delete should actually remove the object
        self.assertEqual(msg.pk, None)

    def test_update(self):
        msg = TestUtils.create_message_default(self.user)
        msg.save()
        initial = msg.messagecodenumber
        initial_pk = msg.pk

        msg.save()
        self.assertEqual(initial+1, msg.messagecodenumber)
        self.assertEqual(initial_pk+1, msg.pk)
        self.assertEqual(MessageStatus.SAVED, msg.status)

        # Fake this, the view does this after pushing
        # TODO Just test the view, remove this
        Kv15Stopmessage.objects.get(pk=initial_pk).set_status(MessageStatus.DELETED)
        self.assertEqual(MessageStatus.DELETED, Kv15Stopmessage.objects.get(pk=initial_pk).status)