from typing import Any

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.petition.helpers import send_welcome_mail


class PytitionUserCreationForm(UserCreationForm):
    answer = forms.IntegerField(required=True)
    email_confirm = forms.EmailField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "answer",
            "email_confirm",
        )
        field_classes = {"username": UsernameField}

    def __init__(self, request: Any = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["email"].required = True
        self.request = request

    def clean(self) -> dict[str, Any]:
        session = self.request.session
        cleaned_data = super(UserCreationForm, self).clean()
        if cleaned_data is None:
            cleaned_data = {}
        if (
            "answer" in cleaned_data
            and int(cleaned_data["answer"]) != session["answer"]
        ):
            self.add_error(
                "answer",
                ValidationError(_("Wrong answer"), code="invalid"),
            )
        if "email_confirm" in cleaned_data and cleaned_data["email_confirm"] != "":
            # Normal users should end up with email_confirm == "" because the field is
            # hidden. Robots might fill up this field, thus we throw an error.
            self.add_error(
                "email_confirm",
                ValidationError(
                    "Incorrect email confirmation",
                    code="invalid",
                ),
            )
        if "answer" in cleaned_data:
            del cleaned_data["answer"]
        if "answer" in self.data:
            # QueryDict() objects are immutable!
            new_data = dict(self.data.items())
            del new_data["answer"]
            self.data = new_data
        self.cleaned_data = cleaned_data
        return cleaned_data

    def send_success_email(self) -> None:
        send_welcome_mail(self.cleaned_data)


class UpdateInfoForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name", "email")

    def __init__(self, user: Any, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.user = user
        del self.fields["password1"]
        del self.fields["password2"]

    def save(self, commit: bool = True) -> Any:
        self.user.email = self.cleaned_data["email"]
        self.user.first_name = self.cleaned_data["first_name"]
        self.user.last_name = self.cleaned_data["last_name"]
        if commit:
            self.user.save()
        return self.user


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
