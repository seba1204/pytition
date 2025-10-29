from __future__ import annotations

from typing import Any

from django import forms
from django.utils.safestring import SafeString


class SwitchWidget(forms.CheckboxInput):
    """A custom widget to render a boolean field as a switch."""

    template_name = "ui/components/switch_input.html"

    def get_context(
        self, name: str, value: Any, attrs: dict[str, Any] | None
    ) -> dict[str, Any]:
        if attrs is None:
            attrs = {}
        if "class" in attrs:
            attrs["class"] = attrs["class"] + " custom-control-input"
        else:
            attrs.update({"class": "custom-control-input"})

        ctx = super().get_context(name, value, attrs)
        # Attach label so the template can render a custom label element
        if hasattr(self, "label"):
            ctx["widget"].update({"label": self.label})
        return ctx

    def __init__(
        self,
        attrs: dict[str, Any] | None = None,
        check_test: Any | None = None,
        *,
        label: str | None = None,
    ) -> None:
        super().__init__(attrs=attrs, check_test=check_test)
        # keep a label reference for template consumption
        self.label = label


class SwitchField(forms.BooleanField):
    """A custom form field to render a boolean as a switch widget."""

    widget = SwitchWidget

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        label = kwargs.pop("label", None)
        super().__init__(*args, **kwargs)
        # Propagate label into widget instance
        self.widget.label = label

    def get_bound_field(
        self, form: forms.BaseForm, field_name: str
    ) -> forms.BoundField:
        bf = super().get_bound_field(form, field_name)
        # mypy doesn't like rebinding a method; it's intentional to hide the label
        bf.label_tag = self.label_tag  # type: ignore[method-assign]
        return bf

    def label_tag(
        self,
        contents: str | None = None,
        attrs: dict[str, str | bool] | None = None,
        label_suffix: str | None = None,
        tag: str | None = None,
    ) -> SafeString:
        # We render the label manually in the widget template, so suppress here.
        return SafeString("")
