from django.test import TestCase
from django.urls import reverse

from apps.core.tests.utils import add_default_data
from apps.organizations.routes import OrgRoute


class OrgProfileViewTest(TestCase):
    """Test org_profile view."""

    @classmethod
    def setUpTestData(cls) -> None:
        add_default_data()

    def test_OrgProfileViewOk(self) -> None:
        response = self.client.get(reverse(OrgRoute.PROFILE, args=["rap"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "org/profile.html")

    def test_OrgProfileViewKo(self) -> None:
        response = self.client.get(reverse(OrgRoute.PROFILE, args=["not_existing_org"]))
        self.assertEqual(response.status_code, 404)
