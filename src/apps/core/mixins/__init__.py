"""Core mixins package."""

from .has_config import HasConfig
from .has_owner import HasOwner as HasOwner

__all__ = [
    "HasConfig",
    "HasOwner",
]
