import logging
import random
import string

from django.core.management.base import BaseCommand, CommandParser

from apps.petition.models import Petition
from apps.signatures.models import Signature

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Generate signatures for petitions.

    ./manage.py gen_sig 1 > Generate a random signature for Petition:1 ./manage.py
    gen_sig "Petition Test" -n 10 > Generate 10 signatures for Petition:Petition Test if
    unique
    """

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("petition", type=str)
        parser.add_argument("--number", "-n", type=int, default=1)

    def handle(self, *args: object, **opts: object) -> None:
        petition_str = str(opts["petition"])
        if petition_str.isnumeric():
            try:
                petition = Petition.objects.get(id=int(petition_str))
            except Petition.DoesNotExist:
                logger.error("%s petition id not found.", petition_str)
                return
        else:
            petitions = Petition.objects.filter(title=opts["petition"])
            if petitions.count() > 1:
                logger.warning(
                    "Many petition match this title: %s, choose it by id: %s",
                    opts["petition"],
                    petitions.values_list("id"),
                )
                return
            if petitions.count() < 1:
                logger.error("%s petition id not found.", opts["petition"])
                return
            petition_obj = petitions.first()
            if petition_obj is None:
                logger.error("%s petition id not found.", opts["petition"])
                return
            petition = petition_obj
        num = opts.get("number")
        if not isinstance(num, int) or num < 1:
            num = 1
        for _ in range(num):
            firstname = "".join([random.choice(string.ascii_letters) for n in range(7)])
            lastname = "".join([random.choice(string.ascii_letters) for n in range(7)])
            Signature.objects.create(
                first_name=firstname.capitalize(),
                last_name=lastname.capitalize(),
                email=f"{firstname}@{lastname}.net",
                petition=petition,
                confirmed=True,
            )
        logger.info("%d signatures created.", opts["number"])
