from django.contrib.messages import constants
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Permission, PytitionUser
from apps.accounts.routes import AccountsRoute
from apps.core.tests.utils import add_default_data
from apps.organizations.models import Organization
from apps.organizations.routes import OrgRoute
from apps.signatures.models import Signature


class PetitionViewTest(TestCase):
    """Test index view."""

    @classmethod
    def setUpTestData(cls) -> None:
        add_default_data()

    def tearDown(self) -> None:
        # Clean up run after every test method.
        pass

    def login(self, name: str, password: str | None = None) -> PytitionUser:
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self) -> None:
        self.client.logout()

    def test_show_signatures(self) -> None:
        julia = self.login("julia")
        # User petition
        p = julia.petition_set.first()
        self.assertIsNotNone(p, "Petition should not be None for user 'julia'")

        if p is None:
            return  # Prevent further errors if the petition is None

        response = self.client.get(reverse("show_signatures", args=[p.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signatures/data.html")
        # Add signature
        self.assertEqual(Signature.objects.count(), 0)
        Signature.objects.create(
            first_name="Me", last_name="You", email="you@example.org", petition=p
        )
        self.assertEqual(Signature.objects.count(), 1)
        response = self.client.get(reverse("show_signatures", args=[p.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signatures/data.html")
        # Org petition
        max = self.login("max")
        org = Organization.objects.get(name="Les Amis de la Terre")
        p2 = org.petition_set.first()

        self.assertIsNotNone(
            p2, "Petition should not be None for organization 'Les Amis de la Terre'"
        )
        if p2 is None:
            return  # Prevent further errors if the petition is None
        response = self.client.get(reverse("show_signatures", args=[p2.id]))
        self.assertEqual(response.status_code, 302)
        # Ah right, Max does not have access rights for that
        perm = Permission.objects.get(organization=org, user=max)
        perm.can_view_signatures = True
        perm.save()
        response = self.client.get(reverse("show_signatures", args=[p2.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signatures/data.html")

    def test_get_csv_signature(self) -> None:
        julia = self.login("julia")
        # User petition
        p = julia.petition_set.first()
        self.assertIsNotNone(p, "Petition should not be None for user 'julia'")
        if p is None:
            return  # Prevent further errors if the petition is None
        response = self.client.get(reverse("get_csv_signature", args=[p.id]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("get_csv_confirmed_signature", args=[p.id]))
        self.assertEqual(response.status_code, 200)
        # Add signature
        self.assertEqual(Signature.objects.count(), 0)
        Signature.objects.create(
            first_name="Me", last_name="You", email="you@example.org", petition=p
        )
        self.assertEqual(Signature.objects.count(), 1)
        response = self.client.get(reverse("get_csv_signature", args=[p.id]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("get_csv_confirmed_signature", args=[p.id]))
        self.assertEqual(response.status_code, 200)
        # Org petition
        self.login("max")
        org = Organization.objects.get(name="Les Amis de la Terre")
        p2 = org.petition_set.first()

        self.assertIsNotNone(
            p2, "Petition should not be None for organization 'Les Amis de la Terre'"
        )
        if p2 is None:
            return  # Prevent further errors if the petition is None
        response = self.client.get(reverse("get_csv_signature", args=[p2.id]))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse("get_csv_confirmed_signature", args=[p2.id]))
        self.assertEqual(response.status_code, 403)
        # Ah right, max does not have access rights for that
        self.login("julia")
        response = self.client.get(reverse("get_csv_signature", args=[p2.id]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("get_csv_confirmed_signature", args=[p2.id]))
        self.assertEqual(response.status_code, 200)

    def test_show_signatures_post_deleteOK(self) -> None:
        julia = self.login("julia")
        petition = julia.petition_set.first()
        self.assertIsNotNone(petition, "Petition should not be None for user 'julia'")
        if petition is None:
            return  # Prevent further errors if the petition is None
        pid = petition.id
        signature = Signature.objects.create(
            first_name="Me", last_name="You", email="you@example.org", petition=petition
        )
        sid = signature.id
        data = {
            "action": "delete",
            "signature_id": [sid],
        }
        response = self.client.post(
            reverse("show_signatures", args=[pid]), data, follow=True
        )
        self.assertRedirects(response, reverse("show_signatures", args=[pid]))
        self.assertTemplateUsed(response, "signatures/data.html")
        with self.assertRaises(Signature.DoesNotExist):
            Signature.objects.get(pk=sid)
        messages = response.context["messages"]
        self.assertGreaterEqual(len(messages), 1)
        ThereIsAnyError = False
        for msg in messages:
            if msg.level == constants.ERROR:
                ThereIsAnyError = True
        self.assertEqual(ThereIsAnyError, False)

    def test_show_signatures_post_deleteOK_org(self) -> None:
        self.login("julia")
        org = Organization.objects.get(name="Les Amis de la Terre")
        petition = org.petition_set.first()
        self.assertIsNotNone(petition, f"Petition should not be None for {org.name}")
        if petition is None:
            return  # Prevent further errors if the petition is None
        pid = petition.id
        signature = Signature.objects.create(
            first_name="Me", last_name="You", email="you@example.org", petition=petition
        )
        sid = signature.id
        data = {
            "action": "delete",
            "signature_id": [sid],
        }
        response = self.client.post(
            reverse("show_signatures", args=[pid]), data, follow=True
        )
        self.assertRedirects(response, reverse("show_signatures", args=[pid]))
        self.assertTemplateUsed(response, "signatures/data.html")
        with self.assertRaises(Signature.DoesNotExist):
            Signature.objects.get(pk=sid)
        messages = response.context["messages"]
        self.assertGreaterEqual(len(messages), 1)
        ThereIsAnyError = False
        for msg in messages:
            if msg.level == constants.ERROR:
                ThereIsAnyError = True
        self.assertEqual(ThereIsAnyError, False)

    def test_show_signatures_post_deleteKONoRightsUser(self) -> None:
        self.login("julia")
        max = PytitionUser.objects.get(user__username="max")
        petition = max.petition_set.first()
        self.assertIsNotNone(petition, f"Petition should not be None for {max.name}")
        if petition is None:
            return  # Prevent further errors if the petition is None
        pid = petition.id
        signature = Signature.objects.create(
            first_name="Me", last_name="You", email="you@example.org", petition=petition
        )
        sid = signature.id
        data = {
            "action": "delete",
            "signature_id": [sid],
        }
        response = self.client.post(
            reverse("show_signatures", args=[pid]), data, follow=True
        )
        self.assertRedirects(response, reverse(AccountsRoute.DASHBOARD))
        self.assertTemplateUsed(response, "accounts/dashboard.html")
        s = Signature.objects.get(pk=sid)
        self.assertEqual(s.id, sid)
        # dummy test, we just want the previous line
        # not to raise a DoesNotExist exception
        messages = response.context["messages"]
        self.assertGreaterEqual(len(messages), 1)
        ThereIsAnyError = False
        for msg in messages:
            if msg.level == constants.ERROR:
                ThereIsAnyError = True
        self.assertEqual(ThereIsAnyError, True)

    def test_show_signatures_post_deleteKONoRightsOrg(self) -> None:
        self.login("max")
        org = Organization.objects.get(name="Les Amis de la Terre")
        petition = org.petition_set.first()
        self.assertIsNotNone(petition, f"Petition should not be None for {org.name}")
        if petition is None:
            return  # Prevent further errors if the petition is None
        pid = petition.id
        signature = Signature.objects.create(
            first_name="Me", last_name="You", email="you@example.org", petition=petition
        )
        sid = signature.id
        data = {
            "action": "delete",
            "signature_id": [sid],
        }
        response = self.client.post(
            reverse("show_signatures", args=[pid]), data, follow=True
        )
        self.assertRedirects(response, reverse(OrgRoute.DASHBOARD, args=[org.slugname]))
        self.assertTemplateUsed(response, "org/dashboard.html")
        s = Signature.objects.get(pk=sid)
        self.assertEqual(s.id, sid)
        # dummy test, we just want the previous line not to raise
        # a DoesNotExist exception
        messages = response.context["messages"]
        self.assertGreaterEqual(len(messages), 1)
        ThereIsAnyError = False
        for msg in messages:
            if msg.level == constants.ERROR:
                ThereIsAnyError = True
        self.assertEqual(ThereIsAnyError, True)

    def test_show_signatures_post_resendOK_org(self) -> None:
        self.login("julia")
        org = Organization.objects.get(name="Les Amis de la Terre")
        petition = org.petition_set.first()

        self.assertIsNotNone(petition, f"Petition should not be None for {org.name}")
        if petition is None:
            return  # Prevent further errors if the petition is None
        pid = petition.id
        signature = Signature.objects.create(
            first_name="Me", last_name="You", email="you@example.org", petition=petition
        )
        sid = signature.id
        data = {
            "action": "re-send",
            "signature_id": [sid],
        }
        response = self.client.post(
            reverse("show_signatures", args=[pid]), data, follow=True
        )
        self.assertRedirects(response, reverse("show_signatures", args=[pid]))
        self.assertTemplateUsed(response, "signatures/data.html")
        messages = response.context["messages"]
        self.assertGreaterEqual(len(messages), 1)
        ThereIsAnyError = False
        for msg in messages:
            if msg.level == constants.ERROR:
                ThereIsAnyError = True
        self.assertEqual(ThereIsAnyError, False)

    def test_show_signatures_post_resendOK(self) -> None:
        julia = self.login("julia")
        petition = julia.petition_set.first()

        self.assertIsNotNone(petition, f"Petition should not be None for {julia.name}")
        if petition is None:
            return  # Prevent further errors if the petition is None
        pid = petition.id
        signature = Signature.objects.create(
            first_name="Me", last_name="You", email="you@example.org", petition=petition
        )
        sid = signature.id
        data = {
            "action": "re-send",
            "signature_id": [sid],
        }
        response = self.client.post(
            reverse("show_signatures", args=[pid]), data, follow=True
        )
        self.assertRedirects(response, reverse("show_signatures", args=[pid]))
        self.assertTemplateUsed(response, "signatures/data.html")
        messages = response.context["messages"]
        self.assertGreaterEqual(len(messages), 1)
        ThereIsAnyError = False
        for msg in messages:
            if msg.level == constants.ERROR:
                ThereIsAnyError = True
        self.assertEqual(ThereIsAnyError, False)

    def test_show_signatures_post_resend_allOK(self) -> None:
        julia = self.login("julia")
        petition = julia.petition_set.first()

        self.assertIsNotNone(petition, f"Petition should not be None for {julia.name}")
        if petition is None:
            return  # Prevent further errors if the petition is None
        pid = petition.id
        _ = Signature.objects.create(
            first_name="Me", last_name="You", email="you@example.org", petition=petition
        )
        # sid = signature.id
        data = {
            "action": "re-send-all",
        }
        response = self.client.post(
            reverse("show_signatures", args=[pid]), data, follow=True
        )
        self.assertRedirects(response, reverse("show_signatures", args=[pid]))
        self.assertTemplateUsed(response, "signatures/data.html")
        messages = response.context["messages"]
        self.assertGreaterEqual(len(messages), 1)
        ThereIsAnyError = False
        for msg in messages:
            if msg.level == constants.ERROR:
                ThereIsAnyError = True
        self.assertEqual(ThereIsAnyError, False)

    def test_show_signatures_post_resend_allOK_org(self) -> None:
        self.login("julia")
        org = Organization.objects.get(name="Les Amis de la Terre")
        petition = org.petition_set.first()

        self.assertIsNotNone(petition, f"Petition should not be None for {org.name}")
        if petition is None:
            return  # Prevent further errors if the petition is None
        pid = petition.id
        _ = Signature.objects.create(
            first_name="Me", last_name="You", email="you@example.org", petition=petition
        )
        # sid = signature.id
        data = {
            "action": "re-send-all",
        }
        response = self.client.post(
            reverse("show_signatures", args=[pid]), data, follow=True
        )
        self.assertRedirects(response, reverse("show_signatures", args=[pid]))
        self.assertTemplateUsed(response, "signatures/data.html")
        messages = response.context["messages"]
        self.assertGreaterEqual(len(messages), 1)
        ThereIsAnyError = False
        for msg in messages:
            if msg.level == constants.ERROR:
                ThereIsAnyError = True
        self.assertEqual(ThereIsAnyError, False)
