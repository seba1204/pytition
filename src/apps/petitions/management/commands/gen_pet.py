"""Management command to generate petitions for users or organizations."""

import logging

from django.core.management.base import BaseCommand, CommandParser

from apps.accounts.models import PytitionUser
from apps.organizations.models import Organization
from apps.petitions.models import Petition

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Generate petitions for a user or an org.

    ./manage.py gen_pet --user username > Generate a petition for user:username
    ./manage.py gen_pet --orga orgname -n 10 > Generate 10 petitions for org:orgname
    """

    # TODO: [#81] Improve creation by not naming all petitions the same way
    # (idempotence)

    def add_arguments(self, parser: CommandParser) -> None:
        """Add command line arguments."""
        parser.add_argument("--user", type=str)
        parser.add_argument("--orga", type=str)
        parser.add_argument("--number", "-n", type=int, default=1)

    def handle(self, *args: object, **opts: object) -> None:
        """Handle the command to generate petitions."""
        opts = dict(opts)  # Ensure opts is a dict
        if not opts["orga"] and not opts["user"]:
            logger.error("You must either specify --orga or --user")
            return
        data = {
            "title": "Petition",
            "text": "content",
            "org_twitter_handle": "@RAP_Asso",
            "published": True,
        }
        if opts["orga"]:
            try:
                orga = Organization.objects.get(name=opts["orga"])
                data.update({"org": orga})
            except Organization.DoesNotExist:
                logger.error("%s org not found.", opts["orga"])
                return
        elif opts["user"]:
            try:
                user = PytitionUser.objects.get(user__username=opts["user"])
                data.update({"user": user})
            except PytitionUser.DoesNotExist:
                logger.error("%s user not found.", opts["user"])
                return
        num = opts.get("number")
        if not isinstance(num, int) or num < 1:
            num = 1
        for i in range(1, num + 1):
            data["title"] = f"Petition {i}"
            Petition.objects.create(**data)
        logger.info("%d petitions created", opts["number"])
