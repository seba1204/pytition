from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.petition.models import Petition


# FIXME: this check only remove medias not referenced in petitions texts or
# twitter images, but, in the future, other models may reference medias too
# cf. ticket #31
class Command(BaseCommand):
    """Find orphans medias in media root."""

    def handle(self, *args: object, **opts: object) -> None:
        media_root = Path(settings.MEDIA_ROOT)
        all_petition = list(Petition.objects.all())
        if all_petition:
            last_petition = all_petition[-1]

        for media in media_root.glob("**/*.*"):
            media_str = str(media)
            if all_petition:
                for petition in all_petition:
                    if (
                        media_str in petition.text
                        or media_str in petition.twitter_image
                    ):
                        break
                    if petition == last_petition:
                        print(media_str)
            else:
                print(media_str)
