#!/usr/bin/env python3
"""
Bootstrap 4 → 5 migrator (safe for Django templates).

This script:
- Scans "src/apps/**" for files matching "*_bs5.html" starting from the project root
  which is taken as the directory containing this script file.
- Applies straightforward and safe renames inside HTML class attribute values
  and Bootstrap JS data attribute names (data-* → data-bs-*).
- Emits a YAML report (migration_report.yml) listing warnings for manual follow-up
  with file path, line number, token, and an excerpt.
- Writes in-place modifications and creates .bak backups next to each changed file.

The rules implemented are derived from the official Bootstrap v4 → v5 migration guide:
https://getbootstrap.com/docs/5.3/migration/

Notes
-----
- The script is careful to only touch class="" values and known data-* attributes.
- Complex structural refactors (forms overhaul, input group append/prepend, etc.)
  are not auto-fixed; they are detected and reported as warnings.
- The script is friendly to Django templates: it does not alter template tags and
  only edits content within attribute values.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from re import Match, Pattern

# --------------------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------------------


def project_root() -> Path:
    """
    Return the project root as the directory containing this script file.

    This avoids relying on the current working directory, which varies depending on how
    the script is invoked and led to "Path.relative_to" errors for users running the
    script from outside the repository root.
    """
    return Path(__file__).resolve().parent


REPO_ROOT: Path = project_root()
ROOT_SEARCH_DIR: Path = REPO_ROOT / "src" / "apps"
FILE_GLOB: str = "**/*_bs5.html"
REPORT_PATH: Path = REPO_ROOT / "migration_report.yml"

# Regex to match class attributes; keep quote capture to preserve single/double quotes
CLASS_ATTR_RE: Pattern[str] = re.compile(
    r"""(?P<attr>class\s*=\s*)(?P<quote>["'])(?P<val>.*?)(?P=quote)""",
    re.DOTALL,
)

# Pairs of regex -> replacement for data-* attribute names (not values)
DATA_ATTR_REPLACERS: list[tuple[Pattern[str], str]] = [
    (re.compile(r"\bdata-toggle\b"), "data-bs-toggle"),
    (re.compile(r"\bdata-target\b"), "data-bs-target"),
    (re.compile(r"\bdata-dismiss\b"), "data-bs-dismiss"),
    (re.compile(r"\bdata-spy\b"), "data-bs-spy"),
    (re.compile(r"\bdata-offset\b"), "data-bs-offset"),
    (re.compile(r"\bdata-ride\b"), "data-bs-ride"),
    (re.compile(r"\bdata-parent\b"), "data-bs-parent"),
]

# Exact token-to-token class renames
TOKEN_RENAMES: dict[str, str] = {
    "no-gutters": "g-0",
    "text-monospace": "font-monospace",
    "font-italic": "fst-italic",
    "sr-only": "visually-hidden",
    "sr-only-focusable": "visually-hidden-focusable",
    "text-hide": "visually-hidden",
}

# Regex-based class renames that must preserve optional breakpoints or suffixes
RegexRepl = tuple[Pattern[str], Callable[[Match[str]], str] | str]

REGEX_CLASS_RULES: list[RegexRepl] = [
    # float-left/right -> float-start/end (with optional breakpoint like md-)
    (
        re.compile(r"\bfloat-(?:(xs|sm|md|lg|xl|xxl)-)?(left|right)\b"),
        lambda m: f"float-{(m.group(1) or '')}{'start' if m.group(2) == 'left' else 'end'}",
    ),
    # text-left/right -> text-(bp-)start/end
    (
        re.compile(r"\btext-(?:(xs|sm|md|lg|xl|xxl)-)?(left|right)\b"),
        lambda m: f"text-{(m.group(1) or '')}{'start' if m.group(2) == 'left' else 'end'}",
    ),
    # spacing margin: ml-/mr- -> ms-/me-
    (re.compile(r"\bml-"), "ms-"),
    (re.compile(r"\bmr-"), "me-"),
    # spacing padding: pl-/pr- -> ps-/pe-
    (re.compile(r"\bpl-"), "ps-"),
    (re.compile(r"\bpr-"), "pe-"),
    # borders left/right -> start/end (with optional -0)
    (
        re.compile(r"\bborder-(left|right)-0\b"),
        lambda m: f"border-{'start' if m.group(1) == 'left' else 'end'}-0",
    ),
    (
        re.compile(r"\bborder-(left|right)\b"),
        lambda m: f"border-{'start' if m.group(1) == 'left' else 'end'}",
    ),
    # rounded left/right -> start/end
    (
        re.compile(r"\brounded-(left|right)\b"),
        lambda m: f"rounded-{'start' if m.group(1) == 'left' else 'end'}",
    ),
    # font-weight-* -> fw-*
    (re.compile(r"\bfont-weight-"), "fw-"),
    # embed-responsive* -> ratio*
    (re.compile(r"\bembed-responsive-16by9\b"), "ratio-16x9"),
    (re.compile(r"\bembed-responsive-4by3\b"), "ratio-4x3"),
    (re.compile(r"\bembed-responsive-1by1\b"), "ratio-1x1"),
    (re.compile(r"\bembed-responsive\b"), "ratio"),
    (re.compile(r"\bembed-responsive-item\b"), ""),
]

BADGE_VARIANTS: tuple[str, ...] = (
    "primary",
    "secondary",
    "success",
    "danger",
    "warning",
    "info",
    "light",
    "dark",
)
BADGE_RE: Pattern[str] = re.compile(rf"\bbadge-({'|'.join(BADGE_VARIANTS)})\b")
BADGE_PILL_RE: Pattern[str] = re.compile(r"\bbadge-pill\b")

# Warning patterns: these are not auto-fixed; we surface them in the report
WARN_PATTERNS: list[tuple[Pattern[str], str]] = [
    (
        re.compile(r"\bform-group\b"),
        "Form layout changed: replace .form-group with utilities (often .mb-3).",
    ),
    (re.compile(r"\bform-row\b"), "Form layout removed: use .row + grid utilities."),
    (re.compile(r"\bform-inline\b"), "Form inline removed: use flex utilities."),
    (
        re.compile(r"\bcustom-(control|select|file|range)\b"),
        "Custom form controls removed: use .form-check, .form-select, .form-control, .form-range.",
    ),
    (
        re.compile(r"\binput-group-(append|prepend)\b"),
        "Input group append/prepend removed: place buttons and .input-group-text directly.",
    ),
    (
        re.compile(r"\bjumbotron\b"),
        "Jumbotron removed: recreate with utilities/helpers.",
    ),
    (
        re.compile(r"\bmedia\b"),
        "Media component removed: recreate with flex utilities.",
    ),
    (
        re.compile(r"\bcard-(deck|columns)\b"),
        "Card deck/columns removed: use grid + .row-cols-*.",
    ),
    (
        re.compile(r"\bbtn-block\b"),
        "Button block removed: use .d-grid wrapper or .w-100.",
    ),
    (
        re.compile(r"\bnavbar\b"),
        "Navbar now expects an inner .container in many examples: review structure.",
    ),
    (
        re.compile(r"\bthead-(light|dark)\b"),
        "thead-light/dark removed: use .table-* variants on thead/rows/cells.",
    ),
    (re.compile(r"\btext-justify\b"), "text-justify removed."),
    (re.compile(r"\bpre-scrollable\b"), "pre-scrollable removed."),
    (
        re.compile(r"\border-(?:[6-9]|[1-9]\d+)\b"),
        "Some .order-* values greater than 5 were removed or changed.",
    ),
    (
        re.compile(r"\bclose\b"),
        "Close button changed to .btn-close and markup adjusted.",
    ),
]

# --------------------------------------------------------------------------------------
# Data structures
# --------------------------------------------------------------------------------------


@dataclass
class WarningEntry:
    """A single warning instance discovered in a specific file and line."""

    line: int
    token: str
    message: str
    excerpt: str


@dataclass
class FileReport:
    """Per-file report including change status and warnings."""

    path: Path
    changed: bool
    warnings: list[WarningEntry] = field(default_factory=list)


# --------------------------------------------------------------------------------------
# Transform functions
# --------------------------------------------------------------------------------------


def tidy_whitespace(s: str) -> str:
    """Collapse duplicate spaces and strip surrounding whitespace."""
    return re.sub(r"\s{2,}", " ", s).strip()


def replace_classes(value: str) -> str:
    """
    Apply token and regex-based class renames to a value from class="...".

    Only class tokens are altered; surrounding whitespace and quote style are preserved.
    """
    out: str = value

    # Token-to-token renames
    for old, new in TOKEN_RENAMES.items():
        out = re.sub(rf"\b{re.escape(old)}\b", new, out)

    # Regex rules
    for rx, repl in REGEX_CLASS_RULES:
        out = rx.sub(repl, out)

    # Badges
    out = BADGE_PILL_RE.sub("rounded-pill", out)
    out = BADGE_RE.sub(lambda m: f"bg-{m.group(1)}", out)

    return tidy_whitespace(out)


def transform_class_attributes(line: str) -> str:
    """Apply class value transformations inside a single line of HTML."""

    def _sub(m: Match[str]) -> str:
        before, quote, val = m.group("attr"), m.group("quote"), m.group("val")
        new_val = replace_classes(val)
        return f"{before}{quote}{new_val}{quote}"

    return CLASS_ATTR_RE.sub(_sub, line)


def transform_data_attributes(line: str) -> str:
    """Rename Bootstrap JS data-* attributes to data-bs-* on a single line."""
    out: str = line
    for rx, repl in DATA_ATTR_REPLACERS:
        out = rx.sub(repl, out)
    return out


def find_warnings(line: str) -> list[tuple[str, str]]:
    """Return a list of (token, message) for each warning pattern found in the line."""
    found: list[tuple[str, str]] = []
    for rx, msg in WARN_PATTERNS:
        for hit in rx.finditer(line):
            found.append((hit.group(0), msg))
    return found


def process_file(path: Path) -> tuple[bool, list[WarningEntry]]:
    """
    Process a single file: perform safe replacements and collect warnings.

    Returns
    -------
        (changed, warnings)
        - changed: True if the file content was modified and saved
        - warnings: a list of WarningEntry discovered in the file
    """
    original: str = path.read_text(encoding="utf-8")
    new_lines: list[str] = []
    warnings: list[WarningEntry] = []
    changed: bool = False

    for lineno, line in enumerate(original.splitlines(keepends=False), start=1):
        transformed = transform_class_attributes(transform_data_attributes(line))
        if transformed != line:
            changed = True
        MAX_WARNING_SNIPPET_LENGTH = 160
        # Collect warnings (based on original line for better highlighting)
        for token, msg in find_warnings(line):
            snippet = line.strip()
            if len(snippet) > MAX_WARNING_SNIPPET_LENGTH:
                snippet = snippet[: MAX_WARNING_SNIPPET_LENGTH - 3] + "..."
            warnings.append(
                WarningEntry(line=lineno, token=token, message=msg, excerpt=snippet)
            )

        new_lines.append(transformed)

    if changed:
        backup = path.with_suffix(path.suffix + ".bak")
        if not backup.exists():
            backup.write_text(original, encoding="utf-8")
        path.write_text(
            "\n".join(new_lines) + ("\n" if original.endswith("\n") else ""),
            encoding="utf-8",
        )

    return changed, warnings


# --------------------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------------------


def count_auto_fixes(before: str, after: str) -> dict[str, int]:
    """
    Heuristically count the number of applied fixes between two full texts.

    This is approximate but good enough for a useful summary.
    """
    counters: dict[str, int] = {
        "float_left_right_to_start_end": 0,
        "text_left_right_to_start_end": 0,
        "ml_mr_to_ms_me": 0,
        "pl_pr_to_ps_pe": 0,
        "border_lr_to_start_end": 0,
        "rounded_lr_to_start_end": 0,
        "badge_variants_to_bg": 0,
        "badge_pill_to_rounded_pill": 0,
        "no_gutters_to_g0": 0,
        "font_weight_to_fw": 0,
        "font_italic_to_fst": 0,
        "text_monospace_to_font_monospace": 0,
        "embed_responsive_to_ratio": 0,
        "sr_only_to_visually_hidden": 0,
        "data_attributes_to_data_bs": 0,
    }

    patterns: list[tuple[Pattern[str], str]] = [
        (
            re.compile(r"\bfloat-(?:xs|sm|md|lg|xl|xxl-)?(?:left|right)\b"),
            "float_left_right_to_start_end",
        ),
        (
            re.compile(r"\btext-(?:xs|sm|md|lg|xl|xxl-)?(?:left|right)\b"),
            "text_left_right_to_start_end",
        ),
        (re.compile(r"\bml-|\bmr-"), "ml_mr_to_ms_me"),
        (re.compile(r"\bpl-|\bpr-"), "pl_pr_to_ps_pe"),
        (re.compile(r"\bborder-(?:left|right)\b"), "border_lr_to_start_end"),
        (re.compile(r"\brounded-(?:left|right)\b"), "rounded_lr_to_start_end"),
        (
            re.compile(r"\bbadge-(?:" + "|".join(BADGE_VARIANTS) + r")\b"),
            "badge_variants_to_bg",
        ),
        (re.compile(r"\bbadge-pill\b"), "badge_pill_to_rounded_pill"),
        (re.compile(r"\bno-gutters\b"), "no_gutters_to_g0"),
        (re.compile(r"\bfont-weight-"), "font_weight_to_fw"),
        (re.compile(r"\bfont-italic\b"), "font_italic_to_fst"),
        (re.compile(r"\btext-monospace\b"), "text_monospace_to_font_monospace"),
        (
            re.compile(
                r"\bembed-responsive\b|\bembed-responsive-\w+\b|\bembed-responsive-item\b"
            ),
            "embed_responsive_to_ratio",
        ),
        (
            re.compile(r"\bsr-only\b|\bsr-only-focusable\b|\btext-hide\b"),
            "sr_only_to_visually_hidden",
        ),
        (
            re.compile(r"\bdata-(toggle|target|dismiss|spy|offset|ride|parent)\b"),
            "data_attributes_to_data_bs",
        ),
    ]

    for rx, key in patterns:
        before_hits = len(rx.findall(before))
        after_hits = len(rx.findall(after))
        if before_hits and before_hits != after_hits:
            delta = before_hits - after_hits
            counters[key] += delta if delta != 0 else before_hits

    return counters


def write_yaml_report(files: list[FileReport], fixed_totals: dict[str, int]) -> None:
    """Serialize the YAML report to REPORT_PATH without external dependencies."""
    ts = datetime.now().isoformat(timespec="seconds")
    lines: list[str] = []
    lines.append(f'datetime: "{ts}"')
    lines.append("summary:")
    lines.append(f"  files_scanned: {len(files)}")
    lines.append(f"  files_changed: {sum(1 for f in files if f.changed)}")
    lines.append("  auto_fixes:")
    for k in sorted(fixed_totals):
        lines.append(f"    {k}: {fixed_totals[k]}")
    lines.append("warnings:")
    for f in files:
        if not f.warnings:
            continue
        # Make path relative to repo root for stable output
        try:
            rel = f.path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
        except ValueError:
            # Fallback to absolute path if outside of repo root (should not happen)
            rel = f.path.resolve().as_posix()
        lines.append(f"  - file: {rel}")
        for w in f.warnings:
            # Escape double quotes for YAML strings
            token = w.token.replace('"', "'")
            message = w.message.replace('"', "'")
            excerpt = w.excerpt.replace('"', "'")
            lines.append(f"    - line: {w.line}")
            lines.append(f'      token: "{token}"')
            lines.append(f'      message: "{message}"')
            lines.append(f'      excerpt: "{excerpt}"')
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------


def main() -> None:
    """Entry-point: scan files, apply transformations, and produce the YAML report."""
    if not ROOT_SEARCH_DIR.exists():
        print(
            f'ERROR: Not found: "{ROOT_SEARCH_DIR}". Expected "src/apps" under {REPO_ROOT}.',
            file=sys.stderr,
        )
        sys.exit(1)

    files: list[Path] = sorted(ROOT_SEARCH_DIR.glob(FILE_GLOB))
    if not files:
        print(
            f'ERROR: No files matching "{FILE_GLOB}" under "{ROOT_SEARCH_DIR}".',
            file=sys.stderr,
        )
        sys.exit(1)

    file_reports: list[FileReport] = []
    totals: dict[str, int] | None = None

    for path in files:
        # Read before, process, read after to estimate applied fixes
        before = path.read_text(encoding="utf-8")
        changed, warnings = process_file(path)
        after = path.read_text(encoding="utf-8")

        fixed = count_auto_fixes(before, after)
        if totals is None:
            totals = dict.fromkeys(fixed, 0)
        for k, v in fixed.items():
            totals[k] += v

        file_reports.append(FileReport(path=path, changed=changed, warnings=warnings))

    write_yaml_report(file_reports, totals or {})

    changed_count = sum(1 for f in file_reports if f.changed)
    print(f"OK • Scanned: {len(file_reports)} • Changed: {changed_count}")
    print(f"Report: {REPORT_PATH.as_posix()}")


if __name__ == "__main__":
    main()
