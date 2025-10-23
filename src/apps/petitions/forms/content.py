from django import forms
from django.utils.translation import gettext_lazy as _
from tinymce.widgets import TinyMCE  # type: ignore

from apps.petition.widgets import SwitchField


class ContentFormGeneric(forms.Form):
    """Class generically specifying the content for a petition editing form."""

    text = forms.CharField(widget=TinyMCE, required=False)
    target = forms.IntegerField(required=False)
    side_text = forms.CharField(widget=TinyMCE, required=False)
    footer_text = forms.CharField(widget=TinyMCE, required=False)
    footer_links = forms.CharField(widget=TinyMCE, required=False)
    sign_form_footer = forms.CharField(required=False)


class ContentFormPetition(ContentFormGeneric):
    """Class specifying the content for a petition editing form."""

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
    """Class specifying the content for a petition template editing form."""
    name = forms.CharField(max_length=50)
    field_order = ("name",)
