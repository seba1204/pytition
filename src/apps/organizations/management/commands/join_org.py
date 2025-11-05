"""Management command to make a user join an organization."""

import logging

from django.core.management.base import BaseCommand, CommandParser

from apps.accounts.models import Permission, PytitionUser
from apps.organizations.models import Organization

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Make a user join an orga.

    ./manage.py join_org username orgname > Make user:username join org:orgname
    """

    def add_arguments(self, parser: CommandParser) -> None:
        """Add command arguments for username and organization name."""
        parser.add_argument("username", type=str)
        parser.add_argument("org", type=str)

    def handle(self, *args: object, **opts: object) -> None:
        """Add the specified user to the specified organization with full
        permissions."""
        try:
            user = PytitionUser.objects.get(user__username=opts["username"])
        except PytitionUser.DoesNotExist:
            logger.error("%s user does not exist", opts["username"])
            return
        try:
            org = Organization.objects.get(name=opts["org"])
        except Organization.DoesNotExist:
            logger.error("%s org does not exist", opts["org"])
            return
        org.members.add(user)
        perms, created = Permission.objects.get_or_create(organization=org, user=user)
        perms.can_add_members = True
        perms.can_remove_members = True
        perms.can_create_petitions = True
        perms.can_modify_petitions = True
        perms.can_delete_petitions = True
        perms.can_view_signatures = True
        perms.can_modify_signatures = True
        perms.can_delete_signatures = True
        perms.can_modify_permissions = True
        perms.save()
        if created:
            logger.info("%s user joined %s org", user, org)
        else:
            logger.info("%s user already joined %s org", user, org)
