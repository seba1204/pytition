from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from apps.core.model_refs import PETITION, SLUG_MODEL

if TYPE_CHECKING:
    from apps.petitions.models import Petition, SlugModel


# ------------------------------ Pre save actions -----------------------------
@receiver(pre_save, sender=SLUG_MODEL)
def check_slug_is_not_empty(sender: Any, instance: SlugModel, **kwargs: Any) -> None:
    instance.clean()
    instance.validate_unique()


# ------------------------------ Post save actions -----------------------------
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
