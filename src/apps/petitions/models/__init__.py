"""Initialization of petitions models package."""

from . import config
from .authorship import PetitionAuthor as PetitionAuthor
from .new import PetitionNews as PetitionNews
from .petition import Petition as Petition
from .resource import PetitionResource as PetitionResource
from .slug import SlugModel as SlugModel

__all__ = [
    "Petition",
    "PetitionAuthor",
    "PetitionNews",
    "PetitionResource",
    "SlugModel",
    "config",
]
