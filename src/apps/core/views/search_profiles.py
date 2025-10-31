"""
View to search for users OR orgs.

Used for transferring petition ownership to another user or org.
Should be merged with `/search`, cf. ticket #20.

Old `search_users_and_orgs` view.
"""

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpRequest, JsonResponse

from apps.accounts.models import PytitionUser
from apps.organizations.models import Organization


@login_required
def search_profiles(request: HttpRequest) -> JsonResponse:
    query: str = request.GET.get("q", "")
    users: list[PytitionUser]
    orgs: list[Organization]

    if query != "":
        users = list(
            PytitionUser.objects.filter(
                Q(user__username__contains=query)
                | Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
            ).all()
        )
        orgs = list(Organization.objects.filter(name__icontains=query).all())
    else:
        users = []
        orgs = []

    result = {
        "orgs": [{"slugname": org.slugname, "name": org.name} for org in orgs],
        "users": [
            {
                "username": user.user.username,
                "firstname": user.user.first_name,
                "lastname": user.user.last_name,
            }
            for user in users
        ],
    }
    return JsonResponse(result)
