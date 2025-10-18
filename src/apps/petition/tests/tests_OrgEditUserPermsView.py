from django.test import TestCase
from django.urls import reverse

from apps.petition.models import PytitionUser

from .utils import add_default_data


class OrgEditUserPermsViewTest(TestCase):
    """Test org_edit_user_perms view"""

    @classmethod
    def setUpTestData(cls) -> None:
        add_default_data()

    def login(self, name: str, password: str | None = None) -> PytitionUser:
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self) -> None:
        self.client.logout()

    def test_OrgEditUserPermsViewOk(self) -> None:
        julia = self.login("julia")
        response = self.client.get(
            reverse(
                "org_edit_user_perms",
                kwargs={"orgslugname": "rap", "user_name": "julia"},
            )
        )
        self.assertEqual(response.status_code, 200)
