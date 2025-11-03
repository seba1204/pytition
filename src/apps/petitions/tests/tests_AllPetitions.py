from django.test import TestCase
from django.urls import reverse

from apps.petitions.routes import PetitionsRoute


class AllPetitionsViewTest(TestCase):
    """Test all_petitions view."""

    def test_allPetitionsOk(self) -> None:
        response = self.client.get(reverse(PetitionsRoute.ALL_PETITIONS))
        self.assertEqual(response.status_code, 302)
