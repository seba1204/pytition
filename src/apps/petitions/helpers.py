from __future__ import annotations

from typing import TYPE_CHECKING

from django.http import Http404
from django.utils.translation import gettext as _

# Avoid circular imports for type checking
if TYPE_CHECKING:
    from apps.petition.models import Petition


# Return a 404 if a petition does not exist
def petition_from_id(id: int) -> Petition:
    petition: Petition | None = Petition.by_id(id)
    if petition is None:
        raise Http404(_("Petition does not exist"))
    else:
        return petition
