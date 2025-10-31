from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models, transaction
from django.utils.translation import gettext_lazy

from apps.core.model_refs import ORGANIZATION, PETITION_TEMPLATE

if TYPE_CHECKING:
    pass


class PytitionUser(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pytitionuser"
    )
    invitations: models.ManyToManyField = models.ManyToManyField(
        ORGANIZATION, related_name="invited", blank=True
    )
    default_template = models.ForeignKey(
        PETITION_TEMPLATE,
        blank=True,
        null=True,
        related_name="+",
        verbose_name=gettext_lazy("Default petition template"),
        to_field="id",
        on_delete=models.SET_NULL,
    )
    moderated = models.BooleanField(default=False)

    class Meta:
        db_table = "petition_pytitionuser"
        verbose_name = gettext_lazy("Pytition User")
        verbose_name_plural = gettext_lazy("Pytition Users")

    def drop(self) -> None:
        with transaction.atomic():
            orgs = list(self.organization_set.all())
            petitions = list(self.petition_set.all())
            templates = list(self.petitiontemplate_set.all())
            self.delete()
            for org in orgs:
                if org.members.count() == 0:
                    org.delete()
            for petition in petitions:
                petition.delete()
            for template in templates:
                template.delete()

    def moderate(self, do_moderate: bool = True) -> None:
        self.moderated = do_moderate
        self.save()

    @property
    def is_authenticated(self) -> bool:
        return self.user.is_authenticated

    @property
    def name(self) -> str:
        return self.username

    @property
    def username(self) -> str:
        return self.user.username if self.user is not None else ""

    @property
    def get_full_name(self) -> str:
        return self.user.get_full_name()

    @property
    def fullname(self) -> str:
        return self.get_full_name

    @property
    def kind(self) -> str:
        return "user"

    def __str__(self) -> str:
        if self.get_full_name != "":
            return self.get_full_name
        else:
            return self.username

    def __repr__(self) -> str:
        if self.get_full_name != "":
            return self.get_full_name
        else:
            return self.username
