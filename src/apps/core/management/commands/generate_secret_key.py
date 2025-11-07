"""Management command to generate a new Django SECRET_KEY."""

from __future__ import annotations

import contextlib
import re
from pathlib import Path
from typing import Any, Final

from django.core.management.base import BaseCommand, CommandParser
from django.core.management.utils import get_random_secret_key

_ENV_LINE_REGEX: Final[re.Pattern[str]] = re.compile(
    r"^\s*SECRET_KEY\s*=.*$", re.MULTILINE
)


def _escape_for_env(value: str) -> str:
    """
    Escape a string for safe inclusion in a dotenv-style file using double quotes.

    We escape backslashes and double quotes to avoid breaking the line.
    """
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _write_secret_to_env(env_path: Path, secret_key: str) -> None:
    """
    Create or update the SECRET_KEY entry in a dotenv-style file.

    If an existing SECRET_KEY line is found, it is replaced. Otherwise, a new line is
    appended at the end of the file. File permissions are set to 0o600 when the file is
    created for the first time.
    """
    env_path_parent = env_path.parent
    env_path_parent.mkdir(parents=True, exist_ok=True)

    new_line = f'SECRET_KEY="{_escape_for_env(secret_key)}"\n'

    if env_path.exists():
        content = env_path.read_text(encoding="utf-8")
        if _ENV_LINE_REGEX.search(content):
            updated = _ENV_LINE_REGEX.sub(new_line.strip(), content)
            env_path.write_text(
                updated + ("" if updated.endswith("\n") else "\n"), encoding="utf-8"
            )
        else:
            with env_path.open("a", encoding="utf-8") as f:
                # Ensure there is exactly one trailing newline before appending.
                if content and not content.endswith("\n"):
                    f.write("\n")
                f.write(new_line)
    else:
        env_path.write_text(new_line, encoding="utf-8")
        # Restrictive permissions for secrets (best effort on POSIX systems).
        with contextlib.suppress(OSError):
            env_path.chmod(0o600)


class Command(BaseCommand):
    """
    Django management command that generates a fresh SECRET_KEY.

    By default it prints the key to stdout. With --write, it also updates (or creates) a
    dotenv file (default: .env) with SECRET_KEY=<value>.
    """

    help = "Generate a new Django SECRET_KEY and optionally write it to a dotenv file."

    def add_arguments(self, parser: CommandParser) -> None:
        """
        Define CLI arguments for the command.

        --write      Write the generated key into a dotenv file.
        --env-file   Path to the dotenv file (defaults to .env).
        --quiet      Print only the key (no extra messages).
        """
        parser.add_argument(
            "--write",
            action="store_true",
            help="Write the generated key into the dotenv file (see --env-file).",
        )
        parser.add_argument(
            "--env-file",
            type=str,
            default=".env",
            help="Dotenv file to update/create (default: .env).",
        )
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Only print the key to stdout (useful for scripting).",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """
        Entry point for the management command.

        Generates a secure random SECRET_KEY using Django's official utility. Optionally
        writes it to a dotenv file.
        """
        secret_key: str = get_random_secret_key()
        env_file_arg: str = options.get("env_file", ".env")
        write: bool = bool(options.get("write", False))
        quiet: bool = bool(options.get("quiet", False))

        if not quiet:
            self.stdout.write(
                self.style.SUCCESS("A new SECRET_KEY has been generated:")
            )
        self.stdout.write(secret_key)

        if write:
            env_path = Path(env_file_arg)
            _write_secret_to_env(env_path, secret_key)
            if not quiet:
                self.stdout.write(
                    self.style.SUCCESS(f'→ SECRET_KEY written to "{env_path}"')
                )
