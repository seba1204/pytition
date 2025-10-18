from typing import Any, cast

from colorfield.fields import ColorWidget  # type: ignore
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.forms import ModelForm, ValidationError
from django.utils.translation import gettext_lazy as _
from tinymce.widgets import TinyMCE  # type: ignore

from .helpers import send_welcome_mail
from .models import (
    Organization,
    Petition,
    PytitionUser,
    Signature,
)
from .widgets import SwitchField


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


class EmailForm(forms.Form):
    ### E-mail settings of Petition ###
    confirmation_email_reply = forms.EmailField(
        max_length=100,
        required=False,
        label=_(
            'Your contact email. It will be used as "Reply-To" field of'
            " the confirmation email sent to signatories. People responding"
            " to confirmation email will in fact respond to this address."
        ),
    )


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


class NewsletterForm(forms.Form):
    ### Newsletter settings of Petition ###
    has_newsletter = SwitchField(
        required=False, label=_("Does this petition have a newsletter?")
    )
    newsletter_text = forms.CharField(required=False)
    newsletter_subscribe_http_data = forms.CharField(max_length=1000, required=False)
    newsletter_subscribe_http_mailfield = forms.CharField(
        max_length=100, required=False
    )
    newsletter_subscribe_http_url = forms.CharField(max_length=1000, required=False)
    newsletter_subscribe_mail_subject = forms.CharField(max_length=1000, required=False)
    newsletter_subscribe_mail_from = forms.EmailField(required=False)
    newsletter_subscribe_mail_to = forms.EmailField(required=False)
    newsletter_subscribe_method = forms.ChoiceField(
        choices=Petition.NEWSLETTER_SUBSCRIBE_METHOD_CHOICES, required=False
    )
    newsletter_subscribe_mail_smtp_host = forms.CharField(
        max_length=100, required=False
    )
    newsletter_subscribe_mail_smtp_port = forms.IntegerField(required=False)
    newsletter_subscribe_mail_smtp_user = forms.CharField(
        max_length=200, required=False
    )
    newsletter_subscribe_mail_smtp_password = forms.CharField(
        max_length=200, required=False, widget=forms.PasswordInput()
    )
    newsletter_subscribe_mail_smtp_tls = SwitchField(
        required=False, label=_("Use TLS?")
    )
    newsletter_subscribe_mail_smtp_starttls = SwitchField(
        required=False, label=_("Use STARTTLS?")
    )

    newsletter_subscribe_mail_smtp_port.widget.attrs.update({"min": 1, "max": 65535})

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        data: dict[str, Any] = {}
        if cleaned_data is not None:
            for field in self.base_fields:
                data[field] = cleaned_data.get(field)

        # TLS vs STARTTLS are mutually exclusive
        tls = bool(data.get("newsletter_subscribe_mail_smtp_tls"))
        starttls = bool(data.get("newsletter_subscribe_mail_smtp_starttls"))
        if tls and starttls:
            self.add_error(
                "newsletter_subscribe_mail_smtp_tls",
                ValidationError(
                    _("You cannot select both TLS and STARTTLS."), code="invalid"
                ),
            )
            self.add_error(
                "newsletter_subscribe_mail_smtp_starttls",
                ValidationError(
                    _("You cannot select both TLS and STARTTLS."), code="invalid"
                ),
            )

        # Port bounds check when provided
        MAX_PORT_NUMBER = 65535
        port = data.get("newsletter_subscribe_mail_smtp_port")
        if port is not None:
            try:
                port_int = int(port)
                if port_int < 1 or port_int > MAX_PORT_NUMBER:
                    self.add_error(
                        "newsletter_subscribe_mail_smtp_port",
                        ValidationError(
                            _(f"Port must be between 1 and {MAX_PORT_NUMBER}."),
                            code="invalid",
                        ),
                    )
            except (TypeError, ValueError):
                self.add_error(
                    "newsletter_subscribe_mail_smtp_port",
                    ValidationError(_("Port must be an integer."), code="invalid"),
                )

        # When HTTP method is selected, required fields must be present
        method = cast(str | None, data.get("newsletter_subscribe_method"))
        if method in {"GET", "POST"}:
            if not data.get("newsletter_subscribe_http_url"):
                self.add_error(
                    "newsletter_subscribe_http_url",
                    ValidationError(
                        _("This field is required for HTTP subscription."),
                        code="invalid",
                    ),
                )
            if not data.get("newsletter_subscribe_http_mailfield"):
                self.add_error(
                    "newsletter_subscribe_http_mailfield",
                    ValidationError(
                        _("This field is required for HTTP subscription."),
                        code="invalid",
                    ),
                )

        # When MAIL method is selected, require mail-to fields
        if method == "MAIL":
            if not data.get("newsletter_subscribe_mail_to"):
                self.add_error(
                    "newsletter_subscribe_mail_to",
                    ValidationError(
                        _("Please provide the list admin address."), code="invalid"
                    ),
                )
            if not data.get("newsletter_subscribe_mail_subject"):
                self.add_error(
                    "newsletter_subscribe_mail_subject",
                    ValidationError(
                        _("Please provide the subscription subject template."),
                        code="invalid",
                    ),
                )

        # Save back to cleaned_data with the right type
        self.cleaned_data = dict(data)
        return self.cleaned_data


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
