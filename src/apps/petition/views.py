import random
from pathlib import Path
from time import time
from typing import Any

from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    JsonResponse,
)
from django.utils.translation import gettext as _
from django.views.generic.edit import CreateView

from apps.accounts.forms import PytitionUserCreationForm
from apps.accounts.services import get_session_user


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
