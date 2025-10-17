from django.db import models
from django.utils.translation import gettext_lazy

# NOTE: This module mirrors legacy 'apps.petition' models but keeps DB tables.
# We preserve table names via Meta.db_table to avoid data copy/downtime.


class Organization(models.Model):
    """Organization entity (moved from apps.petition.models).
    Database table is preserved to avoid data migration.
    """

    name = models.CharField(
        max_length=200, verbose_name=gettext_lazy("Name"), unique=True
    )
    default_template = models.ForeignKey(
        "petitions.PetitionTemplate",  # now lives in apps.petitions
        blank=True,
        null=True,
        related_name="+",
        verbose_name=gettext_lazy("Default petition template"),
        to_field="id",
        on_delete=models.SET_NULL,
    )
    slugname = models.SlugField(max_length=200, unique=True)

    # NOTE: 'members' ManyToMany through Permission → defined below
    # See Permission model's ForeignKeys for the through relation.

    class Meta:
        db_table = "petition_organization"  # ← reuse existing table
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"


class Permission(models.Model):
    """Per-user permissions within an Organization."""

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    user = models.ForeignKey("accounts.PytitionUser", on_delete=models.CASCADE)
    can_create_petition = models.BooleanField(default=False)
    can_modify_permissions = models.BooleanField(default=False)
    can_edit_organization = models.BooleanField(default=False)
    can_delete_organization = models.BooleanField(default=False)
    can_create_template = models.BooleanField(default=False)
    can_edit_template = models.BooleanField(default=False)
    can_delete_template = models.BooleanField(default=False)

    class Meta:
        db_table = "petition_permission"  # ← reuse existing table
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
