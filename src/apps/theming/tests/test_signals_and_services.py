"""Tests for Theme model signals and services."""

from __future__ import annotations

from django.test import TestCase

from apps.organizations.models import Organization
from apps.theming.models import Theme
from apps.theming.services.css_renderer import render_theme_tokens
from apps.theming.tests.common import RegistrySettingsMixin, make_pytition_user


class ThemeSignalsAndServicesTests(RegistrySettingsMixin, TestCase):
    """Tests for post_delete cleanup and CSS rendering service."""

    def test_signal_cleanup_on_owner_delete(self) -> None:
        """Deleting an owner should remove orphan Themes via post_delete signal."""
        p_user = make_pytition_user("bye")
        creator = make_pytition_user("creator")

        t = Theme(
            name="OwnedByUser",
            creator=creator,
            tokens_schema_version="v1",
            tokens_css={":root": {"--bs-body-bg": "#fff"}},
        )
        t.set_owner(p_user)
        t.full_clean()
        t.save()

        p_user.delete()
        self.assertEqual(Theme.objects.filter(name="OwnedByUser").count(), 0)

    def test_service_render_theme_tokens_produces_css(self) -> None:
        """Rendering service should output CSS from JSON tokens."""
        org = Organization.objects.create(name="Acme")
        creator = make_pytition_user("creator")

        t = Theme(
            name="R",
            creator=creator,
            tokens_schema_version="v1",
            tokens_css={
                ":root": {"--bs-body-bg": "#ffffff"},
                '[data-bs-theme="dark"]': {"--bs-body-bg": "#000000"},
            },
        )
        t.set_owner(org)
        t.full_clean()

        css: str = render_theme_tokens(t)
        self.assertIn(":root {", css)
        self.assertIn("--bs-body-bg: #ffffff;", css)
        self.assertIn('[data-bs-theme="dark"] {', css)
        self.assertIn("--bs-body-bg: #000000;", css)
