"""Helper functions for the core application."""

from __future__ import annotations

from typing import Any

import lxml
import lxml.html
from django.conf import settings
from django.http import HttpRequest
from lxml.html.clean import Cleaner


def sanitize_html(unsecure_html_content: str) -> str:
    """
    Sanitize HTML content by removing JavaScript and unsafe elements.

    Parameters
    ----------
    unsecure_html_content : str
        The HTML content to be sanitized.
    Returns
    -------
    str
        The sanitized HTML content.
    """

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


def get_client_ip(request: HttpRequest) -> str:
    """
    Get the client IP address from the request, considering proxies.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    Returns
    -------
    str
        The client IP address as a string.
    """

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return str(ip)


def settings_context_processor(request: HttpRequest) -> dict[str, Any]:
    """
    Context processor function to provide settings to templates via context processor.

    This context processor returns Django project settings into the template context
    (eg. Site name, etc).

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object, not used here but required by
        context processor signature.
    Returns
    -------
    dict[str, Any]
        A dictionary containing the settings.
    """

    return {"settings": settings}
