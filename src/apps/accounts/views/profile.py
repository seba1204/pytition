"""Views for user profiles."""

from django.conf import settings
from django.core.paginator import Paginator
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _

from apps.accounts.models import PytitionUser
from apps.moderation.services import filter_moderated_petitions


# Show the user profile
def profile(request: HttpRequest, user_name: str) -> HttpResponse:
    """
    Show a list of all public petitions of the user.

    Parameters
    ----------
        request: HttpRequest
        user_name: str -- the username of the user
    GET parameters (in request.GET):
    ----------------------------
        sort: str -- 'asc' or 'desc' for creation date sorting (default 'desc')
        page: int -- the page number (default 1)

    Returns
    -------
        HttpResponse -- the rendered user profile page

    Notes
    -----
        Shows only published and non-moderated petitions
    """
    user: PytitionUser

    try:
        user = PytitionUser.objects.get(user__username=user_name)
    except PytitionUser.DoesNotExist as err:
        raise Http404(_("not found")) from err
    sort = request.GET.get("sort", "desc")
    creation_date = "-creation_date" if sort == "desc" else "creation_date"
    petitions_qs = user.petition_set.filter(published=True, moderated=False).order_by(
        creation_date
    )
    petitions_list = filter_moderated_petitions(list(petitions_qs))
    paginator = Paginator(petitions_list, settings.PAGINATOR_COUNT)
    page = request.GET.get("page")
    petitions = paginator.get_page(page)

    return render(
        request,
        template_name="accounts/profile_bs5.html",
        context={"user": user, "petitions": petitions, "sort": sort},
    )
