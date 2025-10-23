from django.test import TestCase
from django.urls import reverse

from apps.consents.routes import ConsentRoute
from apps.core.tests.utils import add_default_data
from apps.petition.models import Petition, PytitionUser, Signature


class GoSendConfirmationEmailViewTest(TestCase):
    """Test go_send_confirmation_email view."""

    @classmethod
    def setUpTestData(cls) -> None:
        add_default_data()

    def login(self, name: str, password: str | None = None) -> PytitionUser:
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self) -> None:
        self.client.logout()

    def test_GoSendConfirmationEmailViewLoginKO(self) -> None:
        self.logout()
        data = {
            "first_name": "Alan",
            "last_name": "John",
            "email": "alan@john.org",
            "subscribed_to_mailinglist": False,
        }
        petition = Petition.objects.filter(published=True).first()
        self.assertIsNotNone(petition)
        if petition is None:
            return
        response = self.client.post(
            reverse("create_signature", args=[petition.id]), data, follow=True
        )
        self.assertRedirects(response, petition.url)
        signature = Signature.objects.filter(petition=petition).first()

        self.assertIsNotNone(signature)
        if signature is None:
            return
        response = self.client.get(
            reverse(ConsentRoute.RESEND, args=[signature.id]), follow=True
        )
        self.assertRedirects(
            response,
            reverse("login")
            + "?next="
            + reverse(ConsentRoute.RESEND, args=[signature.id]),
        )

    def test_GoSendConfirmationEmailViewLoginOK(self) -> None:
        self.login("admin")
        data = {
            "first_name": "Alan",
            "last_name": "John",
            "email": "alan@john.org",
            "subscribed_to_mailinglist": False,
        }
        app_label = Signature._meta.app_label
        petition = Petition.objects.filter(published=True).first()

        self.assertIsNotNone(petition)
        if petition is None:
            return
        response = self.client.post(
            reverse("create_signature", args=[petition.id]), data, follow=True
        )
        self.assertRedirects(response, petition.url)
        signature = Signature.objects.filter(petition=petition).first()
        self.assertIsNotNone(signature)
        if signature is None:
            return
        response = self.client.get(
            reverse(ConsentRoute.RESEND, args=[signature.id]), follow=True
        )
        self.assertRedirects(
            response,
            reverse(f"admin:{app_label}_signature_change", args=[signature.id]),
        )
