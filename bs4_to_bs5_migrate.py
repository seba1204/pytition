#!/usr/bin/env python3

"""
bs4_to_bs5_migrate.py
---------------------

Semi-automatic migration tool to help convert Bootstrap 4 markup in Django (or plain HTML)
templates to Bootstrap 5. The tool performs safe, idempotent rewrites and flags
ambiguous cases for manual review.

Key features:
- Walk a templates directory and process HTML/HTM files.
- Save a .bak backup before writing (unless --dry-run).
- Apply attribute/data-attribute transformations (data-* -> data-bs-*).
- Rewrite class tokens where Bootstrap 4 changed/removed names.
- Remove input-group append/prepend wrappers (keeping inner content).
- Best-effort replace legacy .close buttons by .btn-close (with warnings).
- Detect deprecated/removed components and emit warnings.
- Optional JSON report summarizing changes and warnings.
- Strong typing for MyPy; extensive docstrings and English comments.
- Support for a *filename* regex filter to restrict which files are processed
  (e.g., only files ending in "_bs5.html").

Usage examples:
  # Dry run only on files matching *_bs5.html under ./templates
  python bs4_to_bs5_migrate.py ./templates --filename-regex ".*_bs5\.html$" --dry-run --report report.json

  # Write changes for .html and .htm files, any filename, with a report
  python bs4_to_bs5_migrate.py ./templates --ext .html --ext .htm --report report.json

Notes
-----
- The script is idempotent. Running it multiple times will not duplicate changes.
- You should still review warnings and test interactive components (dropdowns, modals, tooltips),
  because Bootstrap 5 removed jQuery and changed some behaviors.
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from re import Pattern

# ----------------------------- Data classes ----------------------------------


@dataclass
class FileStats:
    """Holds per-file processing statistics."""

    file: str
    attr_replacements: int = 0
    class_attr_rewrites: int = 0
    input_group_wrapper_removed: int = 0
    close_button_rewrites: int = 0
    embed_wrapper_flags: int = 0
    warnings_count: int = 0
    warnings: list[str] | None = None
    changed: bool = False
    lines_changed: int = 0


@dataclass
class Summary:
    """Aggregated summary for all processed files."""

    root: str
    files_scanned: int
    files_matched: int
    files_changed: int
    approx_lines_changed: int
    total_warnings: int
    details: list[FileStats]


# --------------------------- Regex / Rewrite Rules ---------------------------

# Attribute replacements: data-* -> data-bs-*
ATTR_RULES: list[tuple[Pattern[str], str]] = [
    # Convert only if not already data-bs-*
    (re.compile(r"(?<!data-bs-)data-toggle(?=\s*=)", re.IGNORECASE), "data-bs-toggle"),
    (re.compile(r"(?<!data-bs-)data-target(?=\s*=)", re.IGNORECASE), "data-bs-target"),
    (
        re.compile(r"(?<!data-bs-)data-dismiss(?=\s*=)", re.IGNORECASE),
        "data-bs-dismiss",
    ),
    (re.compile(r"(?<!data-bs-)data-offset(?=\s*=)", re.IGNORECASE), "data-bs-offset"),
]

# Class token simple mappings (token -> token(s))
CLASS_TOKEN_SIMPLE: dict[str, str] = {
    # Utilities renames
    "btn-block": "w-100",
    "sr-only": "visually-hidden",
    "text-left": "text-start",
    "text-right": "text-end",
    "dropdown-menu-right": "dropdown-menu-end",
    "dropdown-menu-left": "dropdown-menu-start",
    "no-gutters": "g-0",
    "font-weight-bold": "fw-bold",
    "font-weight-bolder": "fw-bolder",
    "font-weight-normal": "fw-normal",
    "font-weight-light": "fw-light",
    "text-monospace": "font-monospace",
    "embed-responsive": "ratio",  # core wrapper (structure may still need manual review)
    "embed-responsive-21by9": "ratio-21x9",
    "embed-responsive-16by9": "ratio-16x9",
    "embed-responsive-4by3": "ratio-4x3",
    "embed-responsive-1by1": "ratio-1x1",
    "thead-light": "table-light",
    "thead-dark": "table-dark",
    "badge-pill": "rounded-pill",
    "float-left": "float-start",
    "float-right": "float-end",
    # Forms/Layout
    "form-group": "mb-3",
    "form-row": "row",
}

# Badge contextual colors in BS5 use "bg-*", not "badge-*".
BADGE_CONTEXTS: list[str] = [
    "primary",
    "secondary",
    "success",
    "danger",
    "warning",
    "info",
    "light",
    "dark",
]

# Tokens that indicate deprecated/removed patterns requiring manual refactor.
DEPRECATED_CLASS_TOKENS: set[str] = {
    "custom-control",
    "custom-checkbox",
    "custom-radio",
    "custom-switch",
    "custom-select",
    "custom-range",
    "custom-file",
    "custom-file-input",
    "custom-file-label",
    "media",
    "media-body",
    "jumbotron",
    "card-deck",
    "input-group-append",
    "input-group-prepend",
    "close",
}

# Markup-level regexes for specific transformations or flags.
RE_INPUT_GROUP_WRAPPER: Pattern[str] = re.compile(
    r'<\s*div\s+class="([^"]*\binput-group-(?:append|prepend)\b[^"]*)"\s*>\s*'
    r"(.*?)\s*</\s*div\s*>",
    re.IGNORECASE | re.DOTALL,
)

RE_CLOSE_BUTTON: Pattern[str] = re.compile(
    r'(<\s*button[^>]*\bclass="[^"]*\bclose\b[^"]*"[^>]*>)(.*?)(</\s*button\s*>)',
    re.IGNORECASE | re.DOTALL,
)

RE_EMBED_WRAPPER: Pattern[str] = re.compile(
    r'(<\s*div[^>]*\bclass="[^"]*\bembed-responsive\b[^"]*"[^>]*>)', re.IGNORECASE
)

# Warning-only patterns for manual review.
WARNING_PATTERNS: dict[Pattern[str], str] = {
    re.compile(
        r"\bcustom-(?:control|checkbox|radio|switch|select|range|file)\b", re.IGNORECASE
    ): "Custom forms (BS4) detected: use .form-check / .form-select / .form-control in BS5.",
    re.compile(
        r"\bjumbotron\b", re.IGNORECASE
    ): "Jumbotron detected: recreate with utilities (.p-5 .mb-4 .bg-body-tertiary .rounded-3).",
    re.compile(
        r"\bmedia\b", re.IGNORECASE
    ): "Media object detected: replace with flex utilities (.d-flex, .me-3, etc.).",
    re.compile(
        r"\bcard-deck\b", re.IGNORECASE
    ): "card-deck detected: use the grid (.row .col or .row.row-cols-*).",
}


# ----------------------------- Helper Functions ------------------------------


def tokenize_classes(class_value: str) -> list[str]:
    """Split a class attribute string into individual tokens."""
    return [t for t in class_value.strip().split() if t]


def detokenize_classes(tokens: Sequence[str]) -> str:
    """Join class tokens while preserving original order and removing duplicates."""
    seen: set[str] = set()
    out: list[str] = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return " ".join(out)


def transform_class_attr(class_value: str, warnings: list[str]) -> str:
    """
    Transform a full class attribute string by rewriting/remapping specific tokens.

    This function handles token-by-token replacements (e.g., 'btn-block' -> 'w-100'),
    badge contextual changes (e.g., 'badge-secondary' -> 'badge bg-secondary'), and
    collects warnings for deprecated tokens that require manual refactor.
    """
    tokens: list[str] = tokenize_classes(class_value)
    new_tokens: list[str] = []

    for tok in tokens:
        low = tok.lower()

        # Convert legacy 'badge-<context>' to 'badge bg-<context>'
        if low.startswith("badge-"):
            parts = low.split("-", 1)
            if len(parts) == 2 and parts[1] in BADGE_CONTEXTS:
                # Ensure 'badge' class exists and replace contextual class by bg-*
                if "badge" not in new_tokens and "badge" not in tokens:
                    new_tokens.append("badge")
                new_tokens.append(f"bg-{parts[1]}")
                continue

        # Map simple token renames (may expand into multiple tokens).
        if low in CLASS_TOKEN_SIMPLE:
            mapped = CLASS_TOKEN_SIMPLE[low]
            new_tokens.extend(mapped.split())
            continue

        # Flag deprecated tokens but keep them to avoid breaking markup.
        if low in DEPRECATED_CLASS_TOKENS:
            warnings.append(
                f"Deprecated/removed class detected: '{tok}' (requires manual rewrite for BS5)."
            )
            new_tokens.append(tok)
            continue

        # Default: keep token
        new_tokens.append(tok)

    return detokenize_classes(new_tokens)


def rewrite_class_attributes(html: str, warnings: list[str]) -> tuple[str, int]:
    """
    Rewrite every class="..." attribute in an HTML document.

    Returns the new HTML and a count of modified class attributes.
    """
    count = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal count
        original = m.group(0)
        classes = m.group(1)
        updated = transform_class_attr(classes, warnings)
        if updated != classes:
            count += 1
        return original.replace(classes, updated, 1)

    pattern: Pattern[str] = re.compile(r'class="([^"]+)"', re.IGNORECASE)
    new_html = pattern.sub(repl, html)
    return new_html, count


def apply_attr_rules(text: str) -> tuple[str, int]:
    """Apply attribute-level regex rewrites and return."""
    count = 0
    for rx, repl in ATTR_RULES:
        text, n = rx.subn(repl, text)
        count += n
    return text, count


def remove_input_group_wrappers(text: str) -> tuple[str, int]:
    """
    Remove <div class="input-group-append|prepend"> wrappers, preserving the inner
    content.

    Returns (new_text, number_removed).
    """

    def repl(m: re.Match[str]) -> str:
        # Keep only inner content (group 2), drop the wrapper
        return m.group(2)

    new_text, n = RE_INPUT_GROUP_WRAPPER.subn(repl, text)
    return new_text, n


def best_effort_close_button(text: str, warnings: list[str]) -> tuple[str, int]:
    """
    Attempt to convert legacy .close buttons to BS5 .btn-close.

    If the inner content includes '×' or '&times;', warn that BS5's .btn-close must be
    empty (no inner content). We transform the class in the opening tag and keep/clear
    content depending on the situation to avoid breaking markup.
    """

    def repl(m: re.Match[str]) -> str:
        open_tag, inner, close_tag = m.groups()
        contains_times = ("&times;" in inner) or ("×" in inner)
        if contains_times:
            # get line number for warning (approximate)
            line_no = text.count("\n", 0, m.start()) + 1
            warnings.append(
                f"Line {line_no}: Close button with inner '×' or '&times;' detected. "
                "Replace by "
                '<button type="button" class="btn-close" data-bs-dismiss="..." aria-label="Close"></button> '
                "without inner content."
            )
            # Replace class to btn-close and drop inner content to mimic BS5
            new_open = re.sub(r"\bclose\b", "btn-close", open_tag)
            return new_open + "" + close_tag
        else:
            # Replace class only; keep inner content (best effort)
            new_open = re.sub(r"\bclose\b", "btn-close", open_tag)
            return new_open + inner + close_tag

    new_text, n = RE_CLOSE_BUTTON.subn(repl, text)
    return new_text, n


def mark_embed_wrappers(text: str, warnings: list[str]) -> tuple[str, int]:
    """
    Mark legacy '.embed-responsive' wrappers for manual review.

    BS5 uses '.ratio' and may require markup restructuring.
    """
    matches = list(RE_EMBED_WRAPPER.finditer(text))
    for m in matches:
        # get line number for warning (approximate)
        line_no = text.count("\n", 0, m.start()) + 1
        warnings.append(
            f"Line {line_no}: 'embed-responsive' wrapper detected. "
            "Convert structure to .ratio and appropriate ratio class (.ratio-16x9...)."
        )
    return text, len(matches)


def scan_warnings(text: str, warnings: list[str]) -> int:
    """
    Run regex checks for patterns that require manual refactor.

    Each match appends a warning message with its line number. Returns the total number
    of matches.
    """
    total = 0
    for rx, message in WARNING_PATTERNS.items():
        for m in rx.finditer(text):
            total += 1
            # Compute approximate line number
            line_no = text.count("\n", 0, m.start()) + 1
            warnings.append(f"Line {line_no}: {message}")
    return total


# ------------------------------ Core Pipeline --------------------------------


def process_file(path: Path, dry_run: bool) -> FileStats:
    """
    Process a single HTML file: apply transformations, collect stats and warnings,
    and write the result (with .bak backup) unless --dry-run is set.
    """
    original = path.read_text(encoding="utf-8")
    text = original
    warnings: list[str] = []

    # 1) data-* -> data-bs-*
    text, n_attr = apply_attr_rules(text)

    # 2) class="..." token remapping
    text, n_class = rewrite_class_attributes(text, warnings)

    # 3) Remove input-group wrappers
    text, n_input_group = remove_input_group_wrappers(text)

    # 4) Replace legacy .close with .btn-close (best effort)
    text, n_close = best_effort_close_button(text, warnings)

    # 5) Flag embed-responsive wrappers
    text, n_embed = mark_embed_wrappers(text, warnings)

    # 6) Scan for additional warnings
    n_warn_matches = scan_warnings(text, warnings)

    # Determine changes and compute rough "lines changed"
    changed = text != original
    lines_changed = 0
    if changed:
        orig_lines = original.splitlines()
        new_lines = text.splitlines()
        max_len = max(len(orig_lines), len(new_lines))
        lines_changed = sum(
            1
            for i in range(max_len)
            if (orig_lines[i] if i < len(orig_lines) else "")
            != (new_lines[i] if i < len(new_lines) else "")
        )
        if not dry_run:
            bak = path.with_suffix(path.suffix + ".bak")
            if not bak.exists():
                bak.write_text(original, encoding="utf-8")
            path.write_text(text, encoding="utf-8")

    return FileStats(
        file=str(path),
        attr_replacements=n_attr,
        class_attr_rewrites=n_class,
        input_group_wrapper_removed=n_input_group,
        close_button_rewrites=n_close,
        embed_wrapper_flags=n_embed,
        warnings_count=n_warn_matches + len(warnings),
        warnings=warnings,
        changed=changed,
        lines_changed=lines_changed,
    )


def collect_files(
    root: Path, exts: Sequence[str], filename_filter: Pattern[str] | None
) -> list[Path]:
    """
    Recursively collect files under 'root' matching provided extensions.

    If 'filename_filter' is provided, only return files whose *basename* matches the
    regex.
    """
    results: list[Path] = []
    for ext in exts:
        for p in root.rglob(f"*{ext}"):
            if not p.is_file():
                continue
            if filename_filter is not None and not filename_filter.search(p.name):
                continue
            results.append(p)
    return sorted(results)


# ---------------------------------- CLI --------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Bootstrap 4 -> 5 migration helper for (Django) HTML templates."
    )
    parser.add_argument(
        "root",
        type=str,
        help="Root folder to scan (e.g., path to your templates directory).",
    )
    parser.add_argument(
        "--ext",
        action="append",
        default=[".html"],
        help="File extensions to process (repeatable). Defaults to .html",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write changes; just report what would change.",
    )
    parser.add_argument(
        "--report",
        type=str,
        default="",
        help="Optional JSON report path to write a summary.",
    )
    parser.add_argument(
        "--filename-regex",
        type=str,
        default="",
        help=(
            "Optional regular expression to filter files by *basename*. "
            "Example: '.*_bs5\\.html$' to process only *_bs5.html files."
        ),
    )
    parser.add_argument(
        "--report-warnings-only",
        action="store_true",
        help="If set, the JSON report will include only files that have warnings.",
    )
    return parser


def main() -> None:
    """Entry point: parse args, collect files, process them, and print summary/report."""
    parser = build_arg_parser()
    args = parser.parse_args()

    root = Path(args.root).resolve()
    exts: list[str] = args.ext
    dry_run: bool = args.dry_run
    report_path: str = args.report
    filename_regex: str = args.filename_regex
    report_warnings_only: bool = args.report_warnings_only

    filename_filter: Pattern[str] | None = (
        re.compile(filename_regex) if filename_regex else None
    )

    # Gather all candidate files first (without filename filter) to report "scanned" count.
    all_candidates: list[Path] = []
    for ext in exts:
        all_candidates.extend(root.rglob(f"*{ext}"))
    all_candidates = [p for p in all_candidates if p.is_file()]

    # Apply the filename filter (if any).
    files: list[Path] = collect_files(root, exts, filename_filter)

    if not all_candidates:
        print("No files found to scan under the given root.")
        return
    if not files:
        print("No files matched the given extensions/filename-regex.")
        return

    all_stats: list[FileStats] = []
    total_changed = 0
    total_lines = 0
    total_warnings = 0

    for f in files:
        stats = process_file(f, dry_run)
        all_stats.append(stats)
        if stats.changed:
            total_changed += 1
            total_lines += stats.lines_changed
        total_warnings += stats.warnings_count

        flag = "[DRY]" if dry_run else "[WRITE]"
        chg = "CHANGED" if stats.changed else "OK"
        warns = stats.warnings_count
        print(
            f"{flag} {chg:<8} {f} "
            f"(attrs:{stats.attr_replacements}, class:{stats.class_attr_rewrites}, "
            f"append/prepend-: {stats.input_group_wrapper_removed}, close:{stats.close_button_rewrites}, "
            f"warns:{warns})"
        )

    summary = Summary(
        root=str(root),
        files_scanned=len(all_candidates),
        files_matched=len(files),
        files_changed=total_changed,
        approx_lines_changed=total_lines,
        total_warnings=total_warnings,
        details=all_stats,
    )

    # Write report if requested.
    if report_path:
        details_for_report: list[FileStats] = (
            [s for s in all_stats if s.warnings_count > 0]
            if report_warnings_only
            else all_stats
        )
        files_with_warnings: int = sum(1 for s in all_stats if s.warnings_count > 0)

        report_data = asdict(summary)
        # Override only the "details" section to keep the top-level counts unchanged
        report_data["details"] = [asdict(s) for s in details_for_report]
        # Add a convenience metric
        report_data["files_with_warnings"] = files_with_warnings

        Path(report_path).write_text(
            json.dumps(report_data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    # Print concise summary to console.
    concise = {k: v for k, v in asdict(summary).items() if k != "details"}
    print("\n=== Summary ===")
    print(json.dumps(concise, indent=2, ensure_ascii=False))
    print("\nTips:")
    print(
        "- Review files with WARNINGS (custom forms, jumbotron, media, input-group wrappers)."
    )
    print(
        "- Verify interactive components (dropdowns, modals, tooltips) without jQuery."
    )
    print(
        "- After migration, progressively remove any temporary BS4 compatibility styles."
    )


if __name__ == "__main__":
    main()
