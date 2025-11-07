"""Advanced tests for cssutils-based CSS sanitizer."""

from __future__ import annotations

from django.test import TestCase

from apps.theming.services.css_sanitizer import sanitize_css

from .common import compact_css


class CssSanitizerAdvancedTests(TestCase):
    """
    Advanced tests for cssutils-based sanitizer.

    - Grid properties allowlist
    - transform (rotate|scale|skew only)
    - opacity in [0.1, 1]
    - precleaning malformed CSS (unbalanced braces, empty values)
    - @media / @supports kept and sanitized
    """

    # ---------- Grid / allowlist --------------------------------------------

    def test_grid_template_columns_is_kept(self) -> None:
        """Grid-template-columns should be preserved when value is simple."""
        raw = """
        @media (min-width: 800px) {
          .container { display: grid; grid-template-columns: 1fr 1fr; zoom: 1; }
        }
        """
        out = sanitize_css(raw)
        s = compact_css(out)
        self.assertIn("@media", s)
        self.assertIn(".container{display:grid;grid-template-columns:1fr1fr}", s)
        self.assertNotIn("zoom:", s)

    # ---------- transform rules ---------------------------------------------

    def test_transform_rotate_scale_skew_allowed(self) -> None:
        """Allow rotate/scale/skew transforms and simple chaining."""
        raw = ".box { transform: rotate(45deg) scale(1.2) skewX(10deg); }"
        out = sanitize_css(raw)
        s = compact_css(out)
        self.assertIn(
            ".box{transform:rotate(45deg)scale(1.2)skewx(10deg)}".lower(), s.lower()
        )

    def test_transform_translate_and_matrix_rejected(self) -> None:
        """Reject translate/matrix/perspective/3D variants."""
        raws = [
            ".bad { transform: translateX(10px); }",
            ".bad { transform: matrix(1,0,0,1,0,0); }",
            ".bad { transform: perspective(500px); }",
            ".bad { transform: rotate3d(1,0,0,45deg); }",
        ]
        for css in raws:
            with self.assertRaises(ValueError):
                out = sanitize_css(css)
                s = compact_css(out)
                # Rule may remain but without transform, or rule dropped if empty
                self.assertNotIn(
                    "transform:", s, msg=f"Unexpected transform kept for: {css!r}"
                )

    def test_transform_invalid_syntax_rejected(self) -> None:
        """Reject invalid transform syntax."""
        raw = ".x { transform: rotate(); }"
        with self.assertRaises(ValueError):
            out = sanitize_css(raw)
            self.assertNotIn("transform:", out)

    # ---------- opacity rules ------------------------------------------------

    def test_opacity_in_range_kept(self) -> None:
        """Opacity in [0.1, 1] should be kept."""
        raw = ".a { opacity: 0.8; } .b { opacity: 1; } .c { opacity: 0.1; }"
        out = sanitize_css(raw)
        s = compact_css(out)
        self.assertIn(".a{opacity:0.8}", s)
        self.assertIn(".b{opacity:1}", s)
        self.assertIn(".c{opacity:0.1}", s)

    def test_opacity_out_of_range_rejected(self) -> None:
        """Opacity < 0.1 or > 1 should be removed."""
        raws = [
            ".x { opacity: 0; }",
            ".x { opacity: -0.2; }",
            ".x { opacity: 1.2; }",
            ".x { opacity: foo; }",
        ]
        for css in raws:
            with self.assertRaises(ValueError):
                out = sanitize_css(css)
                self.assertNotIn("opacity:", out)

    # ---------- malformed CSS precleaning -----------------------------------

    def test_preclean_balances_missing_brace(self) -> None:
        """Missing closing brace should be balanced to keep valid decls."""
        raw = ".x { color: #000"  # no closing }
        out = sanitize_css(raw)
        s = compact_css(out)
        self.assertIn(".x{color:#000}", s)

    def test_preclean_drops_empty_declaration(self) -> None:
        """Drop declarations with empty values like 'zoom: ;'."""
        raw = ".y { background-color: #fff; zoom: ; }"
        out = sanitize_css(raw)
        s = compact_css(out)
        self.assertIn(".y{background-color:#fff}", s)
        self.assertNotIn("zoom:", s)

    # ---------- @media / @supports complex snippet --------------------------

    def test_complex_css(self) -> None:
        """Test a complex CSS snippet with various constructs."""
        raw = """
        /* A comment */
        @media (min-width: 800px) {
            .container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                zoom: 1; /* disallowed */
            }
        }
        @supports (display: flex) {
            .flex-item {
                background-color: #eee;
                behavior: url(#x); /* disallowed */
            }
        }
        .normal {
            color: #111;
            width: expression(alert(1)); /* disallowed */
        }
        """
        out = sanitize_css(raw)
        squeezed = compact_css(out)

        # Kept and sanitized @media/@supports inner rules
        self.assertIn("@media", squeezed)
        self.assertIn(".container{display:grid;grid-template-columns:1fr1fr}", squeezed)
        self.assertIn("@supports", squeezed)
        self.assertIn(".flex-item{background-color:#eee}", squeezed)
        self.assertIn(".normal{color:#111}", squeezed)

        # Disallowed properties/values are removed
        self.assertNotIn("zoom:", out)
        self.assertNotIn("behavior:", out)
        self.assertNotIn("expression(", out)

    # ---------- url() policy -------------------------------------------------

    def test_url_blocked_by_default(self) -> None:
        """Url() should be rejected by default policy."""
        with self.assertRaises(ValueError):
            sanitize_css(".x{background-image:url(/img/a.png)}")
