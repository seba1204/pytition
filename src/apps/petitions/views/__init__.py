"""Petitions app views package."""

from .delete import delete
from .detail import detail, legacy_detail
from .edit import edit
from .new import new
from .publish import publish
from .transfer import transfer
from .unpublish import unpublish

__all__ = [
    "delete",
    "detail",
    "edit",
    "publish",
    "legacy_detail",
    "transfer",
    "unpublish",
    "new",
]
