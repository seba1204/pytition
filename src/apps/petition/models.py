from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from apps.core.model_refs import PETITION, PYTITION_USER, SLUG_MODEL

if TYPE_CHECKING:
    from apps.accounts.models import PytitionUser
    from apps.petitions.models import Petition, SlugModel


# ------------------------------ Pre save actions -----------------------------
@receiver(pre_save, sender=SLUG_MODEL)
def check_slug_is_not_empty(sender: Any, instance: SlugModel, **kwargs: Any) -> None:
    instance.clean()
    instance.validate_unique()


# ------------------------------ Post save actions -----------------------------
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(
    sender: Any, instance: Any, created: bool, **kwargs: Any
) -> None:
    # lazy import to avoid circular imports
    from apps.accounts.models import PytitionUser  # noqa

    if created:
        PytitionUser.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender: Any, instance: Any, **kwargs: Any) -> None:
    instance.pytitionuser.save()


@receiver(pre_save, sender=PETITION)
def pre_save_petition(sender: Any, instance: Petition, **kwargs: Any) -> None:
    if not instance.creation_date:
        instance.creation_date = timezone.now()


@receiver(post_save, sender=PETITION)
def save_petition(sender: Any, instance: Petition, **kwargs: Any) -> None:
    if instance.slugmodel_set.count() == 0:
        instance.slugify()
    if kwargs.get("created"):
        instance.creation_date = timezone.now()
        instance.save()


@receiver(post_delete, sender=PYTITION_USER)
def post_delete_user(
    sender: Any, instance: PytitionUser, *args: Any, **kwargs: Any
) -> None:
    if instance.user:  # just in case user is not specified
        instance.user.delete()
