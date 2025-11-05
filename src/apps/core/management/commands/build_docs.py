"""
Management command to build Sphinx documentation for all configured languages.

This command performs the full i18n workflow:
1) Extract messages to POT files with `sphinx-build -b gettext`
2) Update PO files for all Django `settings.LANGUAGES` via `sphinx-intl update`
3) Build HTML for each language (output in `docs/build/html/<lang>/`)
4) Create a root `index.html` redirecting to the default language

Usage:
    python manage.py docs_build
    python manage.py docs_build --clean
    python manage.py docs_build --skip-intl
    python manage.py docs_build --jobs 4
    python manage.py docs_build --locale-dir docs/locale --pot-dir docs/locale/pot
"""

from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError, CommandParser

# Default paths relative to the Django project root
DOCS_DIR: Path = Path("docs")
SRC_DIR: Path = DOCS_DIR / "source"
BUILD_DIR: Path = DOCS_DIR / "build" / "html"
DEFAULT_LOCALE_DIR: Path = DOCS_DIR / "locale"
DEFAULT_POT_DIR: Path = DEFAULT_LOCALE_DIR / "pot"


def run_command(cmd: Sequence[str], env: Mapping[str, str] | None = None) -> None:
    """
    Run a subprocess command with strict error handling.

    Args:
        cmd: The command and arguments to execute.
        env: Optional environment variables mapping (merged over current env).

    Raises:
        CommandError: If the executable is missing or the command exits non-zero.
    """
    try:
        subprocess.run(list(cmd), check=True, env=dict(env) if env else None)
    except FileNotFoundError:
        raise CommandError(f"Command not found: {cmd[0]!r}. Is it installed?") from None
    except subprocess.CalledProcessError as exc:
        raise CommandError(
            f"Command failed with exit code {exc.returncode}: {' '.join(cmd)}"
        ) from exc


def get_configured_languages() -> list[str]:
    """
    Read enabled languages from Django settings.LANGUAGES.

    Returns:
        The list of language codes (e.g., ["en", "fr"]).

    Raises:
        CommandError: If LANGUAGES is empty or not configured.
    """
    langs_raw: Sequence[tuple[str, str]] = getattr(settings, "LANGUAGES", ())
    languages: list[str] = [code for code, _name in langs_raw]
    if not languages:
        raise CommandError("No languages configured in settings.LANGUAGES")
    return languages


def extract_messages(src_dir: Path, pot_dir: Path, jobs: str) -> None:
    """
    Extract translatable strings from Sphinx sources into POT files.

    Args:
        src_dir: Sphinx source directory (where conf.py and .rst/.md live).
        pot_dir: Directory where POT files will be generated.
        jobs: Value passed to sphinx-build `-j` (e.g., 'auto' or '4').
    """
    pot_dir.mkdir(parents=True, exist_ok=True)
    run_command(
        [
            "sphinx-build",
            "-b",
            "gettext",
            str(src_dir),
            str(pot_dir),
            "-j",
            jobs,
        ]
    )


def update_po_files(locale_dir: Path, pot_dir: Path, languages: Iterable[str]) -> None:
    """
    Update PO files for all given languages using sphinx-intl.

    Args:
        locale_dir: Destination directory for PO files (e.g., docs/locale).
        pot_dir: Source POT directory produced by gettext build.
        languages: Language codes to update.

    Notes:
        Passing `-d <locale_dir>` is important; otherwise sphinx-intl defaults to
        a `locale/` folder in the current working directory.
    """
    locale_dir.mkdir(parents=True, exist_ok=True)
    args: list[str] = [
        "sphinx-intl",
        "update",
        "-p",
        str(pot_dir),
        "-d",
        str(locale_dir),
    ]
    for lang in languages:
        args.extend(["-l", lang])
    run_command(args)


def build_language_html(src_dir: Path, build_dir: Path, lang: str, jobs: str) -> None:
    """
    Build Sphinx HTML for a specific language.

    Args:
        src_dir: Sphinx source directory.
        build_dir: Root HTML build directory (language subfolders will be created).
        lang: Language code to build.
        jobs: Value passed to sphinx-build `-j`.
    """
    out_dir: Path = build_dir / lang
    out_dir.mkdir(parents=True, exist_ok=True)
    env: dict[str, str] = dict(os.environ)
    # Sphinx picks language from conf.py `language` or -D language=...
    # Here we set an env var read in conf.py (SPHINX_LANGUAGE) to keep things simple.
    env["SPHINX_LANGUAGE"] = lang
    run_command(
        [
            "sphinx-build",
            "-b",
            "html",
            str(src_dir),
            str(out_dir),
            "-j",
            jobs,
        ],
        env=env,
    )


def write_root_redirect(build_dir: Path, default_lang: str) -> None:
    """
    Write a tiny root index.html that redirects to the default language.

    Args:
        build_dir: Root HTML build directory.
        default_lang: Language code to be used as the default landing page.
    """
    build_dir.mkdir(parents=True, exist_ok=True)
    redirect_html: str = (
        '<!doctype html><meta charset="utf-8">'
        f'<meta http-equiv="refresh" content="0; url=./{default_lang}/index.html">'
        f'<script>location.href="./{default_lang}/index.html"</script>'
    )
    (build_dir / "index.html").write_text(redirect_html, encoding="utf-8")


def _has_pot_files(pot_dir: Path) -> bool:
    """
    Check whether the POT directory contains at least one .pot file.

    Args:
        pot_dir: POT directory path.

    Returns:
        True if there is at least one .pot file, False otherwise.
    """
    return any(pot_dir.rglob("*.pot"))


class Command(BaseCommand):
    """
    Django management command to build Sphinx documentation for all languages.

    Options:
        --clean             Remove previous HTML build directory before building
        --skip-intl         Skip PO update step (useful if Weblate already updated them)
        --jobs <N>          Pass value to sphinx-build -j (default: 'auto')
        --locale-dir <DIR>  Override docs locale directory (default: docs/locale)
        --pot-dir <DIR>     Override POT directory (default: docs/locale/pot)
    """

    help = "Build Sphinx docs for ALL languages (extract -> update -> build)."

    def add_arguments(self, parser: CommandParser) -> None:
        """Register CLI arguments for the management command."""
        parser.add_argument(
            "--clean",
            action="store_true",
            help="Clean build dir first",
        )
        parser.add_argument(
            "--skip-intl",
            action="store_true",
            help="Skip sphinx-intl update step",
        )
        parser.add_argument(
            "--jobs",
            default="auto",
            help="Value passed to sphinx-build -j (default: auto)",
        )
        parser.add_argument(
            "--locale-dir",
            default=str(DEFAULT_LOCALE_DIR),
            help=f"Locale directory for PO files (default: {DEFAULT_LOCALE_DIR})",
        )
        parser.add_argument(
            "--pot-dir",
            default=str(DEFAULT_POT_DIR),
            help=f"POT directory (default: {DEFAULT_POT_DIR})",
        )

    def handle(self, *args: object, **opts: object) -> None:
        """
        Execute the management command.

        Workflow:
            1. Optionally clean the output directory.
            2. Extract POT files from sources.
            3. Optionally update PO files with sphinx-intl (with explicit -d).
            4. Build HTML for each configured language.
            5. Create a root redirect to the default language.
        """
        clean: bool = bool(opts.get("clean"))
        skip_intl: bool = bool(opts.get("skip_intl"))
        jobs: str = str(opts.get("jobs") or "auto")

        locale_dir = Path(str(opts.get("locale_dir") or DEFAULT_LOCALE_DIR))
        pot_dir = Path(str(opts.get("pot_dir") or DEFAULT_POT_DIR))

        languages: list[str] = get_configured_languages()
        default_lang: str = languages[0]

        # Filter out the source language ("en" by default)
        langs_for_update = [lang for lang in languages if lang != default_lang]

        if clean and BUILD_DIR.exists():
            shutil.rmtree(BUILD_DIR)

        BUILD_DIR.mkdir(parents=True, exist_ok=True)
        locale_dir.mkdir(parents=True, exist_ok=True)
        pot_dir.mkdir(parents=True, exist_ok=True)

        self.stdout.write(self.style.HTTP_INFO("→ Extracting messages (gettext)..."))
        extract_messages(src_dir=SRC_DIR, pot_dir=pot_dir, jobs=jobs)

        if not _has_pot_files(pot_dir):
            raise CommandError(
                f"No POT files were generated in {pot_dir}. "
                "Ensure Sphinx sources exist and `conf.py` is correct."
            )

        if not skip_intl:
            self.stdout.write(
                self.style.HTTP_INFO("→ Updating .po files (sphinx-intl)...")
            )
            if not langs_for_update:
                self.stdout.write(
                    self.style.WARNING(
                        "No non-source languages found — skipping sphinx-intl."
                    )
                )
            else:
                update_po_files(
                    locale_dir=locale_dir, pot_dir=pot_dir, languages=langs_for_update
                )

        for lang in languages:
            self.stdout.write(self.style.HTTP_INFO(f"→ Building HTML for {lang}..."))
            build_language_html(
                src_dir=SRC_DIR, build_dir=BUILD_DIR, lang=lang, jobs=jobs
            )

        write_root_redirect(build_dir=BUILD_DIR, default_lang=default_lang)
        self.stdout.write(self.style.SUCCESS("✓ All languages built."))
