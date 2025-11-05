"""Organization model definition."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _lazy

from apps.core.model_refs import PERMISSION, PETITION_TEMPLATE, PYTITION_USER

if TYPE_CHECKING:
    from apps.accounts.models import PytitionUser


class Organization(models.Model):
    """Model representing an organization."""

    name = models.CharField(
        max_length=200,
        verbose_name=_lazy("Name"),
        unique=True,
        null=False,
        blank=False,
    )
    default_template = models.ForeignKey(
        PETITION_TEMPLATE,
        blank=True,
        null=True,
        related_name="+",
        verbose_name=_lazy("Default petition template"),
        to_field="id",
        on_delete=models.SET_NULL,
    )
    slugname = models.SlugField(max_length=200, unique=True)
    members: models.ManyToManyField = models.ManyToManyField(
        PYTITION_USER, through=PERMISSION
    )

    class Meta:
        """Meta information for the Organization model."""

        db_table = "petition_organization"
        # Translators: Organization model verbose name (in the admin interface)
        verbose_name = _lazy("Organization")
        # Translators: Organization model plural verbose name (in the admin interface)
        verbose_name_plural = _lazy("Organizations")

    def is_last_admin(self, user: PytitionUser) -> bool:
        """Check if the given user is the last admin of this organization Admin is an
        user having the can_modify_permissions right Return true or false."""
        # get all permissions
        from apps.accounts.models import Permission  # noqa

        perms = Permission.objects.filter(
            can_modify_permissions=True, organization=self
        )
        if perms.count() > 1:
            return False
        elif perms.count() == 1:
            perm = perms.first()
            return perm is not None and perm.user == user
        else:
            # That should never happen
            return True

    def is_allowed_to(self, user: PytitionUser, right: str) -> bool:
        """Check if an user has a given access right on the organization."""

        from apps.accounts.models import Permission  # noqa

        try:
            perm = Permission.objects.get(organization=self, user=user)
        except Permission.DoesNotExist:
            return False
        else:
            return bool(getattr(perm, right))

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"< {self.name} >"

    @property
    def owners(self) -> models.QuerySet:
        """Return a QuerySet of users who have permission to modify permissions."""
        return self.members.filter(permission__can_modify_permissions=True)

    @property
    def kind(self) -> str:
        """Return the kind of this entity ("org" for organization)."""
        return "org"

    @property
    def fullname(self) -> str:
        """Return the full name of the organization."""
        return self.name

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Override save to automatically generate slugname from name if not set."""
        if not self.slugname:
            self.slugname = slugify(self.name)
        super().save(*args, **kwargs)
