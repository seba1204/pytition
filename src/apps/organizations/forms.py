from typing import Any

from django import forms
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.petition.models import Organization


class OrgCreationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ("name",)

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        name = cleaned_data.get("name") if cleaned_data is not None else None
        if name in ["..", "."]:
            self.add_error(
                "name",
                ValidationError(
                    _(
                        "This is an invalid Organization name. "
                        "Please try something else."
                    ),
                    code="invalid",
                ),
            )
        return self.cleaned_data
