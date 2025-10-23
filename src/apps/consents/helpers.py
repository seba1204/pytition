from __future__ import annotations

import json
from typing import Any

import requests
from django.core.mail import EmailMessage, EmailMultiAlternatives, get_connection
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.translation import gettext as _

from apps.consents.routes import ConsentRoute


# Send Confirmation email
def send_confirmation_email(request: HttpRequest, signature: Any) -> None:
    """
    Send a confirmation email to a signature's email address.

    Parameters:
    -----------
    request : HttpRequest
        The HTTP request object.
    signature : Any
        The signature object containing petition and signatory details.
    """

    petition = signature.petition
    url = request.build_absolute_uri(
        reverse(ConsentRoute.CONFIRM, args=[petition.id, signature.confirmation_hash])
    )
    html_message = render_to_string(
        "consents/confirmation_email.html",
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


# TODO: type hint petition as Petition
def subscribe_to_newsletter(petition: Any, email: str) -> None:
    """
    Subscribe an email to a petition's newsletter.

    Parameters:
    -----------
    petition : Petition
        The petition object containing newsletter subscription details.
    email : str
        The email address to subscribe.
    """
    if petition.newsletter_subscribe_method in ["POST", "GET"]:
        if petition.newsletter_subscribe_http_url == "":
            return
        data = petition.newsletter_subscribe_http_data
        if data == "" or data is None:
            data = {}
        else:
            data = data.replace("'", '"')
            data = json.loads(data)
        if petition.newsletter_subscribe_http_mailfield != "":
            data[petition.newsletter_subscribe_http_mailfield] = email
    if petition.newsletter_subscribe_method == "POST":
        requests.post(petition.newsletter_subscribe_http_url, data)
    elif petition.newsletter_subscribe_method == "GET":
        requests.get(petition.newsletter_subscribe_http_url, data)
    elif petition.newsletter_subscribe_method == "MAIL":
        with get_connection(
            host=petition.newsletter_subscribe_mail_smtp_host,
            port=petition.newsletter_subscribe_mail_smtp_port,
            username=petition.newsletter_subscribe_mail_smtp_user,
            password=petition.newsletter_subscribe_mail_smtp_password,
            use_ssl=petition.newsletter_subscribe_mail_smtp_tls,
            use_tls=petition.newsletter_subscribe_mail_smtp_starttls,
        ) as connection:
            EmailMessage(
                petition.newsletter_subscribe_mail_subject.format(email),
                "",
                petition.newsletter_subscribe_mail_from,
                [petition.newsletter_subscribe_mail_to],
                connection=connection,
            ).send(fail_silently=True)
