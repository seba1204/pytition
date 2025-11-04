"""Permission model for user permissions within an organization."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy

from apps.core.model_refs import ORGANIZATION, PYTITION_USER


class Permission(models.Model):
    """Model representing user permissions within an organization."""

    organization = models.ForeignKey(
        ORGANIZATION,
        on_delete=models.CASCADE,
        verbose_name=gettext_lazy("Organization related to these permissions"),
    )
    user = models.ForeignKey(
        PYTITION_USER,
        on_delete=models.CASCADE,
        verbose_name=gettext_lazy("User related to these permissions"),
    )
    can_add_members = models.BooleanField(default=False)
    can_remove_members = models.BooleanField(default=False)
    can_create_petitions = models.BooleanField(default=True)
    can_modify_petitions = models.BooleanField(default=True)
    can_delete_petitions = models.BooleanField(default=False)
    can_create_templates = models.BooleanField(default=True)
    can_modify_templates = models.BooleanField(default=True)
    can_delete_templates = models.BooleanField(default=False)
    can_view_signatures = models.BooleanField(default=False)
    can_modify_signatures = models.BooleanField(default=False)
    can_delete_signatures = models.BooleanField(default=False)
    can_modify_permissions = models.BooleanField(default=False)

    class Meta:
        """Meta class for Permission model."""

        db_table = "petition_permission"
        unique_together = ("organization", "user")
        verbose_name = gettext_lazy("Permission")
        verbose_name_plural = gettext_lazy("Permissions")

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

    def __str__(self) -> str:
        return f"{self.organization.name} : {self.user.name}"

    def __repr__(self) -> str:
        return f"< {self.__str__()} >"
