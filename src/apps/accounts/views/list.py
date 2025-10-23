from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import (
    HttpRequest,
    JsonResponse,
)

from apps.petition.models import (
    PytitionUser,
)


# /get_user_list
# get the list of users
@login_required
def user_list(request: HttpRequest) -> JsonResponse:
    q = request.GET.get("q", "")
    if q != "":
        users = PytitionUser.objects.filter(
            Q(user__username__contains=q)
            | Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
        ).all()
    else:
        users = PytitionUser.objects.none()

    userdict = {
        "values": [user.user.username for user in users],
    }
    return JsonResponse(userdict)
