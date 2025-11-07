"""Validation tests for Theme model and token registry integration."""

from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.models import PytitionUser
from apps.organizations.models import Organization
from apps.theming.models import Theme
from apps.theming.tests.common import RegistrySettingsMixin, make_pytition_user


class ThemeValidationTests(RegistrySettingsMixin, TestCase):
    """Validation tests for Theme.clean() and token registry integration."""

    def test_clean_owner_exists_ok(self) -> None:
        """`clean()` passes when GFK owner (PytitionUser) exists."""
        p_user = make_pytition_user("ok-owner")
        creator = make_pytition_user("creator")

        t = Theme(
            name="Ok",
            creator=creator,
            tokens_schema_version="v1",
            tokens_css={":root": {"--bs-body-bg": "#ffffff"}},
        )
        t.set_owner(p_user)
        t.full_clean()  # should not raise

    def test_clean_owner_missing_raises(self) -> None:
        """`clean()` fails when GFK points to a non-existent PytitionUser."""
        ct = ContentType.objects.get_for_model(PytitionUser, for_concrete_model=False)
        creator = make_pytition_user("creator")

        t = Theme(
            name="Ko",
            creator=creator,
            tokens_schema_version="v1",
            tokens_css={":root": {"--bs-body-bg": "#000000"}},
        )
        t.owner_content_type = ct
        t.owner_object_id = "999999"  # non-existent user PK
        with self.assertRaises(ValidationError) as ctx:
            t.full_clean()
        self.assertIn("Owner object does not exist", str(ctx.exception))

    def test_tokens_valid_against_v1(self) -> None:
        """Known tokens in v1 validate for :root and dark scopes."""
        org = Organization.objects.create(name="An Org")
        creator = make_pytition_user("creator")

        t = Theme(
            name="Tokens OK v1",
            creator=creator,
            tokens_schema_version="v1",
            tokens_css={
                ":root": {
                    "--bs-body-bg": "#ffffff",
                    "--bs-border-radius": "4px",
                },
                '[data-bs-theme="dark"]': {"--bs-body-bg": "#000000"},
            },
        )
        t.set_owner(org)
        t.full_clean()  # should not raise

    def test_tokens_unknown_raises(self) -> None:
        """Unknown token name should raise a ValidationError."""
        org = Organization.objects.create(name="An Org")
        creator = make_pytition_user("creator")

        t = Theme(
            name="Tokens KO",
            creator=creator,
            tokens_schema_version="v1",
            tokens_css={":root": {"--bs-unknown": "10px"}}, # unknown token
        )
        t.set_owner(org)
        with self.assertRaises(ValidationError) as ctx:
            t.full_clean()
        self.assertIn("--bs-unknown", str(ctx.exception))

    def test_scope_validation_rejects_invalid_scope(self) -> None:
        """Invalid scope key must be rejected by clean()."""
        org = Organization.objects.create(name="An Org")
        creator = make_pytition_user("creator")

        t = Theme(
            name="Bad scope",
            creator=creator,
            tokens_schema_version="v1",
            tokens_css={"body": {"--bs-body-bg": "#fff"}},
        )
        t.set_owner(org)
        with self.assertRaises(ValidationError) as ctx:
            t.full_clean()
        self.assertIn("Invalid token scopes", str(ctx.exception))

    def test_version_upgrade_accepts_new_tokens(self) -> None:
        """Newer version (v2) should allow additional tokens."""
        org = Organization.objects.create(name="An Org")
        creator = make_pytition_user("creator")

        t = Theme(
            name="v2 tokens ok",
            creator=creator,
            tokens_schema_version="v2",
            tokens_css={
                ":root": {"--bs-body-bg": "#ffffff", "--bs-body-font-size": "1rem"}
            },
        )
        t.set_owner(org)
        t.full_clean()  # should not raise
