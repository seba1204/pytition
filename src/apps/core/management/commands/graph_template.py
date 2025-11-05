"""
Django management command to generate a Mermaid graph of template dependencies (flat,
color-coded).

This command scans the project's Django template directories (restricted to
`src/apps/`), parses `{% extends %}` and constant-string `{% include %}` tags,
and emits a Mermaid diagram showing a dependency graph with **no containers**.
Instead, each node is **colored by its parent folder name** (e.g., `<app_name>`,
`layouts`, `ui`, etc.), which is defined as the first segment under
`<app>/templates/`.

Rules
-----
- If a file path matches `<app>/templates/<app>/...`, the parent key is `<app>`.
- If it matches `<app>/templates/<subdir>/...` (with `subdir != app`), the parent key
  is `<subdir>`.
- Files that are not under `src/apps/` are ignored by design (the scan is filtered).
- Coloring is deterministic: the parent key is hashed to a hex color (HSL-based),
  so the same key always receives the same color.
- Solid arrows (`-->`) represent `extends` relationships.
- Dashed arrows (`-.->`) represent `include` relationships.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from re import Pattern
from typing import Final

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.module_loading import import_string

# --- constants ---------------------------------------------------------------

APPS_ROOT: Final[Path] = (Path(settings.BASE_DIR) / "src" / "apps").resolve()

EXTENDS_RE: Final[Pattern[str]] = re.compile(
    r"""{%\s*extends\s+["'](?P<name>[^"']+)["']\s*%}""", re.IGNORECASE
)
INCLUDE_RE: Final[Pattern[str]] = re.compile(
    r"""{%\s*include\s+["'](?P<name>[^"']+)["'](?:\s+with\s+.*?|)\s*%}""",
    re.IGNORECASE,
)


# --- utilities ---------------------------------------------------------------


def _is_under_apps(path: Path) -> bool:
    """
    Return True if `path` is inside the project's `src/apps/` directory.

    Parameters
    ----------
    path : Path
        Filesystem path to test.

    Returns
    -------
    bool
        True if the given path is under `APPS_ROOT`, False otherwise.
    """
    try:
        path.resolve().relative_to(APPS_ROOT)
        return True
    except Exception:
        return False


@dataclass(frozen=True)
class Edge:
    """
    Represents a dependency edge in the template graph.

    Parameters
    ----------
    source : str
        Source template name (the template that extends/includes another).
    target : str
        Target template name (the template being extended/included).
    kind : str
        Edge kind, either `"extends"` or `"include"`.
    """

    source: str
    target: str
    kind: str  # "extends" or "include"


@dataclass
class TemplateNode:
    """
    Represents a template file and its relationships.

    Parameters
    ----------
    name : str
        Normalized Django template name (e.g., `core/base.html`).
    path : Path
        Filesystem path of the template file.
    extends : Optional[str]
        The `{% extends %}` target if present.
    includes : set[str]
        Constant-string `{% include %}` targets.
    """

    name: str
    path: Path
    extends: str | None = None
    includes: set[str] = field(default_factory=set)


def discover_template_dirs() -> list[Path]:
    """
    Collect all template search directories from Django settings.

    Returns
    -------
    list of Path
        Ordered list of directories to scan for templates (restricted to `src/apps/`).

    Notes
    -----
    - Includes `DIRS` declared in `settings.TEMPLATES`.
    - If `APP_DIRS` is enabled, adds each installed app's `templates/` folder.
    - Filters out any directory that is not under `APPS_ROOT`.
    """
    dirs: list[Path] = []

    # Add explicit DIRS
    for cfg in settings.TEMPLATES:
        dirs_value = cfg.get("DIRS", [])
        if not isinstance(dirs_value, (list, tuple)):
            dirs_value = [dirs_value] if dirs_value else []
        for d in dirs_value:
            p = Path(str(d)).resolve()
            if p.is_dir():
                dirs.append(p)

    # Include app templates if APP_DIRS
    for cfg in settings.TEMPLATES:
        if cfg.get("APP_DIRS"):
            for app_label in settings.INSTALLED_APPS:
                try:
                    mod = import_string(app_label)
                except Exception:
                    # Not importable as a module; skip
                    continue
                pkg_paths = getattr(mod, "__path__", None)
                if not pkg_paths:
                    # Single-file module, no filesystem package
                    continue
                for pkg_path in pkg_paths:
                    template_directory = Path(pkg_path) / "templates"
                    if template_directory.is_dir():
                        dirs.append(template_directory.resolve())

    # Deduplicate while preserving order, and keep only paths under apps/
    seen: set[Path] = set()
    unique_dirs: list[Path] = []
    for d in dirs:
        rd = d.resolve()
        if rd in seen:
            continue
        if _is_under_apps(rd):
            seen.add(rd)
            unique_dirs.append(rd)
    return unique_dirs


def iter_template_files(
    template_dirs: Iterable[Path], exts: tuple[str, ...]
) -> Iterable[Path]:
    """
    Yield template files from given directories.

    Parameters
    ----------
    template_dirs : Iterable[Path]
        Directories to recursively scan.
    exts : tuple of str
        File extensions to include (e.g., (".html", ".txt")).

    Yields
    ------
    Path
        Path to a template file discovered under the template dirs.
    """
    for base in template_dirs:
        for root, _, files in os.walk(base):
            for f in files:
                if f.endswith(exts):
                    yield Path(root) / f


def template_name_for(path: Path, roots: list[Path]) -> str:
    """
    Derive a Django template name from a filesystem path.

    Parameters
    ----------
    path : Path
        Full path to a template file.
    roots : list of Path
        Candidate template roots (search order matters).

    Returns
    -------
    str
        The normalized template name relative to its first matching root.

    Notes
    -----
    - Returns a forward-slashed relative path, suitable as a template name.
    - If no root matches, returns the filename stem as a fallback.
    """
    for r in roots:
        try:
            rel = path.relative_to(r)
        except ValueError:
            continue
        return str(rel.as_posix())
    return path.name


def parse_template(path: Path) -> tuple[str | None, set[str]]:
    """
    Parse a template file to extract `extends` and constant `include` targets.

    Parameters
    ----------
    path : Path
        Filepath to the template.

    Returns
    -------
    extends : Optional[str]
        Name passed to `{% extends "..." %}` if present, else `None`.
    includes : set of str
        Constant includes extracted from `{% include "..." %}`.

    Notes
    -----
    - Only constant string includes are collected.
    - Dynamic includes (variables, lists) are ignored by design.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None, set()

    m = EXTENDS_RE.search(text)
    extends = m.group("name") if m else None
    includes = {n.group("name") for n in INCLUDE_RE.finditer(text)}
    return extends, includes


def parent_key_from_path(path: Path) -> str:
    """
    Compute the color-grouping key (parent folder name) for a template path.

    Parameters
    ----------
    path : Path
        Filesystem path to a template.

    Returns
    -------
    str
        Parent folder key used for color assignment.

    Notes
    -----
    The "parent key" is the first segment after `<app>/templates/`:
    - `<app>/templates/<app>/...` -> `<app>`
    - `<app>/templates/<subdir>/...` -> `<subdir>`
    If the path is not under `APPS_ROOT` or does not match the pattern, returns `"other"`.
    """
    try:
        rel = path.resolve().relative_to(APPS_ROOT)
    except Exception:
        return "other"

    parts = rel.parts  # e.g. ("core", "templates", "layouts", "base.html")
    if len(parts) < 3 or parts[1] != "templates":
        return "other"

    return parts[2]  # first item after "templates" (can be the app name itself)


def _hsl_to_hex(h: float, s: float, l: float) -> str:
    """
    Convert an HSL color (0..1 floats) to a hex string.

    Parameters
    ----------
    h : float
        Hue in range [0, 1].
    s : float
        Saturation in range [0, 1].
    l : float
        Lightness in range [0, 1].

    Returns
    -------
    str
        Hex RGB color like `#A1B2C3`.
    """

    # Convert HSL to RGB (utility; small, dependency-free)
    # Algorithm adapted from the CSS Color Module specification.
    def hue_to_rgb(p: float, q: float, t: float) -> float:
        t = t % 1.0
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6
        return p

    if s == 0.0:
        r = g = b = l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1 / 3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1 / 3)

    ri = int(round(r * 255))
    gi = int(round(g * 255))
    bi = int(round(b * 255))
    return f"#{ri:02X}{gi:02X}{bi:02X}"


def color_from_key(key: str) -> str:
    """
    Deterministically derive a hex color for a grouping key.

    Parameters
    ----------
    key : str
        Group label (e.g., `core`, `layouts`, `ui`).

    Returns
    -------
    str
        Hex RGB color (e.g., `#A1B2C3`).

    Notes
    -----
    - A stable MD5 hash is mapped to HSL space to produce visually distinct colors.
    - Saturation/lightness are clamped to readable ranges for Mermaid defaults.
    """
    h = int(hashlib.md5(key.encode("utf-8")).hexdigest()[:2], 16) / 255.0
    s = 0.55  # moderate saturation for readability
    l = 0.80  # light background to contrast Mermaid's default stroke
    return _hsl_to_hex(h, s, l)


def build_graph(
    roots: list[Path],
    exts: tuple[str, ...],
) -> tuple[dict[str, TemplateNode], list[Edge]]:
    """
    Scan the template tree and construct a dependency graph.

    Parameters
    ----------
    roots : list of Path
        Template search roots.
    exts : tuple of str
        File extensions to include.

    Returns
    -------
    nodes : dict
        Mapping of template name to `TemplateNode`.
    edges : list of Edge
        Directed edges representing `extends` and `include` relationships.
    """
    nodes: dict[str, TemplateNode] = {}
    edges: list[Edge] = []

    for path in iter_template_files(roots, exts):
        name = template_name_for(path, roots)
        extends, includes = parse_template(path)

        node = nodes.get(name) or TemplateNode(name=name, path=path)
        node.extends = extends
        node.includes.update(includes)
        nodes[name] = node

    # Create edges
    for node in nodes.values():
        if node.extends:
            edges.append(Edge(source=node.name, target=node.extends, kind="extends"))
        for inc in sorted(node.includes):
            edges.append(Edge(source=node.name, target=inc, kind="include"))

    return nodes, edges


def mermaid_escape(label: str) -> str:
    """
    Escape Mermaid label characters minimally.

    Parameters
    ----------
    label : str
        Node label.

    Returns
    -------
    str
        Escaped label safe for Mermaid labels inside brackets.
    """
    out = label.replace('"', r"\"")
    out = out.replace("]", r"\]")
    return out


def mermaid_id_for(name: str) -> str:
    """
    Build a safe Mermaid identifier for a node alias.

    Parameters
    ----------
    name : str
        Original template name.

    Returns
    -------
    str
        Alphanumeric/underscore-only identifier starting with a letter.
    """
    base = re.sub(r"[^0-9A-Za-z_]", "_", name)
    if not base or not base[0].isalpha():
        base = f"N_{base}"
    return base


def render_mermaid_flat(nodes: dict[str, TemplateNode], edges: list[Edge]) -> str:
    """
    Render the graph as Mermaid without containers (flat), color-coding nodes by parent
    key.

    Parameters
    ----------
    nodes : dict
        Nodes keyed by template name.
    edges : list of Edge
        Graph edges.

    Returns
    -------
    str
        Mermaid markup.
    """
    lines: list[str] = []
    lines.append("%% dependency graph of Django templates (Mermaid, flat)")
    lines.append("graph LR")
    lines.append("%% solid arrows: extends; dashed arrows: include")

    # Precompute node aliases and labels
    aliases: dict[str, str] = {}
    for name in nodes:
        aliases[name] = mermaid_id_for(name)

    # Declare nodes
    for name in sorted(nodes.keys()):
        label = mermaid_escape(name)
        alias = aliases[name]
        lines.append(f'{alias}["{label}"]')

    # Draw edges using aliases
    # Only keep edges whose endpoints exist (i.e., ignore unresolved targets)
    node_names: set[str] = set(nodes.keys())
    for e in edges:
        if e.source not in node_names or e.target not in node_names:
            continue
        src = aliases[e.source]
        dst = aliases[e.target]
        if e.kind == "extends":
            lines.append(f"{src} --> {dst}")
        else:
            lines.append(f"{src} -.-> {dst}")

    # Style nodes by parent key (deterministic color per key)
    groups: dict[str, list[str]] = {}
    for name, node in nodes.items():
        key = parent_key_from_path(node.path)
        groups.setdefault(key, []).append(aliases[name])

    for key, alias_list in sorted(groups.items()):
        color = color_from_key(key)
        for alias in alias_list:
            lines.append(f"style {alias} fill:{color},stroke:#333,stroke-width:1px")

    # Legend as comments (informational)
    lines.append(
        "%% legend: nodes are colored by the first segment under <app>/templates/"
    )
    lines.append("%% example keys: <app_name>, layouts, ui, registration, ...")

    return "\n".join(lines)


# --- command -----------------------------------------------------------------


class Command(BaseCommand):
    """
    Django management command to generate a flat Mermaid dependency graph of templates.

    The command walks through all template directories configured in Django, parses
    `{% extends %}` and constant-string `{% include %}` tags, and emits a Mermaid
    diagram describing the dependency graph. Nodes are **color-coded** based on the
    first folder name after `<app>/templates/` and **no containers** are used.

    Examples
    --------
    Generate a `.mmd` file next to the project:

    >>> python manage.py graph_template_mermaid_flat --output templates_graph_flat.mmd

    Print Mermaid to stdout:

    >>> python manage.py graph_template_mermaid_flat -o -
    """

    help = (
        "Generate a flat Mermaid graph of template dependencies with color-coded nodes."
    )

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """
        Register CLI arguments.

        Parameters
        ----------
        parser : argparse.ArgumentParser
            The argument parser to register options on.
        """
        parser.add_argument(
            "-o",
            "--output",
            default="templates_graph_flat.mmd",
            help='Output file path or "-" for stdout (default: templates_graph_flat.mmd).',
        )
        parser.add_argument(
            "--ext",
            action="append",
            default=[".html", ".txt"],
            help="Template file extension to include (default: .html, .txt).",
        )
        parser.add_argument(
            "--no-includes",
            action="store_true",
            help="If set, omit 'include' edges (only show 'extends' relationships).",
        )

        parser.add_argument(
            "--no-extends",
            action="store_true",
            help="If set, omit 'extends' edges (only show 'includes' relationships).",
        )

    def handle(self, *args: object, **options: object) -> str | None:
        """
        Execute the command.

        Parameters
        ----------
        *args : object
            Positional arguments (unused).
        **options : object
            Parsed CLI options.

        Returns
        -------
        Optional[str]
            If writing to stdout, returns the Mermaid content so Django prints it.
            Otherwise returns `None`.
        """
        output: str = str(options["output"])
        exts_list: list[str] = (
            list(options["ext"])
            if isinstance(options["ext"], (list, tuple))
            else [str(options["ext"])]
        )
        exts: tuple[str, ...] = tuple(
            ext if ext.startswith(".") else f".{ext}" for ext in exts_list
        )

        roots = discover_template_dirs()
        if not roots:
            raise CommandError(
                "No template directories found. Check your TEMPLATES setting."
            )

        nodes, edges = build_graph(roots, exts)

        # Keep only nodes whose files live under apps/, and drop edges accordingly.
        filtered_nodes: dict[str, TemplateNode] = {
            k: v for k, v in nodes.items() if _is_under_apps(v.path)
        }
        filtered_names: set[str] = set(filtered_nodes.keys())
        filtered_edges: list[Edge] = [
            e
            for e in edges
            if e.source in filtered_names and e.target in filtered_names
        ]

        if options.get("no_includes"):
            filtered_edges = [e for e in filtered_edges if e.kind != "include"]

        if options.get("no_extends"):
            filtered_edges = [e for e in filtered_edges if e.kind != "extends"]

        mermaid = render_mermaid_flat(filtered_nodes, filtered_edges)

        if output == "-":
            # Print to stdout
            self.stdout.write(mermaid)
            return None

        out_path = Path(output)
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(mermaid, encoding="utf-8")
        except Exception as exc:
            raise CommandError(f"Failed to write output to {out_path}: {exc}") from exc

        self.stdout.write(self.style.SUCCESS(f"Mermaid graph written to {out_path}"))
        return None
