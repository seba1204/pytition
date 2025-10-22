from django.test import TestCase
from django.urls import reverse

from apps.core.tests.utils import add_default_data
from apps.petition.models import PytitionUser


class GetCsvSignatureViewTest(TestCase):
    """Test get_csv_signature view."""

    @classmethod
    def setUpTestData(cls) -> None:
        add_default_data()

    def login(self, name: str, password: str | None = None) -> PytitionUser:
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self) -> None:
        self.client.logout()

    def test_GetCsvSignatureOk(self) -> None:
        julia = self.login("julia")
        petition = julia.petition_set.first()

        self.assertIsNotNone(petition)
        if petition is None:
            return
        response = self.client.get(reverse("get_csv_signature", args=[petition.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        # TODO: add some csv parsing of the response

    def test_GetConfirmedSignatureOk(self) -> None:
        julia = self.login("julia")
        petition = julia.petition_set.first()

        self.assertIsNotNone(petition)
        if petition is None:
            return
        response = self.client.get(
            reverse("get_csv_confirmed_signature", args=[petition.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        # TODO: add some csv parsing of the response
