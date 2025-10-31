from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Permission, PytitionUser
from apps.accounts.routes import AccountsRoute
from apps.core.tests.utils import add_default_data
from apps.organizations.models import Organization
from apps.organizations.routes import OrgRoute


class OrgDeleteMemberViewTest(TestCase):
    """Test org_delete_member view."""

    @classmethod
    def setUpTestData(cls) -> None:
        add_default_data()

    def login(self, name: str, password: str | None = None) -> PytitionUser:
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self) -> None:
        self.client.logout()

    def test_OrgDeleteMemberViewOk(self) -> None:
        """Let's try to add and then delete user max to org RAP."""
        # Add max to RAP
        julia = self.login("julia")
        julia_perms = Permission.objects.get(organization__slugname="rap", user=julia)
        julia_perms.can_add_members = True
        # Add permission to remove members
        julia_perms.can_remove_members = True
        julia_perms.save()
        response = self.client.get(
            reverse(OrgRoute.ADD_USER, args=["rap"]) + "?user=max"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        user = PytitionUser.objects.get(user__username="max")
        rap = Organization.objects.get(slugname="rap")
        invitations = user.invitations.all()
        self.assertIn(rap, invitations)
        # Max accepts invitation
        self.logout()
        max = self.login("max")
        response = self.client.get(
            reverse(OrgRoute.INVITE_ACCEPT, kwargs={"orgslugname": "rap"}), follow=True
        )
        self.assertRedirects(response, reverse(AccountsRoute.DASHBOARD))
        rap = Organization.objects.get(slugname="rap")
        self.assertIn(max, rap.members.all())
        self.assertIn(rap, max.organization_set.all())
        self.assertNotIn(rap, max.invitations.all())
        # Remove max from RAP
        self.logout()
        julia = self.login("julia")
        response = self.client.get(
            reverse(OrgRoute.DELETE_MEMBER, kwargs={"orgslugname": "rap"})
            + "?member=max"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_OrgDeleteMemberViewKoForbidden(self) -> None:
        """Let's try to add user max to org RAP from non-authorized Julia user."""
        # Add max to RAP
        julia = self.login("julia")
        julia_perms = Permission.objects.get(organization__slugname="rap", user=julia)
        julia_perms.can_add_members = True
        julia_perms.can_remove_members = False
        julia_perms.save()
        response = self.client.get(
            reverse(OrgRoute.ADD_USER, args=["rap"]) + "?user=max"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        user = PytitionUser.objects.get(user__username="max")
        rap = Organization.objects.get(slugname="rap")
        invitations = user.invitations.all()
        self.assertIn(rap, invitations)
        # Max accepts invitation
        self.logout()
        max = self.login("max")
        response = self.client.get(
            reverse(OrgRoute.INVITE_ACCEPT, kwargs={"orgslugname": "rap"}), follow=True
        )
        self.assertRedirects(response, reverse(AccountsRoute.DASHBOARD))
        rap = Organization.objects.get(slugname="rap")
        self.assertIn(max, rap.members.all())
        self.assertIn(rap, max.organization_set.all())
        self.assertNotIn(rap, max.invitations.all())
        # Remove max from RAP
        self.logout()
        julia = self.login("julia")
        # Now try to remove member from RAP org without the corresponding permission
        response = self.client.get(
            reverse(OrgRoute.DELETE_MEMBER, args=["rap"]) + "?member=max"
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_OrgDeleteMemberLastAdminKo(self) -> None:
        julia = self.login("julia")
        julia_perms = Permission.objects.get(organization__slugname="rap", user=julia)
        # Add permission to remove members
        julia_perms.can_remove_members = True
        julia_perms.save()
        response = self.client.get(
            reverse(OrgRoute.DELETE_MEMBER, kwargs={"orgslugname": "rap"})
            + "?member=julia"
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response["Content-Type"], "application/json")
