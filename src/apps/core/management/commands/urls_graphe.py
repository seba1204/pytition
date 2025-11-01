from __future__ import annotations

import hashlib
from collections.abc import Iterable, Sequence
from pathlib import Path

from django.core.management.base import BaseCommand, CommandParser
from django.urls import URLPattern, URLResolver, get_resolver

# ===== Typing =====


class UrlKind:
    RESOLVER = "resolver"
    PATTERN = "pattern"


class UrlEntry:
    """
    Flat URL entry extracted from the resolver tree.

    Only used for filtering/graph wiring; output shows paths only.
    """

    __slots__ = ("full_path", "kind", "view_import")

    def __init__(self, full_path: str, kind: str, view_import: str | None) -> None:
        self.full_path = full_path  # canonical ending with '/', e.g. 'api/users/'
        self.kind = kind  # "resolver" or "pattern"
        self.view_import = (
            view_import  # import path for filtering static/media; not rendered
        )


# ===== Config / helpers =====

STATIC_VIEW_PREFIXES: tuple[str, ...] = (
    "django.views.static",
    "django.contrib.staticfiles.views",
)
DEFAULT_ASSET_EXTENSIONS: tuple[str, ...] = (
    ".ico",
    ".png",
    ".jpg",
    ".jpeg",
    ".svg",
    ".webp",
    ".txt",
    ".xml",
    ".css",
    ".js",
    ".map",
)

INCLUDE_VIEW_PREFIXES: tuple[str, ...] = ("apps.",)


def mermaid_escape_label(text: str) -> str:
    """Escape a label for Mermaid flowchart (no HTML rendering needed)."""
    s = text.replace("&", "&amp;")
    s = s.replace("<", "&lt;").replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    s = s.replace("{", "&#123;").replace("}", "&#125;")
    s = s.replace("[", "&#91;").replace("]", "&#93;")
    s = s.replace("|", "&#124;")
    return s


def node_id(key: str) -> str:
    """Create a stable Mermaid-safe node id from an arbitrary key."""
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]
    return f"n_{digest}"


def _parent_of(path: str) -> str:
    """Return the canonical parent path for a path ending with '/'."""
    if path in ("/", ""):
        return "/"
    parts = [p for p in path.strip("/").split("/") if p]
    if not parts:
        return "/"
    parent_parts = parts[:-1]
    return "/" if not parent_parts else "/".join(parent_parts) + "/"


def _last_segment(path: str) -> str:
    """Return the last URL segment prefixed with '/', or '/' for root."""
    if path in ("/", "", None):
        return "/"
    seg = path.strip("/").split("/")[-1]
    return "/" + seg if seg else "/"


def _has_asset_extension(path: str, extensions: Sequence[str]) -> bool:
    """Return True if path ends with any of the given extensions (case-insensitive)."""
    last = path.rstrip("/").split("/")[-1].lower()
    return any(last.endswith(ext.lower().lstrip()) for ext in extensions)


def _pattern_to_text(pattern: object) -> str:
    """Convert RoutePattern/RegexPattern to a readable string."""
    try:
        return str(pattern)
    except Exception:
        for attr in ("_route", "_regex"):
            val = getattr(pattern, attr, None)
            if val:
                return str(val)
        return "<pattern>"


def _view_to_import(callback: object) -> str:
    """Return 'module.qualname' for a view callable; best-effort fallback to repr()."""
    try:
        mod = getattr(callback, "__module__", "")
        name = getattr(callback, "__name__", repr(callback))
        return f"{mod}.{name}"
    except Exception:
        return repr(callback)


# ===== Harvest / Filter / Build =====


def harvest_urls() -> list[UrlEntry]:
    """Walk Django's URL resolver tree and produce flat UrlEntry records."""
    resolver = get_resolver()
    out: list[UrlEntry] = []

    def walk(urlpatterns: Sequence[object], prefix_parts: list[str]) -> None:
        for entry in urlpatterns:
            if isinstance(entry, URLPattern):
                pattern_text = _pattern_to_text(entry.pattern)
                full_parts = prefix_parts + [pattern_text]
                full_path = "/".join([p.strip("/") for p in full_parts if p]) + "/"
                view_str = _view_to_import(entry.callback)
                out.append(
                    UrlEntry(
                        full_path=full_path, kind=UrlKind.PATTERN, view_import=view_str
                    )
                )
            elif isinstance(entry, URLResolver):
                pattern_text = _pattern_to_text(entry.pattern)
                full_parts = prefix_parts + [pattern_text]
                full_path = "/".join([p.strip("/") for p in full_parts if p]) + "/"
                out.append(
                    UrlEntry(
                        full_path=full_path, kind=UrlKind.RESOLVER, view_import=None
                    )
                )
                try:
                    walk(entry.url_patterns, prefix_parts + [pattern_text])
                except Exception:
                    # Some resolvers lazily compute subpatterns;
                    # ignore failures gracefully.
                    continue
            else:
                continue

    walk(resolver.url_patterns, [])
    return out


def filter_entries(
    entries: Iterable[UrlEntry],
    exclude_admin: bool,
    exclude_static_media: bool,
    asset_extensions: Sequence[str],
    exclude_prefixes: set[str],
) -> list[UrlEntry]:
    """
    Keep only relevant entries for rendering path-only graph.

    - Enforce that URLPattern views must live under INCLUDE_VIEW_PREFIXES.
    - Keep ancestor resolvers of kept patterns so the tree stays connected.
    """
    prelim: list[UrlEntry] = []

    for url_entry in entries:
        normalize_path: UrlEntry

        # Normalize empty to "/"
        normalize_path = (
            UrlEntry("/", url_entry.kind, url_entry.view_import)
            if url_entry.full_path == ""
            else url_entry
        )

        # Exclude arbitrary prefixes
        if any(
            normalize_path.full_path.startswith(p if p.endswith("/") else f"{p}/")
            for p in exclude_prefixes
        ):
            continue

        # Exclude admin subtree
        if exclude_admin and normalize_path.full_path.startswith("admin/"):
            continue

        # Exclude static/media serving views
        if (
            exclude_static_media
            and normalize_path.kind == UrlKind.PATTERN
            and normalize_path.view_import
            and normalize_path.view_import.startswith(STATIC_VIEW_PREFIXES)
        ):
            continue

        # Exclude obvious assets by extension (e.g., favicon.ico)
        if _has_asset_extension(normalize_path.full_path, asset_extensions):
            continue

        prelim.append(normalize_path)

    # Pass 2: keep only patterns whose view is under INCLUDE_VIEW_PREFIXES
    kept_pattern_paths: set[str] = set()
    for normalize_path in prelim:
        if (
            normalize_path.kind == UrlKind.PATTERN
            and normalize_path.view_import
            and normalize_path.view_import.startswith(INCLUDE_VIEW_PREFIXES)
        ):
            kept_pattern_paths.add(normalize_path.full_path)

    # Ancestor check for resolvers
    def is_ancestor(resolver_path: str) -> bool:
        return any(lp.startswith(resolver_path) for lp in kept_pattern_paths)

    final: list[UrlEntry] = []
    for normalize_path in prelim:
        if normalize_path.kind == UrlKind.PATTERN:
            if normalize_path.full_path in kept_pattern_paths:
                final.append(normalize_path)
        elif is_ancestor(normalize_path.full_path) or normalize_path.full_path == "/":
            final.append(normalize_path)

    return final


def build_mermaid(
    entries: Sequence[UrlEntry],
    orientation: str = "LR",
) -> str:
    """
    Build a Mermaid flowchart with **path nodes only**.

    - Node label: last segment of the path (e.g., '/dashboard'; '/' for root).
    - Edges: parent path -> child path.
    """
    ori = orientation if orientation in {"TD", "LR", "BT", "RL"} else "LR"

    # Nodes: key => label; Edges: (parent, child)
    nodes: dict[str, str] = {"/": "/"}
    edges: set[tuple[str, str]] = set()

    all_paths: set[str] = {"/"}
    for ent in entries:
        p = ent.full_path or "/"
        all_paths.add(p if p else "/")

    for ent in entries:
        path = ent.full_path or "/"
        if path == "":
            path = "/"

        # Label logic:
        # - if the parent is present in the graph => show only last segment
        #   (e.g., '/dashboard')
        # - otherwise (no parent) => show full path (e.g., '/petition/user/dashboard')
        if path not in nodes:
            parent = _parent_of(path)
            if parent in all_paths and parent != path:
                nodes[path] = _last_segment(path)
            else:
                nodes[path] = "/" + path.strip("/") if path != "/" else "/"

        parent = _parent_of(path)
        # Avoid self-loop for root
        if parent != path:
            edges.add((parent, path))

    # Emit Mermaid
    out: list[str] = [f"flowchart {ori}"]

    # Emit nodes
    id_map: dict[str, str] = {k: node_id(k) for k in nodes}
    for key, label in nodes.items():
        nid = id_map[key]
        lbl = mermaid_escape_label(label)
        out.append(f'  {nid}["{lbl}"]')

    # Emit edges (sorted for stability)
    for parent, child in sorted(edges):
        pid = id_map.get(parent)
        cid = id_map.get(child)
        if pid and cid:
            out.append(f"  {pid} --> {cid}")

    return "\n".join(out) + "\n"


# ===== Management command =====


class Command(BaseCommand):
    help = "Generate a Mermaid flowchart of Django URL paths (paths only)."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "-o",
            "--outfile",
            default="urls.mmd",
            help="Output Mermaid file path (default: urls.mmd)",
        )
        parser.add_argument(
            "--orientation",
            default="LR",
            choices=["TD", "LR", "BT", "RL"],
            help="Mermaid flowchart orientation (default: LR)",
        )
        parser.add_argument(
            "--exclude-admin",
            action="store_true",
            default=True,
            help="Exclude all routes under 'admin/' (default: on)",
        )
        parser.add_argument(
            "--no-exclude-admin",
            dest="exclude_admin",
            action="store_false",
            help="Do not exclude admin/",
        )
        parser.add_argument(
            "--exclude-static-media",
            action="store_true",
            default=True,
            help="Exclude Django static/media serving views (default: on)",
        )
        parser.add_argument(
            "--no-exclude-static-media",
            dest="exclude_static_media",
            action="store_false",
            help="Do not exclude static/media views",
        )
        parser.add_argument(
            "--asset-extensions",
            default=",".join(DEFAULT_ASSET_EXTENSIONS),
            help=f"Comma-separated file extensions to treat as assets "
            f"(default: {','.join(DEFAULT_ASSET_EXTENSIONS)})",
        )
        parser.add_argument(
            "--exclude-prefix",
            action="append",
            default=[],
            help=(
                "URL path prefix to exclude (repeatable), e.g. --exclude-prefix debug/"
            ),
        )

    def handle(self, *args: object, **options: object) -> None:
        outfile: str = str(options.get("outfile"))
        orientation: str = str(options.get("orientation"))
        exclude_admin: bool = bool(options.get("exclude_admin"))
        exclude_static_media: bool = bool(options.get("exclude_static_media"))
        asset_extensions_raw: str = str(options.get("asset_extensions"))
        exclude_prefixes_raw = options.get("exclude_prefix")
        exclude_prefixes_list: list[str] = (
            list(exclude_prefixes_raw)
            if isinstance(exclude_prefixes_raw, (list, tuple))
            else []
        )

        asset_exts: list[str] = [
            p.strip() for p in asset_extensions_raw.split(",") if p.strip()
        ]
        if not asset_exts:
            asset_exts = list(DEFAULT_ASSET_EXTENSIONS)

        entries = harvest_urls()
        filtered = filter_entries(
            entries=entries,
            exclude_admin=exclude_admin,
            exclude_static_media=exclude_static_media,
            asset_extensions=asset_exts,
            exclude_prefixes=set(exclude_prefixes_list),
        )
        mermaid = build_mermaid(filtered, orientation=orientation)

        try:
            with Path(outfile).open("w", encoding="utf-8") as f:
                f.write(mermaid)
        except OSError as exc:
            raise SystemExit(f"[ERROR] Cannot write {outfile}: {exc}") from exc

        self.stdout.write(
            self.style.SUCCESS(f"[OK] Mermaid graph written to: {outfile}")
        )
