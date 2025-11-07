"""Theme model definition."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from typing import Any, cast
from uuid import uuid4

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError, models, transaction
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext_lazy as _lazy

from apps.core.model_refs import PYTITION_USER
from apps.theming.registry import CssTokenRegistry
from apps.theming.validators import ThemeQuerySet


class Theme(models.Model):
    """
    Model representing a custom user theme.

    Notes
    -----
    - Strongly typed for mypy.
    - Docstrings follow the Numpy convention.
    - Comments are in English as requested.
    """

    # --- Identity / labeling ------------------------------------------------------
    name = models.CharField(
        max_length=100,
        verbose_name=_lazy("Theme name"),
        help_text=_lazy("Short human-readable name for this theme."),
    )
    slug: models.SlugField = models.SlugField(
        max_length=160,
        unique=True,
        blank=True,
        verbose_name=_lazy("Slug"),
        help_text=_lazy("A unique identifier for the theme (auto generated)."),
    )
    description: models.TextField = models.TextField(
        blank=True,
        verbose_name=_lazy("Description"),
        help_text=_lazy("Optional description of the theme."),
    )
    etag = models.CharField(
        max_length=32,
        blank=True,
        editable=False,  # non-editable: cache-only field
        verbose_name=_lazy("ETag"),
        help_text=_lazy("Hash of concatenated CSS for caching purpose."),
    )

    # --- Creator (who created the theme record) ----------------------------------
    creator: models.ForeignKey = models.ForeignKey(
        PYTITION_USER,
        on_delete=models.PROTECT,
        related_name="created_themes",
        help_text=_lazy("User who created this theme."),
    )

    # --- Generic owner (user OR organization OR anything else) -------------------
    owner_content_type: models.ForeignKey[ContentType] = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="theme_owners",
        help_text=_lazy("Django content type for the owner."),
    )
    owner_object_id = models.CharField(
        max_length=255,
        verbose_name=_lazy("Owner object ID"),
        help_text=_lazy("Primary key of the owner instance."),
    )
    owner: GenericForeignKey = GenericForeignKey(
        ct_field="owner_content_type",
        fk_field="owner_object_id",
    )

    # --- Theme data ---------------------------------------------------------------
    tokens_schema_version = models.CharField(
        max_length=20,
        default="v1",
        help_text=_lazy("Version of the token registry used to validate tokens_css."),
    )
    tokens_css: models.JSONField[dict[str, dict[str, Any]]] = models.JSONField(
        default=dict,
        help_text=_lazy(
            'Mapping of CSS tokens per scope (:root, [data-bs-theme="dark"]).'
        ),
    )
    components_css: models.TextField = models.TextField(
        blank=True,
        verbose_name=_lazy("Components CSS"),
        help_text=_lazy("Custom sanitized CSS to be included in the theme."),
    )

    # --- Metadata -----------------------------------------------------------------
    is_public: models.BooleanField = models.BooleanField(
        default=False,
        verbose_name=_lazy("Is public"),
        help_text=_lazy("Whether this theme is publicly available to other users."),
    )
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_lazy("Created at"),
        help_text=_lazy("Timestamp when the theme was created."),
    )
    updated_at: models.DateTimeField = models.DateTimeField(
        auto_now=True,
        verbose_name=_lazy("Updated at"),
        help_text=_lazy("Timestamp when the theme was last updated."),
    )

    # Manager
    objects = ThemeQuerySet.as_manager()

    class Meta:
        """Meta configuration for the Theme model."""

        verbose_name = _lazy("Theme")
        verbose_name_plural = _lazy("Themes")

    # --- Magic methods ------------------------------------------------------------
    def __str__(self) -> str:  # pragma: no cover - trivial
        """Human-friendly representation."""
        return self.name

    def __repr__(self) -> str:  # pragma: no cover - avoid GFK DB hits
        """Debug representation that does not dereference GenericForeignKey."""
        return (
            f"<Theme id={self.pk} name={self.name!r} "
            f"owner_ct={self.owner_content_type_id} owner_id={self.owner_object_id}>"
        )

    # --- Public API ---------------------------------------------------------------
    def get_tokens(self) -> dict[str, dict[str, str]]:
        """
        Return the tokens_css as a mapping of scope -> {token_name: value}.

        Returns
        -------
        dict[str, dict[str, str]]
            Mapping of scope to token name-value pairs (stringified).
        """
        return {
            scope: {
                k: str(v) for k, v in tokens.items() if isinstance(v, (str, int, float))
            }
            for scope, tokens in self.tokens_css.items()
        }

    def set_owner(self, owner: models.Model) -> None:
        """
        Set the generic owner, storing a stringified PK.

        Parameters
        ----------
        owner : models.Model
            Concrete owner instance (user, organization, etc.).
        """
        owner_ct = ContentType.objects.get_for_model(owner, for_concrete_model=False)
        self.owner_content_type = owner_ct
        self.owner_object_id = str(owner.pk)

    def get_owner_pk(self) -> str:
        """
        Return owner's primary key as a string.

        Returns
        -------
        str
            The stored owner PK (stringified).
        """
        return self.owner_object_id

    def get_owner_ct(self) -> ContentType:
        """
        Return the owner's content type.

        Returns
        -------
        ContentType
            Stored content type for the owner.
        """
        return cast(ContentType, self.owner_content_type)

    def owner_label(self) -> str:
        """
        Return a compact human-readable label for the owner.

        Returns
        -------
        str
            String like 'App.Model#<pk>'.
        """
        ct_id = self.owner_content_type_id
        obj_id = getattr(self, "owner_object_id", None)
        if not ct_id or not obj_id:
            return "—"
        try:
            ct = ContentType.objects.get_for_id(ct_id)
        except ContentType.DoesNotExist:
            return f"unknown_ct #{obj_id}"
        return f"{ct.app_label}.{ct.model} #{obj_id}"

    def to_css(self) -> str:
        """
        Render the full CSS for this theme (tokens + components).

        Returns
        -------
        str
            The complete CSS string for the theme.
        """
        # Import locally to avoid circular imports at module import time.
        from apps.theming.services import render_theme_tokens  # noqa

        tokens_css = render_theme_tokens(self)
        if self.components_css:
            return tokens_css + "\n\n" + str(self.components_css)
        return tokens_css

    # --- Internal helpers ---------------------------------------------------------
    def _build_unique_slug(self, using: str | None = None) -> str:
        """
        Build a unique slug for this instance.

        Parameters
        ----------
        using : str or None
            Optional DB alias to perform uniqueness checks.

        Returns
        -------
        str
            A unique slug candidate for the current instance.

        Notes
        -----
        Excludes the current instance (by PK) to avoid false positives on updates.
        """
        base = slugify(self.name) or "theme"
        slug = base
        counter = 1

        qs = Theme.objects.all()
        if using is not None:
            qs = qs.using(using)
        qs = qs.exclude(pk=self.pk)

        while qs.filter(slug=slug).exists():
            slug = f"{base}-{counter}"
            counter += 1
        return slug

    def _compute_etag(self) -> str:
        """
        Compute a stable hash representing the effective CSS payload.

        Returns
        -------
        str
            Lowercase hexadecimal MD5 digest.
        """
        tokens_json = json.dumps(self.tokens_css, sort_keys=True, separators=(",", ":"))
        payload = f"{self.slug}\n{tokens_json}\n{self.components_css}"
        return hashlib.md5(payload.encode("utf-8")).hexdigest()

    # --- Validation & persistence -------------------------------------------------
    def clean(self) -> None:
        """
        Validate tokens and owner; optionally auto-fill slug for forms/admin.

        Notes
        -----
        - Coerces THEME_ALLOWED_TOKEN_SCOPES to a set of strings.
        - Validates that owner exists.
        - Fills slug if missing (for ergonomics when forms/admin call full_clean()).
        """
        if not isinstance(self.tokens_css, dict):
            raise ValidationError("tokens_css must be an object")

        # Allowed scopes from settings; coerce to a set[str]
        allowed_scopes_cfg = getattr(settings, "THEME_ALLOWED_TOKEN_SCOPES", None)
        if allowed_scopes_cfg is None:
            raise ValidationError(
                _("THEME_ALLOWED_TOKEN_SCOPES setting is not defined.")
            )
        try:
            allowed_scopes: set[str] = set(map(str, allowed_scopes_cfg))
        except TypeError as exc:
            raise ValidationError(
                _("THEME_ALLOWED_TOKEN_SCOPES must be an iterable of strings.")
            ) from exc

        invalid_scopes = set(self.tokens_css.keys()) - allowed_scopes
        if invalid_scopes:
            raise ValidationError(
                _("Invalid token scopes: %(scopes)s")
                % {"scopes": ", ".join(sorted(invalid_scopes))}
            )

        registry = CssTokenRegistry(self.tokens_schema_version)
        registry.validate_tokens(self.tokens_css)

        # Ensure GFK owner exists
        if not self.owner_content_type_id or not self.owner_object_id:
            raise ValidationError({"owner": _("Owner must be set.")})

        try:
            ct = cast(ContentType, self.owner_content_type)
            model_cls = ct.model_class()
            if model_cls is None:
                raise ValidationError({"owner": _("Invalid content type for owner.")})
            ct.get_object_for_this_type(pk=self.owner_object_id)
        except ObjectDoesNotExist as exc:
            raise ValidationError({"owner": _("Owner object does not exist.")}) from exc

        # Pre-fill slug for admin/forms ergonomics (save() also safeguards this).
        if not self.slug:
            self.slug = self._build_unique_slug()

        super().clean()

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Persist the model, auto-generating a unique slug and ETag if needed.

        Parameters
        ----------
        *args : Any
            Positional parameters forwarded to Django's ``Model.save``.
        **kwargs : Any
            Keyword parameters forwarded to Django's ``Model.save``. Common keys are:
            - force_insert : bool
            - force_update : bool
            - using : str or None
            - update_fields : Sequence[str] or None
        """
        using = cast(str | None, kwargs.get("using"))
        update_fields = cast(Sequence[str] | None, kwargs.get("update_fields"))

        will_update_slug = update_fields is None or "slug" in update_fields
        if will_update_slug and not self.slug:
            self.slug = self._build_unique_slug(using=using)

        # Validate prior to saving for consistent errors
        self.full_clean()

        # Refresh ETag if any contributing field may change
        contributes = {"slug", "tokens_css", "components_css"}
        will_update_etag = update_fields is None or any(
            f in contributes for f in (update_fields or ())
        )
        if will_update_etag:
            self.etag = self._compute_etag()

        try:
            with transaction.atomic(using=using):
                super().save(*args, **kwargs)
        except IntegrityError:
            # Rare race: another row took the slug between exists() and save()
            if will_update_slug:
                base = slugify(self.name) or "theme"
                self.slug = f"{base}-{uuid4().hex[:6]}"
                if will_update_etag:
                    self.etag = self._compute_etag()
            with transaction.atomic(using=using):
                super().save(*args, **kwargs)
