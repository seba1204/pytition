from typing import Any, cast

from django import forms
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.core.widgets import SwitchField
from apps.petitions.models import Petition


class NewsletterForm(forms.Form):
    """Newsletter settings of Petition."""

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

    def clean(self) -> dict[str, Any]:  # noqa
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
                            _("Port must be between 1 and %(max)d.")
                            % {"max": MAX_PORT_NUMBER},
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
        has_newsletter = bool(data.get("has_newsletter"))
        if method in {"GET", "POST"}:
            # Mailfield is always required for HTTP subscription
            if not data.get("newsletter_subscribe_http_mailfield"):
                self.add_error(
                    "newsletter_subscribe_http_mailfield",
                    ValidationError(
                        _("This field is required for HTTP subscription."),
                        code="invalid",
                    ),
                )

            # Accept either a URL or a raw body (tests only provide http_data)
            if not data.get("newsletter_subscribe_http_url") and not data.get(
                "newsletter_subscribe_http_data"
            ):
                self.add_error(
                    "newsletter_subscribe_http_url",
                    ValidationError(
                        _("Provide either a subscription URL or HTTP data."),
                        code="invalid",
                    ),
                )
        # When MAIL method is selected, require mail-to fields

        if method == "MAIL" and has_newsletter:
            if not data.get("newsletter_subscribe_mail_to"):
                self.add_error(
                    "newsletter_subscribe_mail_to",
                    ValidationError(
                        # Translators: Newsletter subscription - mail to address
                        _("Please provide the list admin address."),
                        code="invalid",
                    ),
                )
            if not data.get("newsletter_subscribe_mail_subject"):
                self.add_error(
                    "newsletter_subscribe_mail_subject",
                    ValidationError(
                        # Translators: Newsletter subscription - mail subject template
                        _("Please provide the subscription subject template."),
                        code="invalid",
                    ),
                )

        # Save back to cleaned_data with the right type
        self.cleaned_data = dict(data)

        # ensure booleans are strictly True/False
        for k in (
            "has_newsletter",
            "newsletter_subscribe_mail_smtp_tls",
            "newsletter_subscribe_mail_smtp_starttls",
        ):
            self.cleaned_data[k] = bool(self.cleaned_data.get(k))

        return self.cleaned_data
