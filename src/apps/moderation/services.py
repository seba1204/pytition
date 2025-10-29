from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.petition.models import Petition


# Remove all moderated instances of Petition
def filter_moderated_petitions(petitions: list[Petition]) -> list[Petition]:
    """
    Filter-out moderated petitions when we already have a list.

    (Used where we cannot easily express the check in a queryset.)
    """
    return [p for p in petitions if not getattr(p, "is_moderated", False)]
