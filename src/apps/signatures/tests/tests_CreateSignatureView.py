"""Tests for CreateSignatureView."""

from django.test import TestCase
from django.urls import reverse

from apps.core.tests.utils import add_default_data
from apps.petitions.models import Petition
from apps.signatures.models import Signature
from apps.signatures.routes import SignatureRoute


class CreateSignatureViewTest(TestCase):
    """Test new signature view."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the whole TestCase."""
        add_default_data()

    def test_CreateSignaturePOSTOk(self) -> None:
        """Test creating a signature with valid data."""
        data = {
            "first_name": "Alan",
            "last_name": "John",
            "email": "alan@john.org",
            "phone": "0605040302",
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
        self.assertEqual(signature.email, "alan@john.org")
        self.assertEqual(signature.phone, "+33605040302")
        self.assertEqual(signature.first_name, "Alan")
        self.assertEqual(signature.last_name, "John")
        self.assertEqual(signature.subscribed_to_mailinglist, False)

    def test_CreateSignaturePOSTNok(self) -> None:
        """Test creating a signature with invalid data."""
        data = {
            "first_name": "Alan",
            "last_name": "",
            "email": "wrong-mail.org",
            "phone": "060504030201",
        }
        petition = Petition.objects.filter(published=True).first()
        self.assertIsNotNone(petition)
        if petition is None:
            return
        response = self.client.post(
            reverse(SignatureRoute.NEW, args=[petition.id]), data
        )
        self.assertEqual(Signature.objects.count(), 0)
        self.assertTemplateUsed(response, "petitions/detail.html")
        self.assertContains(response, "This field is required")
        self.assertContains(response, "Enter a valid phone number")
        self.assertContains(response, "Enter a valid email address")

    def test_CreateSignatureGETOk(self) -> None:
        """Test accessing the signature creation page."""
        petition = Petition.objects.filter(published=True).first()
        self.assertIsNotNone(petition)
        if petition is None:
            return
        response = self.client.get(
            reverse(SignatureRoute.NEW, args=[petition.id]), follow=True
        )
        self.assertRedirects(response, petition.url)
