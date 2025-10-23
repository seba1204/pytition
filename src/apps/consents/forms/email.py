from django import forms
from django.utils.translation import gettext_lazy as _


class EmailForm(forms.Form):
    """E-mail settings of Petition."""

    confirmation_email_reply = forms.EmailField(
        max_length=100,
        required=False,
        label=_(
            'Your contact email. It will be used as "Reply-To" field of'
            " the confirmation email sent to signatories. People responding"
            " to confirmation email will in fact respond to this address."
        ),
    )
