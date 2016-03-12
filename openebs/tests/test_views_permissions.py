from datetime import timedelta
from django.contrib.auth.models import User, Group, Permission
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.test import Client, TestCase
from django.utils.timezone import now
from openebs.models import UserProfile, Kv15Stopmessage
from openebs.tests.utils_test import TestUtils


class TestViewPermissions(TestCase):
    """
    Gathering place of all tests related to permissions, especially on isolation between different companies
    """
    @classmethod
    def setUpClass(cls):
        super(TestViewPermissions, cls).setUpClass()

        # Setup user and assign company
        cls.user = User.objects.create_user(username="test_permission", password="test")
        cls.user.user_permissions.add(Permission.objects.get(codename='view_messages'))
        cls.user.save()
        p = UserProfile(user=cls.user, company='NS') # Creating messages for Veolia
        p.save()

    def setUp(self):
        self.client = Client()
        result = self.client.login(username="test_permission", password="test")
        self.assertTrue(result)

    def test_view_messages(self):
        response = self.client.get(reverse('msg_index'))
        self.assertEqual(response.status_code, 200)
        self.assertEquals(len(response.context['active_list']), 0)
        self.assertEquals(len(response.context['archive_list']), 0)

        # Create NS message
        msg = TestUtils.create_message_default(self.user)
        msg.dataownercode = "NS"
        msg.messagecontent = "NS zet bussen in"
        msg.save()

        # Create HTM message (note, this user creates it however)
        msg = TestUtils.create_message_default(self.user)
        msg.save()

        response = self.client.get(reverse('msg_index'))
        self.assertEqual(response.status_code, 200)
        self.assertEquals(len(response.context['active_list']), 1)
        self.assertEquals(response.context['active_list'][0].messagecontent, "NS zet bussen in")
        self.assertEquals(len(response.context['archive_list']), 0)

    def test_view_messages_all(self):
        response = self.client.get(reverse('msg_index')+"?all=true")
        self.assertEqual(response.status_code, 200)
        self.assertEquals(len(response.context['active_list']), Kv15Stopmessage.objects.filter(dataownercode='NS').count())
        self.assertEquals(len(response.context['archive_list']), 0)

        view_all_perm = Permission.objects.get(codename='view_all')
        self.user.user_permissions.add(view_all_perm)

        response = self.client.get(reverse('msg_index'))
        self.assertEqual(response.status_code, 200)
        self.assertEquals(len(response.context['active_list']), Kv15Stopmessage.objects.filter(messageendtime__gt=now(),
                                                                                               isdeleted=False).count())

        archive_count = Kv15Stopmessage.objects.filter(Q(messageendtime__lt=now) | Q(isdeleted=True),
                                                       messagestarttime__gt=now() - timedelta(days=3)).count()
        self.assertEquals(len(response.context['archive_list']), archive_count)

        self.user.user_permissions.remove(view_all_perm)
        self.user.save()