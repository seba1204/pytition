"""Theming app permissions."""

from django.contrib.auth.models import AbstractBaseUser

from apps.theming.models import Theme


def theme_can_view(user: AbstractBaseUser | None, theme: Theme) -> bool:
    """
    Return whether a user can view the given theme.

    Parameters
    ----------
    user : AbstractBaseUser or None
        Request user (anonymous possible).
    theme : Theme
        Theme instance.

    Returns
    -------
    bool
        True if theme is public or user is the owner, else False.

    Notes
    -----
    - For now, if the theme is private, only the owner can view it.
    - This function can be extended later for more complex ACLs.
    """
    # Simple rule for now; evolve later (orgs, roles, ACLs...)
    if theme.is_public:
        return True
    # GenericForeignKey: compare to actual instance only if user is authenticated
    return bool(user and getattr(theme, "owner", None) == user)
