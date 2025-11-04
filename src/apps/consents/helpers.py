"""Helper functions for the consents app."""

from __future__ import annotations

import contextlib
import json
from typing import Any

import requests
from django.core.mail import EmailMessage, get_connection


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
        # FIXME: there is no error handling here
    elif petition.newsletter_subscribe_method == "GET":
        with contextlib.suppress(requests.exceptions.RequestException):
            requests.get(petition.newsletter_subscribe_http_url, params=data)
        # if server is currently not accessible, we just skip subscription
        # FIXME: log error on admin panel, so the admin can check failed subscriptions
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
