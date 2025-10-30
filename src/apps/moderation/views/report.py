from django.http import (
    HttpRequest,
    HttpResponse,
)

from apps.moderation.models import Moderation, ModerationReason
from apps.petitions.helpers import petition_from_id


# /<int:petition_id>/report/<int:reason_id>
# Report a petition to moderation
def report(
    request: HttpRequest, petition_id: int, reason_id: int | None = None
) -> HttpResponse:
    petition = petition_from_id(petition_id)
    if reason_id:
        try:
            reason = ModerationReason.objects.get(pk=reason_id)
        except Exception:
            return HttpResponse(status=500)

    if reason_id:
        Moderation.objects.create(petition=petition, reason=reason)
    else:
        Moderation.objects.create(petition=petition)
    return HttpResponse(status=200)
