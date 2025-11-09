"""Base model for sub-configuration items."""

from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy

from apps.core.model_refs import CONFIG_BUNDLE


class BaseSubConfig(models.Model):
    """
    Abstract base for all sub-config models.

    Notes
    -----
    - Each sub-config is one-to-one with a bundle.
    - Validation ensures the sub-config type is authorized for the bundle's scope type.
    """

    name = models.CharField(
        max_length=255,
        verbose_name=_lazy("Name"),
        help_text=_lazy("A human-readable name for this sub-configuration."),
    )
    bundle = models.OneToOneField(
        CONFIG_BUNDLE,
        on_delete=models.CASCADE,
        related_name="%(class)s_item",
        verbose_name=_lazy("Configuration bundle"),
        help_text=_lazy("The configuration bundle this sub-config belongs to."),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_lazy("Created at"),
        help_text=_lazy("Timestamp when this sub-config was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_lazy("Updated at"),
        help_text=_lazy("Timestamp when this sub-config was last updated."),
    )

    class Meta:
        """Meta options."""

        abstract = True

    def clean(self) -> None:
        """
        Validate that this sub-config is allowed by the bundle scope.

        The scope class is fetched from ``self.config.scope_ct`` and must
        expose a class attribute ``config`` (sequence of BaseSubConfig
        subclasses). This sub-config's class must be present in that list.

        Raises
        ------
        ValidationError
            If the scope class does not allow this sub-config class.
        """
        if self.bundle is None:
            raise ValidationError(_("SubConfig must be attached to a ConfigBundle."))

        # Resolve the scope model class from bundle.scope_ct
        scope_model = self.bundle.scope_ct.model_class()
        if scope_model is None:
            raise ValidationError(
                _("Cannot resolve scope model class from ConfigBundle.")
            )

        # Read config contract from the scope class (HasConfig subclasses)
        instance_cfgs: dict[str, str] = getattr(scope_model, "config", {})
        if instance_cfgs is None:
            raise ValidationError(
                _("Scope model %(model)s must define config attribute.")
                % {"model": scope_model.__name__}
            )
        if not isinstance(instance_cfgs, dict):
            raise ValidationError(
                _("Scope model %(model)s config attribute must be a dict.")
                % {"model": scope_model.__name__}
            )

        # Check membership by subclassing (supports inheritance)

        current_cls: type[BaseSubConfig] = self.__class__
        # instance_cfgs is a dict of field_name to model path
        # e.g. { "mail_config": "notifications.MailConfig" }
        # check if current_cls is subclass of any allowed config class
        is_allowed = any(
            issubclass(
                current_cls,
                scope_model._meta.apps.get_model(model_path),
            )
            for model_path in instance_cfgs.values()
        )

        if not is_allowed:
            raise ValidationError(
                _(
                    "Sub-config of type %(sub_config)s is not allowed "
                    "for scope model %(model)s."
                )
                % {"sub_config": current_cls.__name__, "model": scope_model.__name__}
            )

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Run full validation before saving.

        Parameters
        ----------
        *args : Any
            Positional args to pass to super().
        **kwargs : Any
            Keyword args to pass to super().
        """
        self.full_clean()
        super().save(*args, **kwargs)
