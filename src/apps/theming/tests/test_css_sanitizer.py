"""Unit tests for the cssutils-based CSS sanitizer."""

from __future__ import annotations

from django.test import TestCase

from apps.theming.services.css_sanitizer import sanitize_css

from .common import compact_css


class CssSanitizerTests(TestCase):
    """
    Unit tests for the cssutils-based CSS sanitizer.

    Notes
    -----
    These tests validate allow/deny behavior for properties, values, and at-rules.
    """

    def test_allows_basic_properties_and_custom_props(self) -> None:
        """Keep allowed properties and custom properties; drop nothing unsafe."""
        raw = """
        :root {
          color: #333;
          --my-accent: #0d6efd;
        }
        """
        out = sanitize_css(raw, allow_custom_properties=True)
        self.assertIn(":root{", out.replace(" ", ""))
        self.assertIn("color:#333", out.replace(" ", ""))
        self.assertIn("--my-accent:#0d6efd", out.replace(" ", ""))

    def test_strips_disallowed_properties(self) -> None:
        """Remove properties not present in the allowlist."""
        raw = """
        .x { zoom: 1; behavior: url(#foo); background-color: #fff; }
        """
        out = sanitize_css(raw)
        # background-color kept; zoom and behavior dropped
        self.assertIn(".x{", out.replace(" ", ""))
        self.assertIn("background-color:#fff", out.replace(" ", ""))
        self.assertNotIn("zoom:", out)
        self.assertNotIn("behavior:", out)

    def test_rejects_javascript_and_expression_values(self) -> None:
        """Reject suspicious values like javascript: and expression()."""
        bads = [
            ".x{background-image: url(javascript:alert(1))}",
            ".x{width: expression(alert(1))}",
            ".x{behavior: url(#foo)}",
        ]
        for css in bads:
            with self.assertRaises(ValueError):
                sanitize_css(css)

    def test_url_blocked_by_default_but_allowed_when_enabled(self) -> None:
        """Block url() by default; allow when allow_urls=True."""
        raw = ".x{background-image:url(/img/a.png)}"
        with self.assertRaises(ValueError):
            sanitize_css(raw, allow_urls=False)

        out = sanitize_css(raw, allow_urls=True)
        self.assertIn("background-image:url(/img/a.png)", out.replace(" ", ""))

    def test_keeps_media_and_supports_but_drops_import_and_keyframes(self) -> None:
        """
        Apply at-rule policy.

        Keep @media and @supports (sanitizing their inner rules); drop @import,
        @keyframes, @font-face, etc.
        """
        raw = """
        @import url('bad.css');
        @keyframes spin { from {transform:rotate(0)} to {transform:rotate(360deg)} }
        @font-face { font-family: X; src: url(a.woff2); }
        @media (min-width: 600px) { .a { color: #000; zoom: 1 } }
        @supports (display:grid) { .b { background-color: #fff; behavior:url(#x) } }
        """
        out = sanitize_css(raw)
        # Dropped at-rules
        self.assertNotIn("@import", out)
        self.assertNotIn("@keyframes", out)
        self.assertNotIn("@font-face", out)
        # Kept and sanitized @media/@supports inner rules
        squeezed = compact_css(out)
        self.assertIn("@media", squeezed)
        self.assertIn(".a{color:#000}", squeezed)
        self.assertIn("@supports", squeezed)
        self.assertIn(".b{background-color:#fff}", squeezed)
        self.assertNotIn("zoom:", out)
        self.assertNotIn("behavior:", out)

    def test_empty_or_all_removed_raises(self) -> None:
        """If everything is removed, the sanitizer should raise."""
        with self.assertRaises(ValueError):
            sanitize_css("@import url(a.css);")

        # but if empty input, just return empty
        out = sanitize_css("")
        self.assertEqual(out, "")

    def test_only_comments_removed_raises(self) -> None:
        """If only comments are present, they are removed and should raise."""
        with self.assertRaises(ValueError):
            sanitize_css("/* comment */ /* another comment */")
