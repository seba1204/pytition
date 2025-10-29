from django.conf import settings
from django.core.paginator import Paginator
from django.http import Http404, HttpRequest
from django.http import HttpResponse as DjangoHttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from apps.accounts.routes import AccountsRoute
from apps.accounts.services import get_session_user
from apps.moderation.services import filter_moderated_petitions
from apps.organizations.routes import OrgRoute
from apps.petition.models import Organization, Petition


def index(request: HttpRequest) -> DjangoHttpResponse:
    if not hasattr(settings, "INDEX_PAGE"):
        raise Http404(_("You must set an INDEX_PAGE config in your settings"))
    index_page = getattr(settings, "INDEX_PAGE", None)
    if index_page == "USER_PROFILE":
        user_name = getattr(settings, "INDEX_PAGE_USER", None)
        if not isinstance(user_name, str) or not user_name:
            raise Http404(_("You must set an INDEX_PAGE_USER config in your settings"))
    elif index_page == "ORGA_PROFILE":
        org_name = getattr(settings, "INDEX_PAGE_ORGA", None)
        if not isinstance(org_name, str) or not org_name:
            raise Http404(_("You must set an INDEX_PAGE_ORGA config in your settings"))

    if index_page == "ORGA_PROFILE":
        org = Organization.objects.get(name=org_name)
        return redirect(OrgRoute.PROFILE, org.slugname)
    elif index_page == "USER_PROFILE":
        return redirect(AccountsRoute.PUBLIC_PROFILE, user_name)
    elif settings.INDEX_PAGE == "LOGIN_REGISTER":
        if request.user.is_authenticated:
            return redirect(AccountsRoute.DASHBOARD)
        else:
            return redirect("login")
    else:
        authenticated = request.user.is_authenticated
        user = get_session_user(request) if authenticated else request.user
        sort = request.GET.get("sort", "desc")
        creation_date = "-creation_date" if sort == "desc" else "creation_date"
        all_petitions_qs = Petition.objects.filter(
            published=True, moderated=False
        ).order_by(creation_date)
        all_petitions = filter_moderated_petitions(list(all_petitions_qs))
        paginator = Paginator(all_petitions, settings.PAGINATOR_COUNT)
        page = request.GET.get("page")
        petitions = paginator.get_page(page)

        return render(
            request,
            "core/index.html",
            {"user": user, "petitions": petitions, "sort": sort},
        )
