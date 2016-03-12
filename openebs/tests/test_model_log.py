from django.test import TestCase
from django.contrib.auth.models import User
from openebs.models import Kv15Log
from openebs.tests.utils_test import TestUtils


class TestKv15LogModel(TestCase):

    def test_log_message(self):
        u = User.objects.create_user("log")
        m = TestUtils.create_message_default(u)
        m.save() # This assigns an codenumber
        Kv15Log.create_log_entry(m, "10.0.0.1")

        self.assertEquals(Kv15Log.objects.count(), 1)