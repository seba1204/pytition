from django.contrib.auth.decorators import login_required
from django.http import (
    HttpRequest,
    JsonResponse,
)
from django.utils.translation import gettext as _

from apps.accounts.services import get_session_user
from apps.petition.models import Organization, PytitionUser
from apps.presets.models import PetitionTemplate


# /presets/<int:preset_id>/fav
# Set a template as favorite
@login_required
def toggle_fav(request: HttpRequest, preset_id: int) -> JsonResponse:
    pytitionuser: PytitionUser = get_session_user(request)
    owner: PytitionUser | Organization | None

    if not preset_id:
        return JsonResponse({}, status=500)

    try:
        template = PetitionTemplate.objects.get(pk=preset_id)
    except PetitionTemplate.DoesNotExist:
        return JsonResponse({}, status=404)

    owner = template.org if template.owner_type == "org" else template.user

    if not owner:
        return JsonResponse({}, status=500)

    if isinstance(owner, Organization):
        if owner not in pytitionuser.organization_set.all():
            return JsonResponse({}, status=403)  # Forbidden
    elif isinstance(owner, PytitionUser) and owner != pytitionuser:
        return JsonResponse(
            {"msg": _("You are not allowed to change this user's default template")},
            status=403,
        )

    if owner.default_template == template:
        owner.default_template = None
    else:
        owner.default_template = template
    owner.save()

    return JsonResponse({})
