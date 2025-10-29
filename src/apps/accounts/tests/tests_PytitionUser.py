from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.petition.models import PytitionUser


class PytitionUserTest(TestCase):
    def setUp(self) -> None:
        pass

    def test_createPytitionUser(self) -> None:
        User = get_user_model()
        u = User.objects.create_user("julia", password="julia")
        self.assertEqual(PytitionUser.objects.count(), 1)
