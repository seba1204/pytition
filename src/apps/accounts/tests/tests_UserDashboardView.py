from django.test import TestCase
from django.urls import reverse

from apps.accounts.routes import AccountsRoute
from apps.core.tests.utils import add_default_data
from apps.petition.models import PytitionUser


class UserDashboardViewTest(TestCase):
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

    def test_NotLoggedIn(self) -> None:
        self.logout()
        response = self.client.get(reverse(AccountsRoute.DASHBOARD), follow=True)
        self.assertRedirects(
            response, reverse("login") + "?next=" + reverse(AccountsRoute.DASHBOARD)
        )
        self.assertTemplateUsed(response, "registration/login.html")
        self.assertTemplateUsed(response, "layouts/base.html")

    def test_UserOK1(self) -> None:
        john = self.login("john")
        num_petitions = john.petition_set.count()

        response = self.client.get(reverse(AccountsRoute.DASHBOARD))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/dashboard.html")
        self.assertTemplateUsed(response, "accounts/base.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        petitions = response.context["petitions"].all()
        self.assertEqual(len(petitions), num_petitions)
        self.assertEqual(response.context["user"], john)

    def test_UserOK2(self) -> None:
        julia = self.login("julia")
        num_petitions = julia.petition_set.count()

        response = self.client.get(reverse(AccountsRoute.DASHBOARD))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/dashboard.html")
        self.assertTemplateUsed(response, "accounts/base.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        petitions = response.context["petitions"].all()
        self.assertEqual(len(petitions), num_petitions)
        self.assertEqual(response.context["user"], julia)

    def test_UserOK3(self) -> None:
        max = self.login("max")
        num_petitions = max.petition_set.count()

        response = self.client.get(reverse(AccountsRoute.DASHBOARD))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/dashboard.html")
        self.assertTemplateUsed(response, "accounts/base.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        petitions = response.context["petitions"].all()
        self.assertEqual(len(petitions), num_petitions)
        self.assertEqual(response.context["user"], max)

    def test_UserOK4(self) -> None:
        sarah = self.login("sarah")
        num_petitions = sarah.petition_set.count()

        response = self.client.get(reverse(AccountsRoute.DASHBOARD))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/dashboard.html")
        self.assertTemplateUsed(response, "accounts/base.html")
        self.assertTemplateUsed(response, "layouts/base.html")
        petitions = response.context["petitions"].all()
        self.assertEqual(len(petitions), num_petitions)
        self.assertEqual(response.context["user"], sarah)
