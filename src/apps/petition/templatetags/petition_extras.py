from django import template
from widget_tweaks.templatetags.widget_tweaks import add_class  # type: ignore

from apps.core.helpers import sanitize_html

register = template.Library()


@register.filter
def addstr(arg1: object, arg2: object) -> str:
    """Concatenate arg1 & arg2."""
    return str(arg1) + str(arg2)


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
def bootstrap(field: object) -> object:
    """Add bootstrap classes to form fields based on their widget type."""
    if (
        hasattr(field, "field")
        and hasattr(field.field, "widget")
        and field.field.widget
    ):
        widget = field.field.widget.__class__.__name__.lower()
        if widget in [
            "passwordinput",
            "textinput",
            "textarea",
            "select",
            "numberinput",
            "emailinput",
        ]:
            return add_class(field, "form-control")
        if widget in ["checkboxinput", "radioselect"]:
            return add_class(field, "form-check-input")
        if widget == "fileinput":
            return add_class(field, "form-control-file")
    return field


@register.filter
def html_sanitize(html: str) -> str:
    return sanitize_html(html)
