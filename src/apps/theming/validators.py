"""
QuerySet validators for theming owners.

Usage
-----

```python
# Query by owner instance
Theme.objects.for_owner(alice)  # all user-owned themes
Theme.objects.for_owner(org)  # all org-owned themes

# Query by owner model (all themes owned by any Organization)
Theme.objects.for_owner_model(Organization)
```
"""

from __future__ import annotations

from typing import TypeVar

from django.contrib.contenttypes.models import ContentType
from django.db import models

OwnerModelT = TypeVar("OwnerModelT", bound=models.Model)


class ThemeQuerySet(models.QuerySet):
    """QuerySet helpers for Theme."""

    def for_owner(self, owner: models.Model) -> ThemeQuerySet:
        """
        Filter themes owned by a given model instance.

        Parameters
        ----------
        owner : models.Model
            Concrete owner instance (user, organization, etc.).

        Returns
        -------
        ThemeQuerySet
            Filtered queryset for the given owner.
        """
        owner_ct = ContentType.objects.get_for_model(owner, for_concrete_model=False)
        return self.filter(owner_content_type=owner_ct, owner_object_id=owner.pk)

    def for_owner_model(self, model: type[OwnerModelT]) -> ThemeQuerySet:
        """
        Filter themes by a given owner model (any instance of this model).

        Parameters
        ----------
        model : type[OwnerModelT]
            Django model class representing potential owners.

        Returns
        -------
        ThemeQuerySet
            Filtered queryset containing rows whose owner is of the given model type.
        """
        owner_ct = ContentType.objects.get_for_model(model, for_concrete_model=False)
        return self.filter(owner_content_type=owner_ct)
