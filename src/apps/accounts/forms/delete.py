"""Form to handle account deletion confirmation."""

from typing import Any

from django import forms
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _


class DeleteAccountForm(forms.Form):
    """Form to confirm account deletion."""

    validation = forms.CharField()

    def clean(self) -> dict[str, Any]:
        """Validate the confirmation input."""
        cleaned_data = super().clean()
        valid = cleaned_data.get("validation") if cleaned_data is not None else None
        if valid != _("DROP MY ACCOUNT"):
            self.add_error(
                "validation",
                ValidationError(
                    _("You miss-typed the validation code"), code="invalid"
                ),
            )
        return self.cleaned_data
