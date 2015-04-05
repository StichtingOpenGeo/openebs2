from django.contrib.auth.models import User
from django.test import Client
from django.utils.unittest.case import TestCase
from openebs.models import UserProfile


class TestViewPermissions(TestCase):
    """
    Gathering place of all tests related to permissions, especially on isolation between different companies
    """
    @classmethod
    def setUpClass(cls):
        # Setup user and assign company
        cls.user = User.objects.create_user(username="test_permission", password="test")
        cls.user.save()
        p = UserProfile(user=cls.user, company='CXX') # Creating messages for Veolia
        p.save()

    def setUp(self):
        self.client = Client()
        result = self.client.login(username="test_permission", password="test")
        self.assertTrue(result)

    def test_isolation_messages(self):
        pass
        self.client.get('')

    def test_isolation_scenarios(self):
        pass