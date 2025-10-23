from colorfield.fields import ColorWidget  # type: ignore
from django import forms

from apps.petition.models import (
    Petition,
)


class StyleForm(forms.Form):
    ### Graphical UI style info of Petition ###
    bgcolor = forms.CharField(widget=ColorWidget, required=False)
    linear_gradient_direction = forms.ChoiceField(
        choices=Petition.LINEAR_GRADIENT_CHOICES, required=False
    )
    gradient_from = forms.CharField(widget=ColorWidget, required=False)
    gradient_to = forms.CharField(widget=ColorWidget, required=False)
