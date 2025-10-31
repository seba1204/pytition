from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import PytitionUser
from apps.core.tests.utils import add_default_data


class GetUserListViewTest(TestCase):
    """Test get_user_list view."""

    @classmethod
    def setUpTestData(cls) -> None:
        add_default_data()

    def login(self, name: str, password: str | None = None) -> PytitionUser:
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def test_GetUserListViewOk(self) -> None:
        self.login("julia")
        response = self.client.get(reverse("get_user_list") + "?q=admin")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        values = response.json()["values"]
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0], "admin")

    def test_GetUserListViewEmptySearchOk(self) -> None:
        self.login("julia")
        response = self.client.get(reverse("get_user_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        values = response.json()["values"]
        self.assertEqual(len(values), 0)

    def test_GetUserListViewEmptyStringSearchOk(self) -> None:
        self.login("julia")
        response = self.client.get(reverse("get_user_list") + "?q=")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        values = response.json()["values"]
        self.assertEqual(len(values), 0)
