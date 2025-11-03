from django import template

from apps.core.helpers import sanitize_html

register = template.Library()


@register.filter
def addstr(arg1: object, arg2: object) -> str:
    """Concatenate arg1 & arg2."""
    return str(arg1) + str(arg2)


# FIXME: this seems to be never used.
@register.filter
def getitem(array: object, item: object) -> object:
    """Get an item from a list, tuple, dict, or object's attribute."""
    try:
        if isinstance(array, dict):
            return array[item]
        elif isinstance(array, (list, tuple)):
            if isinstance(item, int):
                return array[item]
            else:
                raise TypeError
        else:
            raise TypeError
    except (TypeError, KeyError, IndexError):
        try:
            return getattr(array, str(item))
        except AttributeError:
            return None


@register.filter
def html_sanitize(html: str) -> str:
    """Sanitize HTML content to prevent XSS attacks."""
    return sanitize_html(html)
