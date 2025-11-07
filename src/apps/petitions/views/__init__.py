"""Petitions app views package."""

from .delete import delete
from .detail import detail
from .edit import edit
from .new import new
from .publish import publish
from .show_petition import slug_show_petition
from .transfer import transfer
from .unpublish import unpublish

__all__ = [
    "delete",
    "detail",
    "edit",
    "publish",
    "slug_show_petition",
    "transfer",
    "unpublish",
    "new",
]
