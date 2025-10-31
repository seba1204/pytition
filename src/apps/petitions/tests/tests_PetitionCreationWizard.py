from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import Permission
from apps.accounts.routes import AccountsRoute
from apps.organizations.models import Organization
from apps.petition.models import PytitionUser

users = ["julia", "john", "max", "sarah"]
orgs = ["RAP", "Greenpeace", "Attac", "Les Amis de la Terre"]

org_members = {
    "RAP": ["julia"],
    "Les Amis de la Terre": ["julia", "max"],
    "Attac": ["john"],
}


class PetitionCreateWizardViewTest(TestCase):
    """Test PetitionCreateWizard view."""

    @classmethod
    def setUpTestData(cls) -> None:
        User = get_user_model()
        for org in orgs:
            o = Organization.objects.create(name=org)
            o.save()
        for user in users:
            u = User.objects.create_user(user, password=user)
            u.first_name = user
            u.last_name = user + "Last"
            u.save()
        for orgname, member_usernames in org_members.items():
            org_obj = Organization.objects.get(name=orgname)
            for username in member_usernames:
                user_obj = PytitionUser.objects.get(user__username=username)
                org_obj.members.add(user_obj)
                permission = Permission.objects.get(organization=org_obj, user=user_obj)
                permission.can_modify_permissions = True
                permission.save()

        # give julia can_modify_petitions permission on "Les Amis de la Terre" organization
        user_obj = PytitionUser.objects.get(user__username="julia")
        org_obj = Organization.objects.get(name="Les Amis de la Terre")
        perm = Permission.objects.get(organization=org_obj, user=user_obj)
        perm.can_modify_petitions = True
        perm.save()

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
            reverse("org_petition_wizard", args=[org.slugname]), follow=True
        )
        self.assertRedirects(
            response,
            reverse("login")
            + "?next="
            + reverse("org_petition_wizard", args=[org.slugname]),
        )
        self.assertTemplateUsed(response, "registration/login.html")
        self.assertTemplateUsed(response, "layouts/base.html")

    def test_call_page1_ok(self) -> None:
        self.login("julia")
        org = Organization.objects.get(name="Les Amis de la Terre")
        response = self.client.get(reverse("org_petition_wizard", args=[org.slugname]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "org/base.html")

    def test_call_page2_ok(self) -> None:
        self.login("julia")
        org = Organization.objects.get(name="Les Amis de la Terre")
        response = self.client.get(reverse("user_petition_wizard"))
        self.assertEqual(response.status_code, 200)

    @override_settings(DISABLE_USER_PETITION=True)
    def test_user_petition_disabled(self) -> None:
        self.login("julia")
        response = self.client.get(reverse("user_petition_wizard"))
        self.assertRedirects(response, reverse(AccountsRoute.DASHBOARD))
        response = self.client.get(reverse("user_petition_wizard"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Users are not allowed to create their own petitions."
        )

    @override_settings(DISABLE_USER_PETITION=True)
    def test_org_petition_still_working(self) -> None:
        self.login("julia")
        org = Organization.objects.get(name="Les Amis de la Terre")
        response = self.client.get(reverse("org_petition_wizard", args=[org.slugname]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response, "Users are not allowed to create their own petitions."
        )
