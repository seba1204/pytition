"""Django template filters for various utilities."""

from django import template

from apps.core.helpers import sanitize_html

register = template.Library()


@register.filter
def addstr(arg1: object, arg2: object) -> str:
    """Concatenate arg1 & arg2."""
    return str(arg1) + str(arg2)


@register.filter
def html_sanitize(html: str) -> str:
    """Sanitize HTML content to prevent XSS attacks."""
    return sanitize_html(html)
