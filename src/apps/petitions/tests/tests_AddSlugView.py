from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify

from apps.accounts.models import PytitionUser
from apps.core.tests.utils import add_default_data
from apps.petitions.routes import PetitionsRoute, PetitionsSlugRoute


class AddSlugViewTest(TestCase):
    """Test Slug creation view."""

    @classmethod
    def setUpTestData(cls) -> None:
        add_default_data()

    def login(self, name: str, password: str | None = None) -> PytitionUser:
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self) -> None:
        self.client.logout()

    def tearDown(self) -> None:
        # Clean up run after every test method.
        pass

    def test_addSlugOK(self) -> None:
        max = self.login("max")
        petition = max.petition_set.all()[0]
        slugtext = "coucou ceci est un slug"
        data = {
            "slugtext": slugtext,
        }
        previous_slug_count = petition.slugmodel_set.count()
        response = self.client.post(
            reverse(PetitionsSlugRoute.ADD, args=[petition.id]), data, follow=True
        )
        self.assertRedirects(
            response,
            reverse(PetitionsRoute.EDIT, args=[petition.id])
            + "#tab_social_network_form",
        )
        slug_count = petition.slugmodel_set.count()
        self.assertEqual(slug_count, previous_slug_count + 1)
        new_slug = petition.slugmodel_set.get(slug=slugify(slugtext))
        self.assertEqual(new_slug.slug, slugify(slugtext))

    def test_addSlugAlreadyExistsKO(self) -> None:
        max = self.login("max")
        petition = max.petition_set.all()[0]
        slugtext = "coucou ceci est un slug"
        data = {
            "slugtext": slugtext,
        }
        previous_slug_count = petition.slugmodel_set.count()
        # first time slug insertion
        response = self.client.post(
            reverse(PetitionsSlugRoute.ADD, args=[petition.id]), data, follow=True
        )
        self.assertRedirects(
            response,
            reverse(PetitionsRoute.EDIT, args=[petition.id])
            + "#tab_social_network_form",
        )
        slug_count = petition.slugmodel_set.count()
        self.assertEqual(slug_count, previous_slug_count + 1)
        new_slug = petition.slugmodel_set.get(slug=slugify(slugtext))
        self.assertEqual(new_slug.slug, slugify(slugtext))
        # second time slug insertion (should fail)
        with self.assertRaises(ValueError):
            response = self.client.post(
                reverse(PetitionsSlugRoute.ADD, args=[petition.id]), data, follow=True
            )
            self.assertRedirects(
                response,
                reverse(PetitionsRoute.EDIT, args=[petition.id])
                + "#tab_social_network_form",
            )
        slug_count = petition.slugmodel_set.count()
        self.assertEqual(slug_count, previous_slug_count + 1)
        new_slug = petition.slugmodel_set.get(slug=slugify(slugtext))
        self.assertEqual(new_slug.slug, slugify(slugtext))
