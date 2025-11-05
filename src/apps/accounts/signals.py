"""Signal handlers for account-related events."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.core.model_refs import PYTITION_USER

if TYPE_CHECKING:
    from apps.accounts.models import PytitionUser


# ------------------------------ Post save actions -----------------------------


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(
    sender: Any, instance: Any, created: bool, **kwargs: Any
) -> None:
    """Signal to create a PytitionUser profile when a new Django User is created."""
    # lazy import to avoid circular imports
    from apps.accounts.models import PytitionUser  # noqa

    if created:
        PytitionUser.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender: Any, instance: Any, **kwargs: Any) -> None:
    """Signal to save the PytitionUser profile when the Django User is saved."""
    instance.pytitionuser.save()


@receiver(post_delete, sender=PYTITION_USER)
def post_delete_user(
    sender: Any, instance: PytitionUser, *args: Any, **kwargs: Any
) -> None:
    """Signal to delete the associated Django User when a PytitionUser is deleted."""
    if instance.user:  # just in case user is not specified
        instance.user.delete()
