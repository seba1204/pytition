from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.petition.models import (
    Organization,
    Petition,
    PytitionUser,
    Signature,
)


class SignatureTest(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        _u = User.objects.create_user("julia", password="julia")
        _org = Organization.objects.create(name="RAP")
        pu = PytitionUser.objects.get(user__username="julia")
        Petition.objects.create(title="Petition", user=pu)

    def test_createSignature(self) -> None:
        p = Petition.objects.get(title="Petition")
        self.assertEqual(Signature.objects.count(), 0)
        _s = Signature.objects.create(
            first_name="User", last_name="User", email="user@example.org", petition=p
        )
        self.assertEqual(Signature.objects.count(), 1)

    def pending_signature_requires(self) -> None:
        p = Petition.objects.get(title="Petition")
        # A signature requires a petition
        self.assertRaises(
            Signature.petition.RelatedObjectDoesNotExist,
            Signature.objects.create,
            first_name="User",
            last_name="User",
            email="user@example.org",
        )
        _s = Signature.objects.create(first_name="User", last_name="User", petition=p)
        self.assertEqual(Signature.objects.count(), 0)

    def pending_signature_should_be_uniq(self) -> None:
        _org = Organization.objects.first()
        p1 = Petition.objects.get(title="Petition")
        # p2 = Petition.objects.create(title="Petition2", org=org)
        _s1 = Signature.objects.create(
            first_name="User", last_name="User", email="user@example.org", petition=p1
        )
        _s2 = Signature.objects.create(
            first_name="User", last_name="User", email="user@example.org", petition=p1
        )
