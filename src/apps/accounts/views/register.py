"""User registration view with anti-bot measures."""

import random
from time import time
from typing import Any

from django.conf import settings
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBase,
    HttpResponseForbidden,
)
from django.utils.translation import gettext as _
from django.views.generic.edit import CreateView

from apps.accounts.forms import PytitionUserCreationForm


class Register(CreateView):
    """User registration view with simple anti-bot math question."""

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        """Check if registration is allowed before processing the request."""
        if not getattr(settings, "ALLOW_REGISTER", False):
            return HttpResponseForbidden("Registration is not allowed.")
        return super().dispatch(request, *args, **kwargs)

    def save_numbers(self, request: HttpRequest) -> None:
        """Save the random numbers and their answer in the session."""
        request.session["random_a"] = self.a
        request.session["random_b"] = self.b
        request.session["answer"] = self.answer

    def get_new_numbers(self) -> None:
        """Generate new random numbers for the anti-bot question."""
        r = random.Random(time())
        self.a = r.choice(range(0, 100))
        self.b = r.choice(range(0, 100))
        self.answer = self.a + self.b
        if self.form_class is not None and hasattr(self.form_class, "base_fields"):
            self.form_class.base_fields["answer"].label = _(
                "How much is %(a)d + %(b)d?"
            ) % {"a": self.a, "b": self.b}

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.get_new_numbers()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add random numbers to the context data."""
        self.save_numbers(self.request)
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self) -> dict[str, Any]:
        """Pass the request to the form."""
        kwargs = super().get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs

    def form_valid(self, form: PytitionUserCreationForm) -> HttpResponse:
        """Send a welcome email upon successful registration."""
        form.send_success_email()
        return super().form_valid(form)
