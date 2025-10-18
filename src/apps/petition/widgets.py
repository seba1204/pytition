from django import forms
from django.utils.safestring import SafeString


class SwitchWidget(forms.CheckboxInput):
    template_name = "petition/widgets/SwitchInput.html"

    def get_context(self, name: str, value: object, attrs: dict | None) -> dict:
        if attrs is None:
            attrs = {}
        if "class" in attrs:
            attrs["class"] = attrs["class"] + " custom-control-input"
        else:
            attrs.update({"class": "custom-control-input"})

        ctx = super().get_context(name, value, attrs)
        ctx["widget"].update({"label": self.label})
        return ctx

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        if "label" in kwargs:
            self.label = kwargs.pop("label")


class SwitchField(forms.BooleanField):
    widget = SwitchWidget

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        if "label" in kwargs:
            self.widget.label = kwargs["label"]

    def get_bound_field(
        self, form: forms.BaseForm, field_name: str
    ) -> forms.BoundField:
        bf = super().get_bound_field(form, field_name)
        bf.label_tag = self.label_tag
        return bf

    def label_tag(
        self,
        contents: str | None = None,
        attrs: dict[str, str | bool] | None = None,
        label_suffix: str | None = None,
        tag: str | None = None,
    ) -> SafeString:
        return SafeString("")
