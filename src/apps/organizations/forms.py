"""Forms for the Organization model."""

from typing import Any

from django import forms
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.organizations.models import Organization


class OrgCreationForm(forms.ModelForm):
    """Form for creating a new Organization."""

    class Meta:
        """Meta information for the OrgCreationForm."""

        model = Organization
        fields = ("name",)

    def clean(self) -> dict[str, Any]:
        """Custom validation for the Organization name."""
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
