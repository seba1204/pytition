from __future__ import annotations

from typing import Any

from django.conf import settings
from django.http import HttpRequest
from django.template.loader import render_to_string


def footer_content(request: HttpRequest) -> dict[str, Any]:
    """
    Get footer content.

    This context processor loads the footer template specified in settings and makes it
    available in the template context.
    """
    footer_content = None
    if settings.FOOTER_TEMPLATE:
        footer_content = render_to_string(settings.FOOTER_TEMPLATE)
    return {"footer_content": footer_content}
