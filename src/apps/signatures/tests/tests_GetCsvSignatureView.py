"""Test GetCsvSignatureView."""

from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import PytitionUser
from apps.core.tests.utils import add_default_data
from apps.signatures.routes import SignatureRoute


class GetCsvSignatureViewTest(TestCase):
    """Test export view."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data for the whole TestCase."""
        add_default_data()

    def login(self, name: str, password: str | None = None) -> PytitionUser:
        """Login a user and return the PytitionUser."""
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self) -> None:
        """Logout the current user."""
        self.client.logout()

    def test_GetCsvSignatureOk(self) -> None:
        """Test export csv view."""
        julia = self.login("julia")
        petition = julia.petition_set.first()

        self.assertIsNotNone(petition)
        if petition is None:
            return
        response = self.client.get(reverse(SignatureRoute.EXPORT, args=[petition.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        # TODO: [#80] add some csv parsing of the response

    def test_GetConfirmedSignatureOk(self) -> None:
        """Test export csv view with confirmed signatures only."""
        julia = self.login("julia")
        petition = julia.petition_set.first()

        self.assertIsNotNone(petition)
        if petition is None:
            return
        response = self.client.get(
            reverse(SignatureRoute.EXPORT, args=[petition.id]),
            data={"confirmed": "true"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        # TODO: [#80] add some csv parsing of the response
