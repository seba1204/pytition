"""Tests for Theme.components_css sanitization via Theme.clean()."""

from __future__ import annotations

from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.models import PytitionUser
from apps.organizations.models import Organization
from apps.theming.models import Theme

from .common import compact_css


def _make_p_user(username: str | None = None) -> PytitionUser:
    """Create or retrieve a PytitionUser linked to AUTH_USER_MODEL."""
    BaseUser = get_user_model()
    uname: str = username or f"test_{uuid4().hex[:8]}"
    auth = BaseUser.objects.create_user(username=uname, password="x")
    try:
        return auth.pytitionuser  # signal should have created it
    except PytitionUser.DoesNotExist:
        return PytitionUser.objects.create(user=auth)


def _make_org(slug: str | None = None, name: str | None = None) -> Organization:
    """Create a simple Organization with a unique slug."""
    s = slug or f"org-{uuid4().hex[:6]}"
    n = name or f"Org {s}"
    return Organization.objects.create(name=n)


class ThemeComponentsCssTests(TestCase):
    """Integration tests for Theme.components_css sanitization via Theme.clean()."""

    def setUp(self) -> None:
        """Create common test users and orgs."""
        self.creator = _make_p_user("creator_css")
        self.owner = _make_org()

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
