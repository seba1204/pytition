"""Permission model for user permissions within an organization."""

from __future__ import annotations

from collections.abc import Generator

from django.db import models
from django.utils.translation import gettext_lazy as _lazy

from apps.core.model_refs import ORGANIZATION, PYTITION_USER


class Permission(models.Model):
    """Model representing user permissions within an organization."""

    organization = models.ForeignKey(
        ORGANIZATION,
        on_delete=models.CASCADE,
        verbose_name=_lazy("Organization related to these permissions"),
    )
    user = models.ForeignKey(
        PYTITION_USER,
        on_delete=models.CASCADE,
        verbose_name=_lazy("User related to these permissions"),
    )
    can_remove_members = models.BooleanField(
        default=False, verbose_name=_lazy("Can remove member?")
    )
    can_add_members = models.BooleanField(
        default=False, verbose_name=_lazy("Can invite new members?")
    )
    can_create_petitions = models.BooleanField(
        default=True, verbose_name=_lazy("Can create petitions?")
    )
    can_modify_petitions = models.BooleanField(
        default=True, verbose_name=_lazy("Can modify petitions?")
    )
    can_delete_petitions = models.BooleanField(
        default=False, verbose_name=_lazy("Can delete petitions?")
    )
    can_create_templates = models.BooleanField(
        default=True, verbose_name=_lazy("Can create petition templates?")
    )
    can_modify_templates = models.BooleanField(
        default=True, verbose_name=_lazy("Can modify petition templates?")
    )
    can_delete_templates = models.BooleanField(
        default=False, verbose_name=_lazy("Can delete petition templates?")
    )
    can_view_signatures = models.BooleanField(
        default=False, verbose_name=_lazy("Can view signatures?")
    )
    can_modify_signatures = models.BooleanField(
        default=False, verbose_name=_lazy("Can modify signatures?")
    )
    can_delete_signatures = models.BooleanField(
        default=False, verbose_name=_lazy("Can delete signatures?")
    )
    can_modify_permissions = models.BooleanField(
        default=False, verbose_name=_lazy("Can modify permissions?")
    )

    class Meta:
        """Meta class for Permission model."""

        db_table = "petition_permission"
        unique_together = ("organization", "user")
        verbose_name = _lazy("Permission")
        verbose_name_plural = _lazy("Permissions")

    def set_all(self, value: bool) -> None:
        """Set all permission fields to the given value."""
        self.can_add_members = value
        self.can_remove_members = value
        self.can_create_petitions = value
        self.can_modify_petitions = value
        self.can_delete_petitions = value
        self.can_create_templates = value
        self.can_modify_templates = value
        self.can_delete_templates = value
        self.can_view_signatures = value
        self.can_modify_signatures = value
        self.can_delete_signatures = value
        self.can_modify_permissions = value
        self.save()

    def iter_perm_fields(self) -> Generator[tuple[str, str, bool], None, None]:
        """Yield (name, label, value) for all boolean 'can_*' fields."""
        for f in self._meta.get_fields():
            if isinstance(f, models.BooleanField) and f.name.startswith("can_"):
                yield f.name, str(f.verbose_name), bool(getattr(self, f.name))

    def __str__(self) -> str:
        """Return a string representation of the permission."""
        return f"{self.organization.name} : {self.user.name}"

    def __repr__(self) -> str:
        """Return a string representation for debugging purposes."""
        return f"< {self.__str__()} >"
