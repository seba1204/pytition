from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.text import slugify

from apps.accounts.models import Permission, PytitionUser
from apps.accounts.routes import AccountsRoute
from apps.core.tests.utils import add_default_data
from apps.organizations.models import Organization
from apps.organizations.routes import OrgRoute


class OrgCreateViewTest(TestCase):
    """Test Org Creation view."""

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

    def test_CreateGetFormOK(self) -> None:
        _john = self.login("john")
        response = self.client.get(reverse(OrgRoute.CREATE))
        self.assertEqual(response.status_code, 200)

    def test_CreateOK(self) -> None:
        john = self.login("john")
        newname = "my new-org with @ ç special_chars"
        previous_org_numbers = john.organization_set.count()
        data = {
            "name": newname,
        }
        response = self.client.post(reverse(OrgRoute.CREATE), data, follow=True)
        self.assertRedirects(response, reverse(AccountsRoute.DASHBOARD))
        user = response.context["user"]
        orgs = user.organization_set.all()
        self.assertEqual(user, john)
        self.assertEqual(len(orgs), previous_org_numbers + 1)
        org = Organization.objects.get(slugname=slugify(newname))
        self.assertEqual(org.slugname, slugify(newname))
        self.assertEqual(org.name, newname)
        admins_perms = Permission.objects.filter(
            organization=org, can_modify_permissions=True
        )
        self.assertGreaterEqual(admins_perms.count(), 1)

    def test_CreateAlreadyExistsKO(self) -> None:
        john = self.login("john")
        newname = "my new-org with @ ç special_chars"
        previous_org_numbers = john.organization_set.count()
        data = {
            "name": newname,
        }
        # first creation
        response = self.client.post(reverse(OrgRoute.CREATE), data, follow=True)
        self.assertRedirects(response, reverse(AccountsRoute.DASHBOARD))
        user = response.context["user"]
        orgs = user.organization_set.all()
        self.assertEqual(user, john)
        self.assertEqual(len(orgs), previous_org_numbers + 1)
        org = Organization.objects.get(slugname=slugify(newname))
        self.assertEqual(org.slugname, slugify(newname))
        self.assertEqual(org.name, newname)

        # second creation try
        response = self.client.post(reverse(OrgRoute.CREATE), data, follow=True)
        self.assertEqual(response.status_code, 200)
        org_count = user.organization_set.filter(name=newname).count()
        self.assertEqual(org_count, 1)

    def test_CreateEmptyKO(self) -> None:
        john = self.login("john")
        newname = ""
        previous_org_numbers = john.organization_set.count()
        data = {
            "name": newname,
        }
        response = self.client.post(reverse(OrgRoute.CREATE), data)
        self.assertEqual(response.status_code, 200)
        user = response.context["user"]
        orgs = user.organization_set.all()
        self.assertEqual(user, john)
        self.assertEqual(len(orgs), previous_org_numbers)
        empty_org_name_number = Organization.objects.filter(name="").count()
        self.assertEqual(empty_org_name_number, 0)

    def test_UserUnauthenticatedKO(self) -> None:
        self.logout()
        newname = "my new-org with @ ç special_chars"
        data = {
            "name": newname,
        }
        previous_org_num = Organization.objects.count()
        response = self.client.post(reverse(OrgRoute.CREATE), data, follow=True)
        self.assertRedirects(
            response, reverse("login") + "?next=" + reverse(OrgRoute.CREATE)
        )
        new_org_num = Organization.objects.count()
        self.assertEqual(previous_org_num, new_org_num)

    @override_settings(RESTRICT_ORG_CREATION=True)
    def test_restrict_org_creation(self) -> None:
        init_org_number = Organization.objects.count()
        self.login("john")

        response = self.client.get(reverse(OrgRoute.CREATE), follow=True)
        self.assertRedirects(response, reverse(AccountsRoute.DASHBOARD))
        self.assertContains(response, "Only super users can create an organization.")

        data = {"name": "New Org"}
        response = self.client.post(reverse(OrgRoute.CREATE), data, follow=True)
        self.assertRedirects(response, reverse(AccountsRoute.DASHBOARD))
        self.assertEqual(Organization.objects.count(), init_org_number)
        self.assertContains(response, "Only super users can create an organization.")

        self.login("admin")
        response = self.client.post(reverse(OrgRoute.CREATE), data, follow=True)
        self.assertRedirects(response, reverse(AccountsRoute.DASHBOARD))
        self.assertEqual(Organization.objects.count(), init_org_number + 1)
        self.assertNotContains(response, "Only super users can create an organization.")
