"""Forms package for petitions app."""

from .content import ContentFormPetition, ContentFormTemplate
from .social_networks import SocialNetworkForm
from .style import StyleForm

__all__ = [
    "ContentFormPetition",
    "ContentFormTemplate",
    "SocialNetworkForm",
    "StyleForm",
]
