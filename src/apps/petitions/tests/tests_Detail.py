from django.test import TestCase
from django.urls import reverse

from apps.core.tests.utils import add_default_data
from apps.petitions.models import Petition
from apps.petitions.routes import PetitionsRoute


class DetailViewTest(TestCase):
    """Test detail view."""

    @classmethod
    def setUpTestData(cls) -> None:
        add_default_data()

    def test_DetailOk(self) -> None:
        petition = Petition.objects.filter(published=True).first()
        self.assertIsNotNone(petition)
        if petition is None:
            return
        response = self.client.get(reverse(PetitionsRoute.DETAIL, args=[petition.id]))
        self.assertEqual(response.status_code, 200)
