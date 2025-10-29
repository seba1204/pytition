from django.conf import settings
from django.core.paginator import Paginator
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _

from apps.accounts.services import get_session_user
from apps.petition.helpers import remove_user_moderated

# TODO: move model to apps/organizations/models.py
from apps.petition.models import Organization


# /org/<slug:orgslugname>
# Show the profile of an organization
def profile(request: HttpRequest, orgslugname: str) -> HttpResponse:
    """
    View function to show the profile of an organization.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    orgslugname : str
        The slugname of the organization.

    Returns
    -------
    HttpResponse
        The HTTP response object with the rendered organization profile.
    """

    # Try to get the logged-in user, if any
    try:
        user = get_session_user(request)
    except Exception:
        user = None

    # Check that the organization exists
    try:
        org = Organization.objects.get(slugname=orgslugname)
    except Organization.DoesNotExist:
        raise Http404(_("not found")) from None

    sort = request.GET.get("sort", "desc")
    creation_date = "-creation_date" if sort == "desc" else "creation_date"
    petitions_qs = org.petition_set.filter(published=True, moderated=False).order_by(
        creation_date
    )
    petitions_list = remove_user_moderated(list(petitions_qs))
    paginator = Paginator(petitions_list, settings.PAGINATOR_COUNT)
    page = request.GET.get("page")
    petitions = paginator.get_page(page)

    ctx = {"org": org, "petitions": petitions, "sort": sort}

    # if a user is logged-in, put it in the context, it will feed the navbar dropdown
    if user is not None:
        ctx["user"] = user

    return render(request, "org/profile.html", ctx)
