from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.petition.models import (
    Organization,
    PytitionUser,
)
from apps.presets.models import PetitionTemplate


class PetitionTemplateTest(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        _u = User.objects.create_user("julia", password="julia")
        _org = Organization.objects.create(name="RAP")

    def test_createUserPetitionTemplate(self) -> None:
        self.assertEqual(PetitionTemplate.objects.count(), 0)
        pu = PytitionUser.objects.get(user__username="julia")
        PetitionTemplate.objects.create(name="Default", user=pu)
        self.assertEqual(PetitionTemplate.objects.count(), 1)

    def test_createOrgPetitionTemplate(self) -> None:
        self.assertEqual(PetitionTemplate.objects.count(), 0)
        org = Organization.objects.first()
        PetitionTemplate.objects.create(name="Default", org=org)
        self.assertEqual(PetitionTemplate.objects.count(), 1)

    def test_createPetitionTemplateRefused(self) -> None:
        org = Organization.objects.first()
        pu = PytitionUser.objects.get(user__username="julia")
        self.assertEqual(PetitionTemplate.objects.count(), 0)
        self.assertRaises(
            Exception, PetitionTemplate.objects.create, name="PetitionTemplate"
        )
        self.assertEqual(PetitionTemplate.objects.count(), 0)
        self.assertRaises(
            Exception,
            PetitionTemplate.objects.create,
            name="PetitionTemplate",
            user=pu,
            org=org,
        )
        self.assertEqual(PetitionTemplate.objects.count(), 0)

    def test_owner_type(self) -> None:
        org = Organization.objects.first()
        pu = PytitionUser.objects.get(user__username="julia")
        p1 = PetitionTemplate.objects.create(name="PetitionTemplate", org=org)
        self.assertEqual("org", p1.owner_type)
        p2 = PetitionTemplate.objects.create(name="PetitionTemplate", user=pu)
        self.assertEqual("user", p2.owner_type)
