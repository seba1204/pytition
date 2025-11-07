"""Single-step petition creation form."""

from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _
from tinymce.widgets import TinyMCE  # type: ignore


class PetitionCreateForm(forms.Form):
    """
    Form used to create a petition in a single step.

    Notes
    -----
    This consolidates the previous 3-step wizard into one form
    with title, illustration image, and main content.
    """

    title = forms.CharField(
        label=_("Title"),
        max_length=300,
        widget=forms.TextInput(attrs={"class": "form-control", "data-field": "title"}),
    )
    illustration = forms.ImageField(
        label=_("Illustration image"),
        required=False,
        widget=forms.FileInput(
            attrs={"class": "form-control", "data-field": "illustration"}
        ),
    )
    text = forms.CharField(label=_("Content"), required=False, widget=TinyMCE)

    def clean_title(self) -> str:
        """
        Ensure title is not empty and trimmed.

        Returns
        -------
        str
            Cleaned title.
        """
        title = self.cleaned_data.get("title", "")
        title = title.strip()
        if not title:
            raise forms.ValidationError(_("Title is required."))
        return str(title)
