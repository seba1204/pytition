from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse

from apps.petition.helpers import get_session_user, petition_from_id
from apps.petition.models import Permission


# /<int:petition_id>/delete
# Delete a petition
@login_required
def delete(request: HttpRequest, petition_id: int) -> JsonResponse:
    petition = petition_from_id(petition_id)
    pytitionuser = get_session_user(request)

    if petition.owner_type == "user":
        if petition.user == pytitionuser:
            petition.delete()
            return JsonResponse({})
        else:
            return JsonResponse({}, status=403)
    else:  # an organization owns the petition
        user_perms = Permission.objects.get(
            organization=petition.org, user=pytitionuser
        )
        if user_perms.can_delete_petitions:
            petition.delete()
            return JsonResponse({})
        else:
            return JsonResponse({}, status=403)
