from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify

from apps.core.tests.utils import add_default_data
from apps.organizations.routes import OrgRoute
from apps.petition.models import Organization, PytitionUser


class OrgDashboardViewTest(TestCase):
    """Test index view."""

    @classmethod
    def setUpTestData(cls) -> None:
        add_default_data()

    def login(self, name: str) -> PytitionUser:
        self.client.login(username=name, password=name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self) -> None:
        self.client.logout()

    def tearDown(self) -> None:
        # Clean up run after every test method.
        pass

    def test_orgNotExist(self) -> None:
        org_name = "org that does not exist"
        orgslugname = slugify(org_name)
        self.login("julia")
        response = self.client.get(
            reverse(OrgRoute.DASHBOARD, args=[orgslugname]), follow=True
        )
        self.assertRedirects(response, reverse("user_dashboard"))
        self.assertTemplateUsed(response, "petition/user_dashboard.html")

    def test_NotAMember(self) -> None:
        org_name = "Attac"
        orgslugname = slugify(org_name)
        self.login("julia")
        response = self.client.get(
            reverse(OrgRoute.DASHBOARD, args=[orgslugname]), follow=True
        )
        self.assertRedirects(response, reverse("user_dashboard"))
        self.assertTemplateUsed(response, "petition/user_dashboard.html")

    def test_NotLoggedIn(self) -> None:
        self.logout()
        org_name = "RAP"
        orgslugname = slugify(org_name)
        response = self.client.get(
            reverse(OrgRoute.DASHBOARD, args=[orgslugname]), follow=True
        )
        self.assertRedirects(
            response,
            reverse("login")
            + "?next="
            + reverse(OrgRoute.DASHBOARD, args=[orgslugname]),
        )
        self.assertTemplateUsed(response, "registration/login.html")
        self.assertTemplateUsed(response, "layouts/base.html")

    def test_OrgOK1(self) -> None:
        org_name = "Attac"
        orgslugname = slugify(org_name)
        john = self.login("john")
        _org = Organization.objects.get(name=org_name)
        response = self.client.get(reverse(OrgRoute.DASHBOARD, args=[orgslugname]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/org_dashboard.html")
        petitions = response.context["petitions"].all()
        self.assertEqual(len(petitions), 4)
        self.assertEqual(response.context["user"], john)

    def test_OrgOK2(self) -> None:
        org_name = "RAP"
        orgslugname = slugify(org_name)
        julia = self.login("julia")
        response = self.client.get(reverse(OrgRoute.DASHBOARD, args=[orgslugname]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/org_dashboard.html")
        petitions = response.context["petitions"].all()
        self.assertEqual(len(petitions), 0)
        self.assertEqual(response.context["user"], julia)

    def test_OrgOK3(self) -> None:
        org_name = "Les Amis de la Terre"
        orgslugname = slugify(org_name)
        max = self.login("max")
        response = self.client.get(reverse(OrgRoute.DASHBOARD, args=[orgslugname]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "petition/org_dashboard.html")
        petitions = response.context["petitions"].all()
        self.assertEqual(len(petitions), 1)
        self.assertEqual(response.context["user"], max)
