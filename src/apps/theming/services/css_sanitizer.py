"""
CSS sanitizer service using cssutils.

This module provides a function to sanitize user-provided CSS by filtering
out potentially dangerous constructs, allowing only a safe subset of CSS rules
and properties. It leverages the `cssutils` library for parsing and serializing
CSS.

Features:
- Drops dangerous at-rules like `@import`, `@font-face`, and `@keyframes`.
- Allows only a predefined set of safe CSS properties (configurable).
- Optionally allows CSS custom properties (variables) and `url(...)` functions.
- Removes declarations with suspicious values (e.g., JavaScript URLs).
- Produces minified sanitized CSS output.

Usage:
```python
from apps.theming.services.css_sanitizer import sanitize_css

safe_css = sanitize_css(
    user_css,
    allowed_properties={"color", "background-color", "font-size"},
    allow_custom_properties=True,
    allow_urls=False,
)
```
"""

from __future__ import annotations

import re
from typing import Final

import cssutils  # type: ignore

# Reduce cssutils noise during parsing/serialization
cssutils.log.setLevel("FATAL")

MIN_OPACITY: Final[float] = 0.1
MAX_OPACITY: Final[float] = 1.0

# Reasonable default property allowlist (extend as needed)
DEFAULT_ALLOWED_PROPERTIES: Final[set[str]] = {
    # Layout
    "display",
    "position",
    "top",
    "right",
    "bottom",
    "left",
    "margin",
    "margin-top",
    "margin-right",
    "margin-bottom",
    "margin-left",
    "padding",
    "padding-top",
    "padding-right",
    "padding-bottom",
    "padding-left",
    # Size
    "width",
    "min-width",
    "max-width",
    "height",
    "min-height",
    "max-height",
    # Typography
    "font",
    "font-family",
    "font-size",
    "font-weight",
    "font-style",
    "line-height",
    "letter-spacing",
    "text-align",
    "text-decoration",
    "text-transform",
    "white-space",
    # Colors / backgrounds / borders
    "color",
    "background",
    "background-color",
    "background-image",
    "background-repeat",
    "background-size",
    "background-position",
    "border",
    "border-color",
    "border-style",
    "border-width",
    "border-radius",
    "outline",
    "outline-color",
    "outline-style",
    "outline-width",
    "box-shadow",
    "opacity",
    # Misc
    "transform",
    "transition",
    "visibility",
    "cursor",
    "z-index",
    "overflow",
    "overflow-x",
    "overflow-y",
    # Grid Layout
    "grid-template-columns",
    "grid-template-rows",
    "grid-template-areas",
    "grid-auto-columns",
    "grid-auto-rows",
    "grid-auto-flow",
    "grid-column",
    "grid-column-start",
    "grid-column-end",
    "grid-row",
    "grid-row-start",
    "grid-row-end",
    "gap",
    "row-gap",
    "column-gap",
    # Flexbox
    "flex",
    "flex-grow",
    "flex-shrink",
    "flex-basis",
    "justify-content",
    "align-items",
    "align-content",
    "align-self",
}

# Disallow any "url(...)" by default (safer). If you need it, toggle allow_urls=True.
_URL_FUNC_RE: Final[re.Pattern[str]] = re.compile(r"url\s*\(", re.IGNORECASE)
# Classic CSS injection primitives to reject in values
_FORBIDDEN_VALUE_SNIPPETS: Final[tuple[str, ...]] = (
    "expression",
    "javascript:",
    "vbscript:",
    "behavior:",
    "-ms-behavior:",
)

# At-rules policy:
#  - keep @media/@supports (sanitizing their inner rules)
#  - drop others (@import, @font-face, @keyframes, etc.)
_ALLOWED_AT_RULES: Final[set[str]] = {"media", "supports"}


def _is_custom_property(name: str) -> bool:
    """Return True if a property name is a CSS custom property (starts with --)."""
    return name.startswith("--")


def _value_is_safe(value: str, allow_urls: bool, prop_name: str | None = None) -> bool:
    """Return True if a CSS value looks safe (no JS, no URL)."""
    v = value.strip().lower()

    if not v:
        return False
    if prop_name == "opacity":
        try:
            f = float(v)
            return MIN_OPACITY <= f <= MAX_OPACITY
        except ValueError:
            return False

    if prop_name == "transform":
        return bool(
            re.fullmatch(
                r"(rotate|scale|skew)(x|y)?\([^()]+\)(\s+(rotate|scale|skew)(x|y)?\([^()]+\))*",
                v,
            )
        )

    # Basic forbidden substrings
    if any(snippet in v for snippet in _FORBIDDEN_VALUE_SNIPPETS):
        return False
    return not (not allow_urls and _URL_FUNC_RE.search(v))


def _preclean_text(src: str) -> str:
    """
    Make malformed CSS a bit more parsable.

    - Drop obviously empty declarations like `prop: ;`
    - Balance unmatched `{` by appending missing `}` at end
    """
    s = src or ""

    # Remove declarations with empty values (e.g., "zoom: ;")
    s = re.sub(r"(^|[;{])\s*([-\w]+)\s*:\s*;\s*", r"\1", s)

    # Balance braces: if there are more `{` than `}`, append the missing `}`.
    opens = s.count("{")
    closes = s.count("}")
    if opens > closes:
        s = s + ("}" * (opens - closes))

    return s


def _build_sanitized_style_rule(
    rule: cssutils.css.CSSStyleRule,
    *,
    props: set[str],
    allow_custom_properties: bool,
    allow_urls: bool,
) -> cssutils.css.CSSStyleRule | None:
    """Return a sanitized copy of a STYLE_RULE or None if no safe decl remains."""
    new_rule = cssutils.css.CSSStyleRule()
    new_rule.selectorText = rule.selectorText
    for decl in list(rule.style):
        name = decl.name.strip().lower()
        if not decl.value:
            continue
        if (
            (_is_custom_property(name) and allow_custom_properties) or (name in props)
        ) and _value_is_safe(decl.value, allow_urls, name):
            new_rule.style.setProperty(name, decl.value, decl.priority)
    return new_rule if new_rule.style.length else None


def _sanitize_media_rule(
    rule: cssutils.css.CSSMediaRule,
    *,
    sanitized: cssutils.css.CSSStyleSheet,
    props: set[str],
    allow_custom_properties: bool,
    allow_urls: bool,
) -> None:
    """Rebuild a @media rule with only safe nested STYLE_RULEs."""
    new_media = cssutils.css.CSSMediaRule()
    new_media.media.mediaText = rule.media.mediaText
    for nested in list(rule.cssRules):
        if nested.type == nested.STYLE_RULE:
            safe = _build_sanitized_style_rule(
                nested,
                props=props,
                allow_custom_properties=allow_custom_properties,
                allow_urls=allow_urls,
            )
            if safe is not None:
                new_media.cssRules.append(safe)
    if getattr(new_media, "cssRules", None) and len(new_media.cssRules) > 0:
        sanitized.add(new_media)


def _extract_supports_blocks(src: str) -> tuple[list[tuple[str, str]], str]:
    """
    Extract @supports blocks with balanced braces and return (blocks, remainder).

    Returns
    -------
    blocks : list of (condition_text, inner_css)
    remainder : str
        Original CSS with all @supports blocks removed.
    """
    s = src
    i = 0
    blocks: list[tuple[str, str]] = []
    out_chunks: list[str] = []

    while True:
        j = s.find("@supports", i)
        if j == -1:
            out_chunks.append(s[i:])
            break

        # keep text before @supports
        out_chunks.append(s[i:j])

        # scan condition up to first '{'
        k = j + len("@supports")
        n = len(s)
        # skip spaces
        while k < n and s[k].isspace():
            k += 1
        # condition starts at k, ends right before the '{' that opens the block
        cond_start = k
        # find first '{' after condition
        brace_pos = s.find("{", cond_start)
        if brace_pos == -1:
            # malformed, copy rest and stop
            out_chunks.append(s[j:])
            break
        condition = s[cond_start:brace_pos].strip()
        # now find the matching closing '}'
        depth = 0
        body_start = brace_pos + 1
        p = body_start
        while p < n:
            ch = s[p]
            if ch == "{":
                depth += 1
            elif ch == "}":
                if depth == 0:
                    # block ends at p
                    inner = s[body_start:p]
                    blocks.append((condition, inner))
                    i = p + 1
                    break
                else:
                    depth -= 1
            p += 1
        else:
            # no matching brace; copy rest and stop
            out_chunks.append(s[j:])
            break

    remainder = "".join(out_chunks)
    return blocks, remainder


def _rebuild_supports_blocks(
    sanitized: cssutils.css.CSSStyleSheet,
    supports_blocks: list[tuple[str, str]],
    *,
    props: set[str],
    allow_custom_properties: bool,
    allow_urls: bool,
) -> None:
    """Rebuild sanitized @supports blocks and append to the target stylesheet."""
    for condition, inner_body in supports_blocks:
        inner_sheet = cssutils.parseString(inner_body)
        inner_rules_chunks: list[str] = []
        for nested in list(getattr(inner_sheet, "cssRules", [])):
            if getattr(nested, "type", None) == getattr(nested, "STYLE_RULE", 1):
                safe = _build_sanitized_style_rule(
                    nested,
                    props=props,
                    allow_custom_properties=allow_custom_properties,
                    allow_urls=allow_urls,
                )
                if safe is not None:
                    chunk = (
                        safe.cssText.decode("utf-8")
                        if isinstance(safe.cssText, bytes)
                        else str(safe.cssText)
                    )
                    inner_rules_chunks.append(chunk)
        if inner_rules_chunks:
            rebuilt = f"@supports {condition}{{{''.join(inner_rules_chunks)}}}"
            tmp = cssutils.parseString(rebuilt)
            if getattr(tmp, "cssRules", None) and len(tmp.cssRules) > 0:
                sanitized.add(tmp.cssRules[0])


def _sanitize_remainder_css(
    sanitized: cssutils.css.CSSStyleSheet,
    remainder: str,
    *,
    props: set[str],
    allow_custom_properties: bool,
    allow_urls: bool,
) -> None:
    """Sanitize non-@supports CSS (keep STYLE and MEDIA, drop others)."""
    try:
        sheet = cssutils.parseString(remainder)
    except Exception as exc:  # pragma: no cover
        raise ValueError("Invalid CSS content.") from exc

    for rule in list(getattr(sheet, "cssRules", [])):
        try:
            rtype = getattr(rule, "type", None)
            if rtype == getattr(rule, "STYLE_RULE", 1):
                safe = _build_sanitized_style_rule(
                    rule,
                    props=props,
                    allow_custom_properties=allow_custom_properties,
                    allow_urls=allow_urls,
                )
                if safe is not None:
                    sanitized.add(safe)
            elif rtype == getattr(rule, "MEDIA_RULE", 4):
                _sanitize_media_rule(
                    rule,
                    sanitized=sanitized,
                    props=props,
                    allow_custom_properties=allow_custom_properties,
                    allow_urls=allow_urls,
                )
            # else: drop @import/@font-face/@keyframes/unknown
        except Exception:
            continue


def _serialize_stylesheet(sanitized: cssutils.css.CSSStyleSheet) -> str:
    """Serialize a stylesheet to minified CSS and ensure non-empty output."""
    out: str = (
        sanitized.cssText.decode("utf-8")
        if isinstance(sanitized.cssText, bytes)
        else str(sanitized.cssText)
    ).strip()
    if not out:
        raise ValueError("Unsafe or empty CSS after sanitization.")
    return out


def sanitize_css(
    raw_css: str,
    *,
    allowed_properties: set[str] | None = None,
    allow_custom_properties: bool = True,
    allow_urls: bool = False,
) -> str:
    """
    Sanitize CSS keeping @media/@supports and dropping dangerous content.

    Returns
    -------
    str
        Minified, sanitized CSS. Raises ValueError if everything is unsafe/empty.
    """
    # if empty raw_css, return early empty string
    if not raw_css.strip():
        return ""
    raw_css = _preclean_text(raw_css)
    props: set[str] = set(allowed_properties or DEFAULT_ALLOWED_PROPERTIES)

    # 1) Extract all @supports blocks (robust text-based extraction)
    supports_blocks, remainder = _extract_supports_blocks(raw_css or "")

    # 2) Prepare target stylesheet
    sanitized = cssutils.css.CSSStyleSheet()

    # 3) Rebuild @supports and append
    _rebuild_supports_blocks(
        sanitized,
        supports_blocks,
        props=props,
        allow_custom_properties=allow_custom_properties,
        allow_urls=allow_urls,
    )

    # 4) Sanitize the remainder (STYLE + MEDIA)
    _sanitize_remainder_css(
        sanitized,
        remainder,
        props=props,
        allow_custom_properties=allow_custom_properties,
        allow_urls=allow_urls,
    )

    # 5) Serialize
    return _serialize_stylesheet(sanitized)
