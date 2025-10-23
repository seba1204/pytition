from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse

from apps.petition.helpers import get_session_user
from apps.petition.models import Permission
from apps.petitions.helpers import petition_from_id


# /<int:petition_id>/publish
# Publish a petition
@login_required
def publish(request: HttpRequest, petition_id: int) -> JsonResponse:
    """
    Publish a petition.

    Parameters:
    -----------
    request : HttpRequest
        The HTTP request object.
    petition_id : int
        The ID of the petition to publish.
    Returns:
    --------
    JsonResponse
        The JSON response indicating success or failure.
    """
    pytitionuser = get_session_user(request)
    petition = petition_from_id(petition_id)

    if petition.owner_type == "user":
        if petition.user == pytitionuser:
            petition.publish()
            return JsonResponse({})
        else:
            # Petition owned by someone else
            return JsonResponse({}, status=403)
    else:
        # Check if the user has permission over this org
        try:
            user_perms = Permission.objects.get(
                organization=petition.org, user=pytitionuser
            )
            if user_perms.can_modify_petitions:
                petition.publish()
                return JsonResponse({})
            else:
                return JsonResponse({}, status=403)
        except Permission.DoesNotExist:
            return JsonResponse({}, status=403)
