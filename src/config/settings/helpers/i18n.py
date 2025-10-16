"""
i18n.py — Build LANGUAGES and EXTRA_LANG_INFO from LOCALE_PATHS by inspecting .po files.

Rules:
- Nothing hardcoded: discover locale codes from filesystem
- Language display name sourced from .po headers:
    1) "Language:" header
    2) "Language-Team:" header (strip email/angles)
    3) Fallback: capitalize code segments (best effort)
- If a code is unknown to Django's LANG_INFO, expose a minimal EXTRA_LANG_INFO entry.
"""

from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, Iterable, Mapping, Tuple

from django.conf.locale import LANG_INFO as DJANGO_LANG_INFO

_PO_HEADER_LINE = re.compile(r'^"(?P<key>[^:]+):\s*(?P<val>.*?)\\n"$')


def iter_po_headers(po_path: Path) -> Dict[str, str]:
    """
    Return {header_key: header_value} from the header block of a .po file.
    Only reads the quoted header lines immediately following:
      msgid "" / msgstr ""
    Stops at the first non-quoted line.
    """
    headers: Dict[str, str] = {}
    try:
        with po_path.open("r", encoding="utf-8") as f:
            in_header = False
            for line in f:
                if line.startswith('msgid ""'):
                    in_header = True
                    continue
                if in_header and line.startswith('msgstr ""'):
                    continue
                if in_header:
                    if line.startswith('"'):
                        m = _PO_HEADER_LINE.match(line.strip())
                        if m:
                            headers[m.group("key")] = m.group("val")
                    else:
                        break
    except FileNotFoundError:
        pass
    return headers


def discover_locale_dirs(locale_paths: Iterable[Path]) -> Dict[str, Path]:
    """
    Return a mapping {code -> locale_dir} for locales that contain LC_MESSAGES/django.po|.mo.
    If multiple LOCALE_PATHS provide the same code, last one wins.
    """
    found: Dict[str, Path] = {}
    for root in map(Path, locale_paths):
        if not root.exists():
            continue
        for lang_dir in root.iterdir():
            if not lang_dir.is_dir():
                continue
            code = lang_dir.name.lower()
            lc = lang_dir / "LC_MESSAGES"
            if (lc / "django.po").exists() or (lc / "django.mo").exists():
                found[code] = lang_dir
    return found


def extract_lang_name(code: str, lang_dir: Path) -> str:
    """
    Extract a human-readable language name from .po headers.
    Fallback to a best-effort capitalization of the code segments.
    """
    headers = iter_po_headers(lang_dir / "LC_MESSAGES" / "django.po")
    lang = headers.get("Language")
    if lang:
        return lang.strip()

    team = headers.get("Language-Team")
    if team:
        # strip email addresses within angle brackets
        return re.sub(r"<[^>]+>", "", team).strip()

    # Best-effort: "pt-br" -> "Pt-Br", "oc" -> "Oc"
    return re.sub(r"[a-zA-Z]+", lambda m: m.group(0).capitalize(), code)


def build_languages(locale_paths: Iterable[Path]) -> Tuple[Tuple[Tuple[str, str], ...], Dict[str, Dict[str, str]]]:
    """
    Build (LANGUAGES, EXTRA_LANG_INFO) by scanning LOCALE_PATHS.
    - LANGUAGES: tuple of (code, name)
    - EXTRA_LANG_INFO: only for codes not present in Django's LANG_INFO.
    """
    locales = discover_locale_dirs(locale_paths)
    languages = []
    extra_info: Dict[str, Dict[str, str]] = {}

    for code, path in sorted(locales.items()):
        name = extract_lang_name(code, path)
        languages.append((code, name))
        if code not in DJANGO_LANG_INFO:
            extra_info[code] = {"code": code, "name": name}

    return tuple(languages), extra_info
