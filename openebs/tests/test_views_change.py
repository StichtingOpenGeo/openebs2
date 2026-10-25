from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User, Permission
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.timezone import now

from kv1.models import Kv1Line, Kv1Journey
from openebs.models import UserProfile, Kv17Change
from openebs.views_change import ChangeDeleteView, ChangeUpdateView


class TestChangeRecoverViews(TestCase):
    """
    Restoring (and redoing) a KV17 change has to be pushed. Since Django 4.0 a POST to a DeleteView goes through
    form_valid(), so the push mustn't live in delete()
    """
    def setUp(self):
        user = User.objects.create_user(username="test_change", password="test")
        user.user_permissions.add(Permission.objects.get(codename='add_change', content_type__model='kv17change'))
        UserProfile(user=user, company='HTM').save()
        self.client = Client()
        self.assertTrue(self.client.login(username="test_change", password="test"))

        line = Kv1Line(dataownercode='HTM', lineplanningnumber="1001", publiclinenumber="1", headsign="Naar Huis",
                       stop_map=[])
        line.save()
        journey = Kv1Journey(dataownercode='HTM', line=line, journeynumber=100, scheduleref=1, departuretime=900,
                             direction=1)
        journey.save()
        self.change = Kv17Change(dataownercode='HTM', line=line, journey=journey,
                                 operatingday=now().date() + timedelta(days=1))
        self.change.save()

    def test_restore(self):
        with patch.object(ChangeDeleteView, 'push_message', return_value=True) as push:
            response = self.client.post(reverse('change_delete', args=[self.change.pk]))
        self.assertRedirects(response, reverse('change_index'), fetch_redirect_response=False)
        self.assertEqual(1, push.call_count)
        self.assertIn('<RECOVER>', push.call_args[0][0][0])
        self.change.refresh_from_db()
        self.assertTrue(self.change.is_recovered)

    def test_restore_push_fails(self):
        with patch.object(ChangeDeleteView, 'push_message', return_value=False):
            self.client.post(reverse('change_delete', args=[self.change.pk]))
        self.change.refresh_from_db()
        self.assertFalse(self.change.is_recovered)

    def test_restore_delete_request(self):
        with patch.object(ChangeDeleteView, 'push_message', return_value=True) as push:
            self.client.delete(reverse('change_delete', args=[self.change.pk]))
        self.assertEqual(1, push.call_count)

    def test_redo(self):
        self.change.delete()  # Only marks it as recovered
        with patch.object(ChangeUpdateView, 'push_message', return_value=True) as push:
            response = self.client.post(reverse('change_redo', args=[self.change.pk]))
        self.assertRedirects(response, reverse('change_index'), fetch_redirect_response=False)
        self.assertEqual(1, push.call_count)
        self.assertIn('<KV17MUTATEJOURNEY>', push.call_args[0][0])
        self.change.refresh_from_db()
        self.assertFalse(self.change.is_recovered)

    def test_redo_push_fails(self):
        self.change.delete()
        with patch.object(ChangeUpdateView, 'push_message', return_value=False):
            self.client.post(reverse('change_redo', args=[self.change.pk]))
        self.change.refresh_from_db()
        self.assertTrue(self.change.is_recovered)
