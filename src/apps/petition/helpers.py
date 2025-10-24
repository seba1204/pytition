from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

import lxml
import lxml.html
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives, get_connection
from django.http import Http404, HttpRequest
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext as _
from lxml.html.clean import Cleaner

if TYPE_CHECKING:
    from apps.petition.models import PytitionUser


# Remove all moderated instances of Petition
def remove_user_moderated(petitions: list[Any]) -> list[Any]:
    """
    Filter-out moderated petitions when we already have a list.

    (Used where we cannot easily express the check in a queryset.)
    """
    return [p for p in petitions if not getattr(p, "is_moderated", False)]


# Remove all javascript from HTML code
def sanitize_html(unsecure_html_content: str) -> str:
    cleaner = Cleaner(
        inline_style=False,
        scripts=True,
        javascript=True,
        safe_attrs=lxml.html.defs.safe_attrs | {"style"},
        frames=False,
        embedded=False,
        meta=True,
        links=True,
        page_structure=True,
        remove_tags=["body"],
    )
    try:
        secure_html_content = lxml.html.tostring(
            cleaner.clean_html(lxml.html.fromstring(unsecure_html_content)),
            method="html",
        )
        return str(secure_html_content.decode())
    except Exception:
        secure_html_content = b""
    return ""


# Get the client IP address, considering proxies and RP


def get_client_ip(request: HttpRequest) -> str:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return str(ip)


# Get the user of the current session
def get_session_user(request: HttpRequest) -> PytitionUser:
    from .models import PytitionUser  # noqa # to avoid circular import

    try:
        pytitionuser = PytitionUser.objects.get(user__username=request.user.username)
    except User.DoesNotExist as err:
        raise Http404(_("not found")) from err
    return pytitionuser


# Get settings
def settings_context_processor(request: HttpRequest) -> dict[str, Any]:
    return {"settings": settings}


# Get footer content
def footer_content_processor(request: HttpRequest) -> dict[str, Any]:
    footer_content = None
    if settings.FOOTER_TEMPLATE:
        footer_content = render_to_string(settings.FOOTER_TEMPLATE)
    return {"footer_content": footer_content}


# Send welcome mail on account creation
def send_welcome_mail(user_infos: Mapping[str, Any]) -> None:
    html_message = render_to_string("registration/confirmation_email.html", user_infos)
    message = strip_tags(html_message)
    with get_connection() as connection:
        msg = EmailMultiAlternatives(
            _("Account created !"),
            message,
            to=[user_infos["email"]],
            connection=connection,
            reply_to=[settings.DEFAULT_NOREPLY_MAIL],
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)


def get_update_form(user: Any, data: Mapping[str, Any] | None = None) -> Any:
    """Get the update info form for the given user."""
    from apps.accounts.forms import UpdateInfoForm  # noqa # to avoid circular import

    if not data:
        _data: dict[str, Any] = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        }
    else:
        _data = dict(data)
    return UpdateInfoForm(user, _data)
