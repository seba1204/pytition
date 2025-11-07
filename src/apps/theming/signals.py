"""Theme signals module."""

from __future__ import annotations

from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Theme


@receiver(post_delete, dispatch_uid="themes_cleanup_orphans", weak=False)
def cleanup_orphan_themes(sender: type[Any], instance: Any, **kwargs: Any) -> None:
    """
    Delete Theme rows whose GFK owner was just deleted.

    Notes
    -----
    - We listen to *all* model deletions (no sender filter).
    - On each delete, we compute the instance ContentType and purge related themes.
    - This is simple and robust;
      - maybe we can restrict to specific senders later for performance.
    """
    # Compute the ContentType of the deleted instance
    ct = ContentType.objects.get_for_model(instance, for_concrete_model=False)
    # Delete all themes pointing to this (ct, pk)
    Theme.objects.filter(
        owner_content_type=ct,
        owner_object_id=getattr(instance, "pk", None),
    ).delete()
