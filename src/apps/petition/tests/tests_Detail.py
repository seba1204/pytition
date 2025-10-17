from django.test import TestCase
from django.urls import reverse

from apps.petition.models import Petition

from .utils import add_default_data


class DetailViewTest(TestCase):
    """Test detail view"""

    @classmethod
    def setUpTestData(cls):
        add_default_data()

    def test_DetailOk(self):
        petition = Petition.objects.filter(published=True).first()
        response = self.client.get(reverse("detail", args=[petition.id]))
        self.assertEqual(response.status_code, 200)
