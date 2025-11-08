"""Tests for Theme.components_css sanitization via Theme.clean()."""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.theming.models import Theme
from apps.theming.tests.common import (
    RegistrySettingsMixin,
    make_org,
    make_pytition_user,
)

from .common import compact_css


class ThemeComponentsCssTests(RegistrySettingsMixin, TestCase):
    """Integration tests for Theme.components_css sanitization via Theme.clean()."""

    def setUp(self) -> None:
        """Create common test users and orgs."""
        self.creator = make_pytition_user("creator_css")
        self.owner = make_org()

    def _base_theme(self) -> Theme:
        """Create an unsaved Theme with required fields populated."""
        t = Theme(
            name="T",
            creator=self.creator,
            tokens_schema_version="v1",
            tokens_css={":root": {"--bs-body-bg": "#ffffff"}},
            components_css="",  # will be set per test
        )
        t.set_owner(self.owner)
        return t

    def test_components_css_is_sanitized_on_clean(self) -> None:
        """Valid CSS is kept; disallowed declarations are removed."""
        t = self._base_theme()
        t.components_css = """
        /* overrides */
        .btn { background-color: #000; zoom: 1; }
        :root { --accent: #0d6efd; behavior: url(#x); }
        """
        # Should sanitize in-place (Theme.clean assigns sanitized string)
        t.full_clean()
        squeezed = compact_css(t.components_css)
        self.assertIn(".btn{background-color:#000}", squeezed)
        self.assertIn(":root{--accent:#0d6efd}", squeezed)
        self.assertNotIn("zoom:", t.components_css)
        self.assertNotIn("behavior:", t.components_css)

    def test_components_css_rejects_unsafe_values(self) -> None:
        """Unsafe values (javascript:, expression()) should raise ValidationError."""
        t = self._base_theme()
        t.components_css = ".x{background-image:url(javascript:alert(1))}"
        with self.assertRaises(ValidationError) as ctx:
            t.full_clean()
        msg = str(ctx.exception).lower()
        self.assertIn("unsafe", msg)

    def test_components_css_blocks_url_by_default(self) -> None:
        """Url() should be rejected by default policy wired in Theme.clean()."""
        t = self._base_theme()
        t.components_css = ".x{background-image:url(/img/a.png)}"
        with self.assertRaises(ValidationError):
            t.full_clean()

    def test_components_css_keeps_media_supports(self) -> None:
        """@media/@supports blocks are preserved and sanitized inside."""
        t = self._base_theme()
        t.components_css = """
        @supports (display: grid) { .wrap { background-color: #fff; behavior: url(#x) }}
        @media (min-width: 600px) { .card { color: #222; zoom: 1 } }
        """
        t.full_clean()
        compact = compact_css(t.components_css)
        self.assertIn("@media", compact)
        self.assertIn(".card{color:#222}", compact)
        self.assertNotIn("zoom:", compact)
        self.assertIn("@supports", compact)
        self.assertIn(".wrap{background-color:#fff}", compact)
        self.assertNotIn("behavior:", compact)

    def test_components_css_all_removed_is_error(self) -> None:
        """If sanitizer removes all content, should raise ValidationError."""
        t = self._base_theme()
        t.components_css = "@import url(a.css);"
        with self.assertRaises(ValidationError):
            t.full_clean()
