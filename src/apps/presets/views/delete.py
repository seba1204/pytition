from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, JsonResponse

from apps.accounts.services import get_session_user
from apps.petition.models import PetitionTemplate
from apps.presets.services import (
    FatalPermissionError,
    ensure_user_can_delete_preset,
    get_presets_or_404,
)


@login_required
def delete(request: HttpRequest, preset_id: int) -> JsonResponse:
    """
    Delete a petition preset as the authenticated user.

    Parameters
    ----------
    request : HttpRequest
        The incoming Django HTTP request (authenticated).
    preset_id : int
        Primary key of the preset to delete.

    Returns
    -------
    JsonResponse
        Empty JSON body with appropriate HTTP status code.
    """

    # Guard: invalid ID mirrors original behavior (500). Keeping contract as requested.
    if not preset_id:
        return JsonResponse({}, status=500)

    # Lookup phase
    try:
        preset: PetitionTemplate = get_presets_or_404(preset_id)
    except PetitionTemplate.DoesNotExist:
        return JsonResponse({}, status=404)

    # Authorization phase
    pytitionuser = get_session_user(request)

    try:
        ensure_user_can_delete_preset(pytitionuser, preset)
    except PermissionDenied:
        return JsonResponse({}, status=403)
    except FatalPermissionError:
        return JsonResponse({}, status=500)

    # Execution phase
    preset.delete()
    return JsonResponse({})
