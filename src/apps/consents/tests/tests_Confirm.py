from django.test import TestCase
from django.urls import reverse

from apps.core.tests.utils import add_default_data
from apps.petitions.models import Petition
from apps.signatures.models import Signature
from apps.signatures.routes import SignatureRoute


class ConfirmViewTest(TestCase):
    """Test confirm view."""

    @classmethod
    def setUpTestData(cls) -> None:
        add_default_data()

    def test_ConfirmOk(self) -> None:
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
            reverse(SignatureRoute.NEW, args=[petition.id]), data, follow=True
        )
        self.assertRedirects(response, petition.url)
        signature = Signature.objects.filter(petition=petition).first()
        self.assertIsNotNone(signature)
        if signature is None:
            return
        self.assertEqual(signature.confirmed, False)
        confirm_hash = signature.confirmation_hash
        response = self.client.get(
            reverse(SignatureRoute.CONFIRM, args=[petition.id, confirm_hash]),
            follow=True,
        )
        self.assertRedirects(response, petition.url)
        signature = Signature.objects.filter(petition=petition).first()

        self.assertIsNotNone(signature)
        if signature is None:
            return
        self.assertEqual(signature.confirmed, True)
