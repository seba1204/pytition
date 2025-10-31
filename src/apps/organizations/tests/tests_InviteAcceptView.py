from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Permission
from apps.accounts.routes import AccountsRoute
from apps.core.tests.utils import add_default_data
from apps.organizations.models import Organization
from apps.organizations.routes import OrgRoute
from apps.petition.models import PytitionUser


class InviteAcceptViewTest(TestCase):
    """Test invite_accept view."""

    @classmethod
    def setUpTestData(cls) -> None:
        add_default_data()

    def login(self, name: str, password: str | None = None) -> PytitionUser:
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self) -> None:
        self.client.logout()

    def test_InviteAcceptViewOk(self) -> None:
        julia = self.login("julia")
        # julia invites max
        julia_perms = Permission.objects.get(organization__slugname="rap", user=julia)
        julia_perms.can_add_members = True
        julia_perms.save()
        response = self.client.get(
            reverse(OrgRoute.ADD_USER, args=["rap"]) + "?user=max"
        )
        self.assertEqual(response.status_code, 200)
        self.logout()
        max = self.login("max")
        # max accepts julia's invitation
        response = self.client.get(
            reverse(OrgRoute.INVITE_ACCEPT, kwargs={"orgslugname": "rap"}), follow=True
        )
        self.assertRedirects(response, reverse(AccountsRoute.DASHBOARD))
        rap = Organization.objects.get(slugname="rap")
        self.assertIn(max, rap.members.all())
        self.assertIn(rap, max.organization_set.all())
        self.assertNotIn(rap, max.invitations.all())
