"""View to search for petitions and organizations."""

from django.conf import settings
from django.core.paginator import Page, Paginator
from django.db.models import Q
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import render

from apps.moderation.services import filter_moderated_petitions
from apps.organizations.models import Organization
from apps.petitions.models import Petition


# /search?q=QUERY
# Show results of a search query
def search(request: HttpRequest) -> HttpResponse:
    """
    Function-based view to search for petitions and organizations.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object containing GET parameters.

    Returns
    -------
    HttpResponse
        The rendered search results page.
    """
    query = request.GET.get("q", "").strip()
    page = request.GET.get("page", "1")

    petitions: list[Petition] | Page[Petition]
    orgs: list[Organization]

    # if there's a query, filter petitions and orgs by it
    if query != "":
        # get first 15 matching petitions and orgs
        petitions_qs = Petition.objects.filter(
            Q(title__icontains=query) | Q(text__icontains=query)
        ).filter(published=True, moderated=False)[:15]
        petitions = filter_moderated_petitions(list(petitions_qs))
        orgs = list(Organization.objects.filter(name__icontains=query))

    # else, show latest petitions only (used in homepage, user page, etc.)
    else:
        petitions_qs = Petition.objects.filter(
            published=True, moderated=False
        ).order_by("-id")
        petitions = filter_moderated_petitions(list(petitions_qs))
        paginator = Paginator(petitions, settings.PAGINATOR_COUNT)
        petitions = paginator.get_page(page)
        orgs = []
    return render(
        request,
        "core/search_bs5.html",
        {"petitions": petitions, "orgs": orgs, "q": query},
    )
