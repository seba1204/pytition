"""Management command for moderating petitions and user accounts."""

import logging

from django.core.management.base import BaseCommand, CommandParser
from django.db.models import Count

from apps.accounts.models import PytitionUser
from apps.moderation.models import Moderation, ModerationReason
from apps.petitions.models import Petition

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    This command helps manually moderating petitions and user accounts.

    ./manage.py moderate [-a | -l] > -r "some text" : adds some text as a new moderation
    reason > -l : list petitions in decreasing order of moderation demands > -m id :
    moderate a petition > -M username : moderate a user or Organization account > -d id
    : delete a petition > -D username : delete a user or Organization account
    """

    def add_arguments(self, parser: CommandParser) -> None:
        """Define command-line arguments for the moderation command."""
        parser.add_argument("-r", "--add-reason", type=str)
        parser.add_argument("-R", "--delete-reason", type=str)
        parser.add_argument("-l", "--list", action="store_true")
        parser.add_argument("-p", "--moderate-petition", type=int)
        parser.add_argument("-u", "--moderate-user", type=str)
        parser.add_argument("-d", "--delete-petition", type=int)
        parser.add_argument("-D", "--delete-user", type=str)
        parser.add_argument("-P", "--unmoderate-petition", type=int)
        parser.add_argument("-U", "--unmoderate-user", type=str)

    # TODO: refactor into smaller methods
    def handle(self, *args: object, **opts: object) -> None:  # noqa
        """Execute the moderation command with the given options."""
        if opts["list"]:
            petitions = (
                Moderation.objects.values("petition")
                .annotate(count=Count("petition"))
                .filter(petition__moderated=False)
                .order_by("-count")
            )
            if len(petitions) == 0:
                return
            print("Number of moderation request: title [id : url]")
            for petition_data in petitions:
                petition = Petition.objects.get(pk=int(petition_data["petition"]))

        if opts["add_reason"]:
            msg = opts["add_reason"]
            ModerationReason.objects.create(msg=str(msg))
            print(f"Created reason: '{msg}'")

        if opts["delete_reason"]:
            msg = opts["delete_reason"]
            r = ModerationReason.objects.get(msg=msg)
            r.delete()
            print(f"Deleted reason: '{msg}'")

        if opts["moderate_petition"]:
            id = opts["moderate_petition"]
            if not isinstance(id, int):
                print("Invalid petition id")
                return
            petition = Petition.objects.get(pk=id)
            title = petition.title
            petition.moderate()
            petition.save()
            print(f"Petition '{title}' moderated")

        if opts["moderate_user"]:
            username = opts["moderate_user"]
            user = PytitionUser.objects.get(user__username=username)
            user.moderate()
            user.save()
            print(f"User '{username}' moderated")

        if opts["unmoderate_petition"]:
            id = opts["unmoderate_petition"]
            if not isinstance(id, int):
                print("Invalid petition id")
                return
            petition = Petition.objects.get(pk=id)
            title = petition.title
            petition.moderate(False)
            petition.save()
            print(f"Petition '{title}' un-moderated")

        if opts["unmoderate_user"]:
            username = opts["unmoderate_user"]
            user = PytitionUser.objects.get(user__username=username)
            user.moderate(False)
            user.save()
            print(f"User '{username}' un-moderated")

        if opts["delete_petition"]:
            id = opts["delete_petition"]
            if not isinstance(id, int):
                print("Invalid petition id")
                return
            petition = Petition.objects.get(pk=id)
            title = petition.title
            petition.delete()
            print(f"Petition '{title}' deleted")

        if opts["delete_user"]:
            username = opts["delete_user"]
            user = PytitionUser.objects.get(user__username=username)
            user.delete()
            print(f"User '{username}' deleted")
