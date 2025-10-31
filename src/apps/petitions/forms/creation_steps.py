from typing import Any

from django import forms
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from tinymce.widgets import TinyMCE  # type: ignore

from apps.accounts.models import PytitionUser
from apps.organizations.models import Organization
from apps.petitions.models import Petition


class PetitionCreationStep1(forms.Form):
    """Fom that asks for the title of the petition."""

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
    """Form that asks for the content of the petition."""

    message = forms.CharField(widget=TinyMCE)


class PetitionCreationStep3(forms.Form):
    """Form that asks for publishing options."""

    publish = forms.BooleanField(required=False, label=_("Publish the petition now?"))
    configure = forms.BooleanField(required=False, label=_("Save & Configure"))
    ### Hidden fields ###
    use_template = forms.BooleanField(
        widget=forms.HiddenInput, required=False, label=_("Use template")
    )
    template_id = forms.IntegerField(
        widget=forms.HiddenInput, required=False, label=_("Template id")
    )
