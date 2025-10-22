from django.test import TestCase
from django.urls import reverse

from apps.core.tests.utils import add_default_data


class UserProfileViewTest(TestCase):
    """Test user_profile view."""

    @classmethod
    def setUpTestData(cls) -> None:
        add_default_data()

    def test_UserProfileViewOk(self) -> None:
        response = self.client.get(reverse("user_profile", args=["max"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/user_profile.html")

    def test_UserProfileViewKo(self) -> None:
        response = self.client.get(reverse("user_profile", args=["not_existing_user"]))
        self.assertEqual(response.status_code, 404)
