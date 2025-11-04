"""Notification services module."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.translation import gettext as _

from apps.signatures.routes import SignatureRoute

# TODO: [#21] Implement a real notification app


def send_confirmation_email(request: HttpRequest, signature: Any) -> None:
    """
    Send a confirmation email to a signature's email address.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    signature : Any
        The signature object containing petition and signatory details.
    """
    petition = signature.petition
    url = request.build_absolute_uri(
        reverse(SignatureRoute.CONFIRM, args=[petition.id, signature.confirmation_hash])
    )
    html_message = render_to_string(
        "notifications/confirmation_email.html",
        {"firstname": signature.first_name, "url": url},
    )
    message = strip_tags(html_message)
    with get_connection() as connection:
        msg = EmailMultiAlternatives(
            _("Confirm your signature to our petition"),
            message,
            to=[signature.email],
            connection=connection,
            reply_to=[petition.confirmation_email_reply],
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)


def send_welcome_mail(user_infos: Mapping[str, Any]) -> None:
    """
    Send welcome mail on account creation.

    Parameters
    ----------
    user_infos : Mapping[str, Any]
        Information about the user to include in the email.
    """
    html_message = render_to_string("notifications/confirmation_email.html", user_infos)
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
