from django.contrib.auth import get_user_model

from apps.accounts.models import Permission, PytitionUser
from apps.organizations.models import Organization
from apps.petition.models import Petition


def add_default_data() -> None:
    """Add default data for test purpose."""
    users = ["julia", "john", "max", "sarah"]
    orgs = ["RAP", "Greenpeace", "Attac", "Les Amis de la Terre", "Alternatiba"]
    user_published_petitions = {"john": 0, "sarah": 0, "julia": 5, "max": 10}
    user_unpublished_petitions = {"john": 0, "sarah": 5, "julia": 0, "max": 10}
    org_published_petitions = {
        "RAP": 0,
        "Les Amis de la Terre": 0,
        "Greenpeace": 1,
        "Attac": 2,
        "Alternatiba": 1,
    }
    org_unpublished_petitions = {
        "RAP": 0,
        "Les Amis de la Terre": 1,
        "Greenpeace": 0,
        "Attac": 2,
        "Alternatiba": 1,
    }
    org_members = {
        "RAP": ["julia"],
        "Les Amis de la Terre": ["julia", "max"],
        "Attac": ["john"],
        "Alternatiba": ["julia", "max"],
    }
    org_admins = {
        "RAP": ["julia"],
        "Les Amis de la Terre": ["julia"],
        "Attac": ["john"],
        "Alternatiba": ["julia", "max"],
    }
    User = get_user_model()
    for org in orgs:
        o = Organization.objects.create(name=org)
        for i in range(org_published_petitions[org]):
            Petition.objects.create(published=True, title=f"Petition A{i}", org=o)
        for i in range(org_unpublished_petitions[org]):
            Petition.objects.create(published=False, title=f"Petition B{i}", org=o)
    for user in users:
        u = User.objects.create_user(user, password=user)
        u.first_name = user
        u.save()
        pu = PytitionUser.objects.get(user__username=user)
        for i in range(user_published_petitions[user]):
            Petition.objects.create(published=True, title=f"Petition C{i}", user=pu)
        for i in range(user_unpublished_petitions[user]):
            Petition.objects.create(published=False, title=f"Petition D{i}", user=pu)
    for orgname, usernames in org_members.items():
        org_obj = Organization.objects.get(name=orgname)
        for username in usernames:
            user_obj = PytitionUser.objects.get(user__username=username)
            org_obj.members.add(user_obj)
            p = Permission.objects.get(organization=org_obj, user=user_obj)
            p.set_all(False)
            p.can_create_petitions = True
            p.save()
    for orgname, usernames in org_admins.items():
        org_obj = Organization.objects.get(name=orgname)
        for username in usernames:
            user_obj = PytitionUser.objects.get(user__username=username)
            perms = Permission.objects.get(organization=org_obj, user=user_obj)
            perms.set_all(True)
            perms.save()

    User.objects.create_user(
        "admin", password="admin", is_staff=True, is_superuser=True
    )
