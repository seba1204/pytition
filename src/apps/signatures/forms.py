from typing import Any

from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from apps.petition.models import Petition, Signature


class SignatureForm(ModelForm):
    subscribed_to_mailinglist = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={"class": "form-check-input", "group_class": "form-check"}
        ),
        label_suffix="",
        required=False,
    )

    class Meta:
        model = Signature
        fields = [
            "first_name",
            "last_name",
            "phone",
            "email",
            "subscribed_to_mailinglist",
        ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "placeholder": _("First name *"),
                    "class": "form-control has-feedback eaFullWidthContent",
                    "group_class": "form-group has-feedback",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "placeholder": _("Last name *"),
                    "class": "form-control has-feedback eaFullWidthContent",
                    "group_class": "form-group has-feedback",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "placeholder": _("Phone number"),
                    "class": "form-control has-feedback eaFullWidthContent",
                    "group_class": "form-group has-feedback",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": _("Email address *"),
                    "class": "form-control has-feedback eaFullWidthContent",
                    "group_class": "form-group has-feedback",
                }
            ),
        }

        labels = dict.fromkeys(["first_name", "last_name", "phone", "email"], "")

    def __init__(
        self, petition: Petition | None = None, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.instance.petition = petition
        if not petition or not petition.has_newsletter:
            del self.fields["subscribed_to_mailinglist"]
        else:
            self.fields[
                "subscribed_to_mailinglist"
            ].label = self.instance.petition.newsletter_text
