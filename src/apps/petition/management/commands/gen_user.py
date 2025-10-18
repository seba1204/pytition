import logging

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandParser

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Generate a user

    ./manage.py gen_user username password -fn User -ln James
    > Generate user:username with password as password, and named User James
    """

    help = "Create a new user"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("username", type=str)
        parser.add_argument("password", type=str)
        parser.add_argument("--first-name", "-fn", dest="first_name", type=str)
        parser.add_argument("--last-name", "-ln", dest="last_name", type=str)

    def handle(self, *args: object, **opts: object) -> None:
        created = False

        pw = opts.get("password")
        if not isinstance(pw, str) or not pw:
            logger.error("You must provide a valid password")
            return
        username = opts.get("username")
        if not isinstance(username, str) or not username:
            logger.error("You must provide a valid username")
            return

        firstname = opts.get("first_name", "")
        if firstname is not None and not isinstance(firstname, str):
            firstname = ""
        lastname = opts.get("last_name", "")
        if lastname is not None and not isinstance(lastname, str):
            lastname = ""
        lastname = str(lastname)
        firstname = str(firstname)

        try:
            user = User.objects.get(username=username)
            user.set_password(pw)
        except User.DoesNotExist:
            user = User.objects.create_user(username, password=pw)
            created = True
        user.is_staff = True
        user.first_name = firstname
        user.last_name = lastname
        user.save()
        if created:
            logger.info("%s user created", user)
        else:
            logger.info("%s user already created", user)
