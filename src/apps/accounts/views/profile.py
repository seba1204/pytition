from django.conf import settings
from django.core.paginator import Paginator
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import render
from django.utils.translation import gettext as _

from apps.petition.helpers import (
    remove_user_moderated,
)
from apps.petition.models import (
    PytitionUser,
)


# /user/<user_name>
# Show the user profile
def profile(request: HttpRequest, user_name: str) -> HttpResponse:
    try:
        user = PytitionUser.objects.get(user__username=user_name)
    except PytitionUser.DoesNotExist as err:
        raise Http404(_("not found")) from err
    sort = request.GET.get("sort", "desc")
    creation_date = "-creation_date" if sort == "desc" else "creation_date"
    petitions_qs = user.petition_set.filter(published=True, moderated=False).order_by(
        creation_date
    )
    petitions_list = remove_user_moderated(list(petitions_qs))
    paginator = Paginator(petitions_list, settings.PAGINATOR_COUNT)
    page = request.GET.get("page")
    petitions = paginator.get_page(page)

    return render(
        request,
        "petition/user_profile.html",
        {"user": user, "petitions": petitions, "sort": sort},
    )
