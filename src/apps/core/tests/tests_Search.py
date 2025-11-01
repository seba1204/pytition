from django.test import TestCase
from django.urls import reverse

from apps.core.routes import SearchRoute


class SearchViewTest(TestCase):
    """Test search view."""

    def test_SearchOk(self) -> None:
        response = self.client.get(reverse(SearchRoute.SEARCH))
        self.assertEqual(response.status_code, 200)

    def test_SearchWithQueryOk(self) -> None:
        response = self.client.get(reverse(SearchRoute.SEARCH) + "?q=petition")
        self.assertEqual(response.status_code, 200)
