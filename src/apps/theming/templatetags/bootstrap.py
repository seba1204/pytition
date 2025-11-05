"""Template tags for Bootstrap theming."""

from django import template
from widget_tweaks.templatetags.widget_tweaks import add_class  # type: ignore

register = template.Library()


@register.filter
def bootstrap(field: object) -> object:
    """Add Bootstrap 5 classes to form fields based on their widget type."""
    if (
        hasattr(field, "field")
        and hasattr(field.field, "widget")
        and field.field.widget
    ):
        widget = field.field.widget.__class__.__name__.lower()
        # Text-like inputs
        if widget in [
            "passwordinput",
            "textinput",
            "textarea",
            "numberinput",
            "emailinput",
            "urlinput",
            "dateinput",
            "datetimeinput",
            "timeinput",
        ]:
            return add_class(field, "form-control")
        # Selects
        if widget in ["select", "selectmultiple"]:
            return add_class(field, "form-select")
        # Check/radio
        if widget in ["checkboxinput", "radioselect"]:
            return add_class(field, "form-check-input")
        # File inputs (BS5: form-control)
        if widget in ["fileinput", "clearablefileinput"]:
            return add_class(field, "form-control")
    return field
