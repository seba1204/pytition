"""Module for organization views."""

from .accept_invitation import invite_accept
from .add_user import add_user
from .dashboard import dashboard
from .delete_member import delete_member
from .dismiss_invitation import invite_dismiss
from .edit_user_permissions import edit_user_perms
from .leave import leave
from .new import create
from .profile import profile
from .set_user_perms import set_user_perms

# FIXME: there is a lot of duplicated code between all those views.
# It should be refactored to use validator.py and services.py files.

__all__ = [
    "add_user",
    "create",
    "dashboard",
    "delete_member",
    "edit_user_perms",
    "invite_accept",
    "invite_dismiss",
    "leave",
    "profile",
    "set_user_perms",
]
