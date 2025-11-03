from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify

from apps.accounts.models import PytitionUser
from apps.accounts.routes import AccountsRoute
from apps.organizations.models import Organization
from apps.organizations.routes import OrgRoute
from apps.petitions.models import Petition

users = ["julia", "john", "max", "sarah"]
orgs = ["RAP", "Greenpeace", "Attac", "Les Amis de la Terre"]

user_published_petitions = {"john": 0, "sarah": 0, "julia": 5, "max": 10}

user_unpublished_petitions = {"john": 0, "sarah": 5, "julia": 0, "max": 10}

org_published_petitions = {
    "RAP": 0,
    "Les Amis de la Terre": 0,
    "Greenpeace": 1,
    "Attac": 2,
}

org_unpublished_petitions = {
    "RAP": 0,
    "Les Amis de la Terre": 1,
    "Greenpeace": 0,
    "Attac": 2,
}


class IndexViewTest(TestCase):
    """Test index view."""

    @classmethod
    def setUpTestData(cls) -> None:
        User = get_user_model()
        for org in orgs:
            o = Organization.objects.create(name=org)
            for i in range(org_published_petitions[org]):
                _p = Petition.objects.create(
                    published=True, org=o, title=f"Petition A{i}"
                )
            for i in range(org_unpublished_petitions[org]):
                _p = Petition.objects.create(
                    published=False, org=o, title=f"Petition B{i}"
                )
            o.save()
        for user in users:
            u = User.objects.create_user(user)
            u.first_name = user
            u.save()
            pu = PytitionUser.objects.get(user__username=user)
            for i in range(user_published_petitions[user]):
                _p = Petition.objects.create(
                    published=True, user=pu, title=f"Petition C{i}"
                )
            for i in range(user_unpublished_petitions[user]):
                _p = Petition.objects.create(
                    published=False, user=pu, title=f"Petition D{i}"
                )

    def tearDown(self) -> None:
        pass

    def test_index(self) -> None:
        with self.settings(INDEX_PAGE="HOME"):
            response = self.client.get("/", follow=True)
            self.assertTemplateUsed(response, "layouts/base.html")

    def test_index_orga_profile(self) -> None:
        for org in orgs:
            orgslugname = slugify(org)
            with (
                self.settings(INDEX_PAGE="ORGA_PROFILE", INDEX_PAGE_ORGA=org),
                self.subTest(org=org),
            ):
                response = self.client.get("/", follow=True)
                self.assertRedirects(
                    response, reverse(OrgRoute.PROFILE, args=[orgslugname])
                )
                self.assertEqual(
                    len(response.context["petitions"]), org_published_petitions[org]
                )

    def test_index_user_profile(self) -> None:
        for user in users:
            with (
                self.settings(INDEX_PAGE="USER_PROFILE", INDEX_PAGE_USER=user),
                self.subTest(user=user),
            ):
                response = self.client.get("/", follow=True)
                self.assertRedirects(
                    response, reverse(AccountsRoute.PUBLIC_PROFILE, args=[user])
                )
                self.assertEqual(
                    len(response.context["petitions"]),
                    user_published_petitions[user],
                )

    def test_index_login_register(self) -> None:
        with self.settings(INDEX_PAGE="LOGIN_REGISTER"):
            response = self.client.get("/", follow=True)
            self.assertRedirects(response, reverse("login"))

            User = get_user_model()
            user = User.objects.create_user(
                "temporary", "temporary@temporary.com", "temporary"
            )
            pu = PytitionUser.objects.get(user__username=user)
            self.client.login(username="temporary", password="temporary")

            response = self.client.get("/", follow=True)
            self.assertRedirects(response, reverse(AccountsRoute.DASHBOARD))
            self.assertEqual(response.context["user"], pu)
