# DeleteAccountForm
from typing import Any

from django import forms
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _


class DeleteAccountForm(forms.Form):
    validation = forms.CharField()

    def clean(self) -> dict[str, Any]:
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
