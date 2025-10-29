from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext as _


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
