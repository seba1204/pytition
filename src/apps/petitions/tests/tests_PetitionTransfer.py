from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.organizations.models import Organization
from apps.petition.models import Permission, Petition, PytitionUser
from apps.petitions.routes import PetitionsRoute

users = ["julia", "john", "max", "sarah"]
orgs = ["RAP", "Greenpeace", "Attac", "Les Amis de la Terre"]

org_members = {
    "RAP": ["julia"],
    "Les Amis de la Terre": ["julia", "max"],
    "Attac": ["john"],
}


class PetitionCreateWizardViewTest(TestCase):
    """Test PetitionCreateWizard view."""

    @classmethod
    def setUpTestData(cls) -> None:
        User = get_user_model()
        for org in orgs:
            o = Organization.objects.create(name=org)
            o.save()
        for user in users:
            u = User.objects.create_user(user, password=user)
            u.first_name = user
            u.last_name = user + "Last"
            u.save()
        for orgname, member_usernames in org_members.items():
            org_obj = Organization.objects.get(name=orgname)
            for username in member_usernames:
                user_obj = PytitionUser.objects.get(user__username=username)
                org_obj.members.add(user_obj)
                permission = Permission.objects.get(organization=org_obj, user=user_obj)
                permission.can_modify_permissions = True
                permission.save()

        # give julia can_modify_petitions permission
        # on "Les Amis de la Terre" organization
        user_obj = PytitionUser.objects.get(user__username="julia")
        org_obj = Organization.objects.get(name="Les Amis de la Terre")

        perm = Permission.objects.get(organization=org_obj, user=user_obj)
        perm.can_modify_petitions = True
        perm.save()

    def login(self, name: str, password: str | None = None) -> PytitionUser:
        self.client.login(username=name, password=password if password else name)
        self.pu = PytitionUser.objects.get(user__username=name)
        return self.pu

    def logout(self) -> None:
        self.client.logout()

    def test_model_transfer_method(self) -> None:
        org = Organization.objects.get(name="Les Amis de la Terre")
        user = PytitionUser.objects.get(user__username="julia")

        user_petition = Petition.objects.create(title="Petition 1", user=user)
        self.assertEqual(user_petition.user, user)
        self.assertEqual(user_petition.org, None)

        user_petition.transfer_to(org=org)
        self.assertEqual(user_petition.user, None)
        self.assertEqual(user_petition.org, org)

        user_petition.transfer_to(user=user)
        self.assertEqual(user_petition.user, user)
        self.assertEqual(user_petition.org, None)

        with self.assertRaises(ValueError):
            user_petition.transfer_to()
            user_petition.transfer_to(org=org, user=user)

    def test_transfer_view(self) -> None:
        self.login("julia")
        org = Organization.objects.get(name="Les Amis de la Terre")
        user = PytitionUser.objects.get(user__username="julia")
        user_petition = Petition.objects.create(title="Petition 1", user=user)
        url = reverse(PetitionsRoute.TRANSFER, args=[user_petition.id])

        response = self.client.post(
            url,
            data={"new_owner_type": "org", "new_owner_name": org.slugname},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        user_petition = Petition.objects.get(id=user_petition.id)
        self.assertEqual(user_petition.org, org)

        response = self.client.post(
            url,
            data={"new_owner_type": "user", "new_owner_name": user.user.username},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        user_petition = Petition.objects.get(id=user_petition.id)
        self.assertEqual(user_petition.user, user)

        with override_settings(DISABLE_USER_PETITION=True):
            user_petition = Petition.objects.create(title="Petition 1", org=org)
            response = self.client.post(
                url,
                data={"new_owner_type": "user", "new_owner_name": user.user.username},
                follow=True,
            )
            self.assertContains(
                response,
                "Users are not allowed to transfer petitions to "
                "organizations on this instance.",
            )
            user_petition = Petition.objects.get(id=user_petition.id)
            self.assertIsNone(user_petition.user)
