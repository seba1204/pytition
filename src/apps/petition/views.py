import random
from pathlib import Path
from time import time
from typing import Any

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    JsonResponse,
)
from django.http import HttpResponse as DjangoHttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views.generic.edit import CreateView

from apps.accounts.forms import PytitionUserCreationForm
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
            "petition/index.html",
            {"user": user, "petitions": petitions, "sort": sort},
        )


@login_required
def image_upload(request: HttpRequest) -> HttpResponse:
    pytitionuser = get_session_user(request)

    if request.method != "POST":
        return HttpResponseForbidden()

    file = request.FILES.get("file", "")
    if file == "":
        return HttpResponseForbidden()

    storage = FileSystemStorage()
    path = Path(pytitionuser.username) / file.name
    name = storage.save(str(path), file)
    return JsonResponse({"location": storage.url(name)})


class PytitionUserCreateView(CreateView):
    def save_numbers(self, request: HttpRequest) -> None:
        request.session["random_a"] = self.a
        request.session["random_b"] = self.b
        request.session["answer"] = self.answer

    def get_new_numbers(self) -> None:
        r = random.Random(time())
        self.a = r.choice(range(0, 100))
        self.b = r.choice(range(0, 100))
        self.answer = self.a + self.b
        self.form_class.base_fields["answer"].label = _(
            "How much is {a} + {b}?"
        ).format(a=self.a, b=self.b)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.get_new_numbers()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        self.save_numbers(self.request)
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs

    def form_valid(self, form: PytitionUserCreationForm) -> HttpResponse:
        form.send_success_email()
        return super().form_valid(form)
