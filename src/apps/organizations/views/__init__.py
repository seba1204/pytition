"""Module for organization views."""

from .accept_invitation import invite_accept
from .add_user import org_add_user
from .dashboard import org_dashboard
from .delete_member import org_delete_member
from .dismiss_invitation import invite_dismiss
from .edit_user_permissions import org_edit_user_perms
from .leave import leave_org
from .new import org_create
from .profile import org_profile
from .set_user_perms import org_set_user_perms

# FIXME: there is a lot of duplicated code between all those views.
# It should be refactored to use validator.py and services.py files.

__all__ = [
    "invite_accept",
    "leave_org",
    "org_add_user",
    "org_create",
    "org_dashboard",
    "org_delete_member",
    "org_profile",
    "invite_dismiss",
    "org_edit_user_perms",
    "org_set_user_perms",
]
