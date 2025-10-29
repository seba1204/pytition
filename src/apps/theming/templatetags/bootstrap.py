from django import template
from widget_tweaks.templatetags.widget_tweaks import add_class  # type: ignore

register = template.Library()


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
