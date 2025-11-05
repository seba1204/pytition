"""Module for organization views."""

from . import invitations as invitations_views
from . import members as members_views
from .dashboard import dashboard
from .leave import leave
from .new import create
from .profile import profile

# FIXME: [#79] there is a lot of duplicated code between all those views.
# It should be refactored to use validator.py and services.py files.

__all__ = [
    "create",
    "dashboard",
    "leave",
    "profile",
    "members_views",
    "invitations_views",
]
