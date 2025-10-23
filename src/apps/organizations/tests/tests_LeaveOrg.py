from django.test import TestCase
from django.urls import reverse

from apps.core.tests.utils import add_default_data
from apps.organizations.routes import OrgRoute
from apps.petition.models import Organization, PytitionUser


class LeaveOrgViewTest(TestCase):
    """Test LeaveOrg view."""

    @classmethod
    def setUpTestData(cls) -> None:
        add_default_data()

    def login(self, name: str, password: str | None = None) -> PytitionUser:
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self) -> None:
        self.client.logout()

    def tearDown(self) -> None:
        # Clean up run after every test method.
        pass

    def test_NotLoggedIn(self) -> None:
        self.logout()
        org = Organization.objects.get(name="RAP")
        response = self.client.get(
            reverse(OrgRoute.LEAVE, args=[org.slugname]), follow=True
        )
        self.assertRedirects(
            response,
            reverse("login") + "?next=" + reverse(OrgRoute.LEAVE, args=[org.slugname]),
        )
        self.assertTemplateUsed(response, "registration/login.html")
        self.assertTemplateUsed(response, "layouts/base.html")

    def test_leave_org_ok(self) -> None:
        max = self.login("max")
        org = Organization.objects.get(name="Les Amis de la Terre")
        response = self.client.get(reverse(OrgRoute.LEAVE, args=[org.slugname]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("account_settings"))
        self.assertNotIn(org, max.organization_set.all())

    def test_leave_refuse_alone(self) -> None:
        julia = self.login("julia")
        org = Organization.objects.get(name="RAP")
        response = self.client.get(reverse(OrgRoute.LEAVE, args=[org.slugname]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("account_settings") + "#a_org_form")
        self.assertIn(org, julia.organization_set.all())

    def test_leave_refuse_lastAdmin(self) -> None:
        julia = self.login("julia")
        org = Organization.objects.get(name="Les Amis de la Terre")
        response = self.client.get(reverse(OrgRoute.LEAVE, args=[org.slugname]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("account_settings") + "#a_org_form")
        self.assertIn(org, julia.organization_set.all())
