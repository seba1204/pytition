"""Tests for Theme model uniqueness under race-like conditions."""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.theming.models import Theme
from apps.theming.tests.common import RegistrySettingsMixin, make_pytition_user


class ThemeRaceLikeUniquenessTests(RegistrySettingsMixin, TestCase):
    """
    Tests about uniqueness under concurrent-like conditions.

    Notes
    -----
    We cannot easily reproduce a real race in unit tests, but we can still
    validate that two inserts with the same name end up unique.
    """

    def setUp(self) -> None:
        """Create a single creator user reused across tests to avoid duplicates."""
        self.creator = make_pytition_user("creator_race")

    def _mk(self, name: str, *, owner_username: str = "owner_race") -> Theme:
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

    def test_two_inserts_same_name_result_in_distinct_slugs(self) -> None:
        """Back-to-back creates with identical names produce unique slugs."""
        a = self._mk("Same Name", owner_username="owner_race_a")
        b = self._mk("Same Name", owner_username="owner_race_b")
        self.assertNotEqual(a.slug, b.slug)
        self.assertEqual(a.slug, "same-name")
        self.assertEqual(b.slug, "same-name-1")

    def test_manual_duplicate_slug_raises_validation_then_recovers_on_resave(
        self,
    ) -> None:
        """
        Duplicate slug triggers en error clearing slug then regenerates a unique value.

        Notes
        -----
        - Because the model calls `full_clean()` inside `save()`, Django's
        `validate_unique` raises `ValidationError` before hitting the DB.
        - We then clear `slug` to let the model auto-generate a new unique slug
        on the next save.
        """
        first = self._mk("Alpha")
        owner = make_pytition_user("owner_dup")
        creator_dup = make_pytition_user("creator_dup")

        second = Theme(
            name="Beta",
            slug=first.slug,  # force a duplicate
            creator=creator_dup,
            tokens_schema_version="v1",
            tokens_css={":root": {}},
        )
        second.set_owner(owner)

        # 1) First save should fail with ValidationError
        # (unique constraint at validation time)
        with self.assertRaises(ValidationError):
            second.save()

        # 2) Clear slug to force auto-generation, then save successfully
        second.slug = ""  # let the model build a unique slug
        second.save()

        self.assertNotEqual(second.slug, first.slug)
        self.assertTrue(
            second.slug.startswith("beta") or second.slug.startswith("alpha")
        )
