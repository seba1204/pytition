from __future__ import annotations

import html
import uuid
from typing import Any

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy
from phonenumber_field.modelfields import PhoneNumberField  # type: ignore

from apps.core.model_refs import PETITION


class Signature(models.Model):
    first_name = models.CharField(
        max_length=50, verbose_name=gettext_lazy("First name")
    )
    last_name = models.CharField(max_length=50, verbose_name=gettext_lazy("Last name"))
    phone = PhoneNumberField(
        max_length=20, blank=True, verbose_name=gettext_lazy("Phone number")
    )
    email = models.EmailField(verbose_name=gettext_lazy("Email address"))
    confirmation_hash = models.CharField(max_length=128)
    confirmed = models.BooleanField(
        default=False, verbose_name=gettext_lazy("Confirmed")
    )
    petition = models.ForeignKey(
        PETITION, on_delete=models.CASCADE, verbose_name=gettext_lazy("Petition")
    )
    subscribed_to_mailinglist = models.BooleanField(
        default=False, verbose_name=gettext_lazy("Subscribed to mailing list")
    )
    date = models.DateTimeField(
        blank=True, auto_now_add=True, verbose_name=gettext_lazy("Date")
    )
    ipaddress = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "petition_signature"
        verbose_name = gettext_lazy("Signature")
        verbose_name_plural = gettext_lazy("Signatures")

    def clean(self) -> None:
        if (
            self.petition.already_signed(self.email)
            and self.petition.signature_set.filter(email=self.email)
            .get(confirmed=True)
            .id
            != self.id
        ):
            raise ValidationError(_("You already signed the petition"))

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.clean()
        if not self.confirmation_hash:
            self.confirmation_hash = str(uuid.uuid4())
        if self.confirmed:
            # invalidating other signatures from same email
            Signature.objects.filter(petition=self.petition).filter(
                email=self.email
            ).exclude(id=self.id).delete()
        super().save(*args, **kwargs)

    def confirm(self) -> None:
        self.confirmed = True

    def __str__(self) -> str:
        return html.unescape(
            "[{}:{}] {} {}".format(
                self.petition.id,
                "OK" if self.confirmed else "..",
                self.first_name,
                self.last_name,
            )
        )

    def __repr__(self) -> str:
        return html.unescape(
            "[{}:{}] {} {}".format(
                self.petition.id,
                "OK" if self.confirmed else "..",
                self.first_name,
                self.last_name,
            )
        )
