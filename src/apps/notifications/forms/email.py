"""Email forms for a petition."""

from django import forms
from django.utils.translation import gettext_lazy as _


# TODO: [#76] move it
# Has no place here. This form is used in the “Email setup” tab of the petition.
# It should go in the petitions app or, better yet, in the settings of a petition.
class EmailForm(forms.Form):
    """E-mail settings of Petition."""

    confirmation_email_reply = forms.EmailField(
        max_length=100,
        required=False,
        # Translators: Label for the contact email field in the email settings form
        label=_(
            "Your contact email. It will be used as 'Reply-To' field of"
            " the confirmation email sent to signatories. People responding"
            " to confirmation email will in fact respond to this address."
        ),
    )
