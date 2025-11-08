"""Tests for Theme model slug behavior on updates."""

from __future__ import annotations

from django.test import TestCase

from apps.theming.models import Theme
from apps.theming.tests.common import RegistrySettingsMixin, make_pytition_user


class ThemeSlugUpdateBehaviorTests(RegistrySettingsMixin, TestCase):
    """Tests focusing on slug behavior on updates."""

    def setUp(self) -> None:
        """Create a single creator user reused across tests to avoid duplicates."""
        self.creator = make_pytition_user("creator_update")

    def _mk(self, name: str, *, owner_username: str = "owner_update") -> Theme:
        """Create and persist a minimal valid Theme (with owner + required fields)."""
        owner = make_pytition_user(owner_username)

        t = Theme(
            name=name,
            creator=self.creator,
            tokens_schema_version="v1",
            tokens_css={":root": {}},
        )
        t.set_owner(owner)
        t.full_clean()
        t.save()
        return t

    def test_rename_does_not_change_existing_slug(self) -> None:
        """Changing `name` after creation keeps the existing slug stable."""
        t = self._mk("Stable Name")
        self.assertEqual(t.slug, "stable-name")

        t.name = "New Label"
        t.full_clean()
        t.save()
        self.assertEqual(t.slug, "stable-name")

    def test_update_fields_does_not_touch_slug_if_excluded(self) -> None:
        """When `update_fields` excludes `slug`, DB slug should remain untouched."""
        t = self._mk("Locked Slug")
        self.assertEqual(t.slug, "locked-slug")

        # Clear slug in memory and save only 'name'
        t.slug = ""
        t.name = "Locked Slug Renamed"
        t.full_clean()
        t.save(update_fields=["name"])

        # Reload from DB to verify the persisted slug is unchanged
        t.refresh_from_db()
        self.assertEqual(t.slug, "locked-slug")
        self.assertEqual(t.name, "Locked Slug Renamed")
