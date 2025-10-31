from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Permission
from apps.organizations.models import Organization
from apps.petition.models import Petition, PytitionUser, SlugModel
from apps.petitions.routes import PetitionsRoute
from apps.signatures.models import Signature


class PetitionTest(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        _u = User.objects.create_user("julia", password="julia")
        _org = Organization.objects.create(name="RAP")

    def test_createUserPetition(self) -> None:
        self.assertEqual(Petition.objects.count(), 0)
        pu = PytitionUser.objects.get(user__username="julia")
        Petition.objects.create(title="Petition", user=pu)
        self.assertEqual(Petition.objects.count(), 1)

    def test_createOrgPetition(self) -> None:
        self.assertEqual(Petition.objects.count(), 0)
        org = Organization.objects.first()
        Petition.objects.create(title="Petition", org=org)
        self.assertEqual(Petition.objects.count(), 1)

    def test_createPetitionRefused(self) -> None:
        org = Organization.objects.first()
        pu = PytitionUser.objects.get(user__username="julia")
        self.assertEqual(Petition.objects.count(), 0)
        self.assertRaises(Exception, Petition.objects.create, title="Petition")  # noqa
        self.assertEqual(Petition.objects.count(), 0)
        self.assertRaises(  # noqa
            Exception,
            Petition.objects.create,
            title="Petition",
            user=pu,
            org=org,
        )
        self.assertEqual(Petition.objects.count(), 0)

    def test_owner_type(self) -> None:
        org = Organization.objects.first()
        pu = PytitionUser.objects.get(user__username="julia")
        p1 = Petition.objects.create(title="Petition", org=org)
        self.assertEqual("org", p1.owner_type)
        p2 = Petition.objects.create(title="Petition", user=pu)
        self.assertEqual("user", p2.owner_type)

    def test_Petition_url(self) -> None:
        # If there is no slug, returns detail
        pu = PytitionUser.objects.get(user__username="julia")
        p = Petition.objects.create(title="Petition", user=pu)
        self.assertEqual(
            p.url, reverse("slug_show_petition", args=[pu.username, "petition"])
        )
        # This should never happen but testing just in case
        s = SlugModel.objects.first()
        self.assertIsNotNone(s)
        if s is None:
            return
        s.delete()
        self.assertEqual(p.url, reverse(PetitionsRoute.DETAIL, args=[p.id]))
        # Create a slug
        # p.add_slug('foobar')

    def test_PetitionDelete(self) -> None:
        # Deleting a petition should delete related slugs and signatures
        pu = PytitionUser.objects.get(user__username="julia")
        p = Petition.objects.create(title="Petition", user=pu)
        self.assertEqual(Petition.objects.count(), 1)
        self.assertEqual(SlugModel.objects.count(), 1)
        p.delete()
        self.assertEqual(PytitionUser.objects.count(), 1)
        self.assertEqual(Petition.objects.count(), 0)
        self.assertEqual(SlugModel.objects.count(), 0)

    def testPetitionPublish(self) -> None:
        pu = PytitionUser.objects.get(user__username="julia")
        p = Petition.objects.create(title="Petition", user=pu)
        self.assertEqual(p.published, False)
        p.publish()
        self.assertEqual(p.published, True)
        p.unpublish()
        self.assertEqual(p.published, False)

    def test_auto_creation_salt(self) -> None:
        pu = PytitionUser.objects.get(user__username="julia")
        p = Petition.objects.create(title="Petition", user=pu)
        self.assertIsNotNone(p.salt)

    def test_is_allowed_edit(self) -> None:
        # if the petition belong to the user, yes
        pu = PytitionUser.objects.get(user__username="julia")
        p = Petition.objects.create(title="Petition", user=pu)
        self.assertEqual(p.is_allowed_to_edit(pu), True)
        # else no
        User = get_user_model()
        _u = User.objects.create_user("john", password="john")
        john = PytitionUser.objects.get(user__username="john")
        self.assertEqual(p.is_allowed_to_edit(john), False)
        # Now with org petitions
        rap = Organization.objects.get(name="RAP")
        p2 = Petition.objects.create(title="Petition2", org=rap)
        self.assertEqual(p2.is_allowed_to_edit(john), False)
        # If the user has no rights
        rap.members.add(john)
        self.assertEqual(p2.is_allowed_to_edit(john), True)
        perm = Permission.objects.get(organization=rap, user=john)
        perm.can_modify_petitions = False
        perm.save()
        self.assertEqual(p2.is_allowed_to_edit(john), False)

    def test_paper_signatures(self) -> None:
        pu = PytitionUser.objects.get(user__username="julia")
        p = Petition.objects.create(title="Petition", user=pu)
        p.paper_signatures_enabled = True
        p.paper_signatures = 42
        p.save()
        self.assertEqual(p.get_signature_number(), 42)
        p.paper_signatures_enabled = False
        p.save()
        self.assertEqual(p.get_signature_number(), 0)
        _s = Signature.objects.create(
            first_name="User", last_name="User", email="user@example.org", petition=p
        )
        self.assertEqual(p.get_signature_number(), 1)
        p.paper_signatures_enabled = True
        p.save()
        self.assertEqual(p.get_signature_number(), 43)
