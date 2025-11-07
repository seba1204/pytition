"""Tests focusing on Theme model slug creation behavior."""

from __future__ import annotations

from typing import Final

from django.test import TestCase

from apps.theming.models import Theme
from apps.theming.tests.common import RegistrySettingsMixin, make_pytition_user


class ThemeSlugCreationTests(RegistrySettingsMixin, TestCase):
    """Tests focusing on slug auto-generation during creation."""

    ROOT_SCOPE: Final[str] = ":root"

    def setUp(self) -> None:
        """Create a single creator user reused across tests to avoid duplicates."""
        self.creator = make_pytition_user("creator_slug")

    def _mk_theme(
        self,
        name: str,
        owner_username: str = "owner_slug",
        *,
        slug: str | None = None,
    ) -> Theme:
        """
        Create and persist a Theme with minimal required fields.

        Parameters
        ----------
        name : str
            Theme name used to derive the slug.
        owner_username : str, optional
            Username for the owner (Generic owner is set to this User).
        slug : str or None, optional
            Optional pre-defined slug to preserve.

        Returns
        -------
        Theme
            Persisted Theme instance with an owner set.
        """
        owner = make_pytition_user(owner_username)

        t = Theme(
            name=name,
            creator=self.creator,
            tokens_schema_version="v1",
            tokens_css={self.ROOT_SCOPE: {}},
        )
        if slug is not None:
            t.slug = slug
        t.set_owner(owner)
        t.full_clean()
        t.save()
        return t

    def test_auto_slug_generated_when_missing(self) -> None:
        """Slug is auto-generated from `name` when not provided."""
        t = self._mk_theme("My Pretty Theme")
        self.assertEqual(t.slug, "my-pretty-theme")

    def test_given_slug_is_preserved(self) -> None:
        """Slug explicitly provided by the caller must not be overwritten."""
        t = self._mk_theme("Another Theme", slug="custom-slug")
        self.assertEqual(t.slug, "custom-slug")

    def test_unique_enforcement_with_increment(self) -> None:
        """When a slug already exists, a numeric suffix is appended."""
        first = self._mk_theme("Cloned", owner_username="owner_slug_a")
        self.assertEqual(first.slug, "cloned")

        second = self._mk_theme("Cloned", owner_username="owner_slug_b")
        self.assertEqual(second.slug, "cloned-1")

        third = self._mk_theme("Cloned", owner_username="owner_slug_c")
        self.assertEqual(third.slug, "cloned-2")

    def test_unicode_name_slugifies(self) -> None:
        """Non-ASCII names are slugified correctly."""
        t = self._mk_theme("Thème très élégant")
        self.assertEqual(t.slug, "theme-tres-elegant")
