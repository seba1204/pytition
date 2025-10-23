from typing import Any

from colorfield.fields import ColorWidget  # type: ignore
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from tinymce.widgets import TinyMCE  # type: ignore

from .helpers import send_welcome_mail
from .models import (
    Organization,
    Petition,
    PytitionUser,
)
from .widgets import SwitchField


class PetitionCreationStep1(forms.Form):
    ### Ask for title ###
    title = forms.CharField(max_length=200)

    def clean_title(self) -> str:
        title = self.cleaned_data.get("title")
        if not isinstance(title, str) or title is None:
            raise ValidationError(
                _("Title is required and must be a string."), code="invalid"
            )
        filters = {"title": title}
        if self.owned_by_org:
            org = Organization.objects.get(slugname=self.orgslugname)
            org_filter_dict: dict[str, Any] = {"org": org}
            filters.update(org_filter_dict)
        else:
            user = PytitionUser.objects.get(user__username=self.username)
            user_filter_dict: dict[str, Any] = {"user": user}
            filters.update(user_filter_dict)
        results = Petition.objects.filter(**filters)
        if results.count() > 0:
            self.add_error(
                "title",
                ValidationError(
                    _("There is already a petition with this title"), code="invalid"
                ),
            )

        return str(title)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if "orgslugname" in kwargs:
            self.orgslugname = kwargs.pop("orgslugname")
            self.owned_by_org = True
        elif "user_name" in kwargs:
            self.owned_by_org = False
            self.username = kwargs.pop("user_name")
        else:
            raise ValueError(_("You should either provide an org name or a user name"))
        super().__init__(*args, **kwargs)


class PetitionCreationStep2(forms.Form):
    ### Ask for content ###
    message = forms.CharField(widget=TinyMCE)


class PetitionCreationStep3(forms.Form):
    ### Ask for publication ###
    publish = forms.BooleanField(required=False, label=_("Publish the petition now?"))
    configure = forms.BooleanField(required=False, label=_("Save & Configure"))
    ### Hidden fields ###
    use_template = forms.BooleanField(
        widget=forms.HiddenInput, required=False, label=_("Use template")
    )
    template_id = forms.IntegerField(
        widget=forms.HiddenInput, required=False, label=_("Template id")
    )


class ContentFormGeneric(forms.Form):
    ### Content of a Petition ###
    text = forms.CharField(widget=TinyMCE, required=False)
    target = forms.IntegerField(required=False)
    side_text = forms.CharField(widget=TinyMCE, required=False)
    footer_text = forms.CharField(widget=TinyMCE, required=False)
    footer_links = forms.CharField(widget=TinyMCE, required=False)
    sign_form_footer = forms.CharField(required=False)


class ContentFormPetition(ContentFormGeneric):
    title = forms.CharField(max_length=200)
    publication_date = forms.DateField(required=False)
    show_publication_date = SwitchField(
        required=False, label=_("Show publication date")
    )
    paper_signatures = forms.IntegerField()
    field_order = (
        "title",
        "publication_date",
        "show_publication_date",
        "paper_signatures",
    )


class ContentFormTemplate(ContentFormGeneric):
    name = forms.CharField(max_length=50)
    field_order = ("name",)


# This form is not rendered like the others, it is just used to "parse" POSTed data
class SocialNetworkForm(forms.Form):
    ### Social Network settings of Petition ###
    twitter_description = forms.CharField(max_length=200, required=False)
    twitter_image = forms.FileField(max_length=500, required=False)
    org_twitter_handle = forms.CharField(max_length=20, required=False)
    remove_twitter_image = forms.BooleanField(required=False, initial=False)
    has_email_share_button = forms.BooleanField(required=False)
    has_facebook_share_button = forms.BooleanField(required=False)
    has_tumblr_share_button = forms.BooleanField(required=False)
    has_linkedin_share_button = forms.BooleanField(required=False)
    has_twitter_share_button = forms.BooleanField(required=False)
    has_mastodon_share_button = forms.BooleanField(required=False)
    has_whatsapp_share_button = forms.BooleanField(required=False)


class StyleForm(forms.Form):
    ### Graphical UI style info of Petition ###
    bgcolor = forms.CharField(widget=ColorWidget, required=False)
    linear_gradient_direction = forms.ChoiceField(
        choices=Petition.LINEAR_GRADIENT_CHOICES, required=False
    )
    gradient_from = forms.CharField(widget=ColorWidget, required=False)
    gradient_to = forms.CharField(widget=ColorWidget, required=False)


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
