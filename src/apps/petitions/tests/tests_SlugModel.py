from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import PytitionUser
from apps.petitions.models import Petition, SlugModel


class SlugModelTest(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        u = User.objects.create_user("julia", password="julia")

    def test_autocreateSlug(self) -> None:
        pu = PytitionUser.objects.get(user__username="julia")
        self.assertEqual(SlugModel.objects.count(), 0)
        p = Petition.objects.create(title="Petition1", user=pu)
        self.assertEqual(Petition.objects.count(), 1)
        self.assertEqual(SlugModel.objects.count(), 1)

    def test_createSlug(self) -> None:
        pu = PytitionUser.objects.get(user__username="julia")
        p = Petition.objects.create(title="Petition1", user=pu)
        self.assertEqual(Petition.objects.count(), 1)
        self.assertEqual(SlugModel.objects.count(), 1)
        p.add_slug("this-is-a-cool-slug")
        self.assertEqual(SlugModel.objects.count(), 2)

    def test_SlugShouldBeUniq(self) -> None:
        pu = PytitionUser.objects.get(user__username="julia")
        p = Petition.objects.create(title="Petition1", user=pu)
        self.assertEqual(Petition.objects.count(), 1)
        self.assertEqual(SlugModel.objects.count(), 1)
        p.add_slug("this-is-a-cool-slug")
        self.assertEqual(SlugModel.objects.count(), 2)
        # p.add_slug('this-is-a-cool-slug')
        self.assertRaises(ValueError, p.add_slug, "this-is-a-cool-slug")
        self.assertEqual(SlugModel.objects.count(), 2)

    def test_SlugDelete(self) -> None:
        pu = PytitionUser.objects.get(user__username="julia")
        p = Petition.objects.create(title="Petition1", user=pu)
        self.assertEqual(Petition.objects.count(), 1)
        self.assertEqual(SlugModel.objects.count(), 1)
        p.add_slug("this-is-a-cool-slug")
        self.assertEqual(SlugModel.objects.count(), 2)
        p.del_slug("this-is-a-cool-slug")
        self.assertEqual(SlugModel.objects.count(), 1)
