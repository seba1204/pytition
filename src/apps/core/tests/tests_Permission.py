from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.organizations.models import Organization
from apps.petition.models import Permission, PytitionUser


class PermissionTest(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        u = User.objects.create_user("julia", password="julia")
        org = Organization.objects.create(name="RAP")

    def test_createPermission(self) -> None:
        self.assertEqual(Permission.objects.count(), 0)
        org = Organization.objects.get(name="RAP")
        pu = PytitionUser.objects.get(user__username="julia")
        org.members.add(pu)
        self.assertEqual(Permission.objects.count(), 1)
        p = Permission.objects.first()
        self.assertIsNotNone(p)
        if p is None:
            return
        # By default set the following values
        self.assertEqual(p.can_add_members, False)
        self.assertEqual(p.can_remove_members, False)
        self.assertEqual(p.can_create_petitions, True)
        self.assertEqual(p.can_modify_petitions, True)
        self.assertEqual(p.can_delete_petitions, False)
        self.assertEqual(p.can_create_templates, True)
        self.assertEqual(p.can_modify_templates, True)
        self.assertEqual(p.can_delete_templates, False)
        self.assertEqual(p.can_view_signatures, False)
        self.assertEqual(p.can_modify_signatures, False)
        self.assertEqual(p.can_delete_signatures, False)
        self.assertEqual(p.can_modify_permissions, False)

    def test_to_string(self) -> None:
        self.assertEqual(Permission.objects.count(), 0)
        org = Organization.objects.get(name="RAP")
        pu = PytitionUser.objects.get(user__username="julia")
        org.members.add(pu)
        p = Permission.objects.first()
        self.assertEqual(str(p), f"{org.name} : {pu.name}")
