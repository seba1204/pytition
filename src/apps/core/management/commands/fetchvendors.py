"""Management command to fetch vendor assets into STATIC_ROOT/vendor."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError, CommandParser

from apps.core.vendors import get_vendor_class, read_vendors_from_pyproject


class Command(BaseCommand):
    """Fetch vendor assets into STATIC_ROOT/vendor."""

    help = "Download vendor assets into STATIC_ROOT/vendor based on pyproject.toml"

    def add_arguments(self, parser: CommandParser) -> None:
        """Add command line arguments for fetchvendors command."""
        parser.add_argument(
            "vendors", nargs="*", help="Optional list of vendor names to fetch."
        )
        parser.add_argument(
            "--force", action="store_true", help="Force re-download even if present."
        )
        parser.add_argument(
            "--pyproject", default="pyproject.toml", help="Path to pyproject.toml"
        )

    def handle(self, *args: object, **opts: object) -> None:
        """Fetch vendor assets into STATIC_ROOT/vendor."""
        opts = dict(opts)  # Ensure opts is a dict
        pyproject = Path(str(opts["pyproject"])).resolve()
        if not pyproject.exists():
            raise CommandError(f"pyproject not found at {pyproject}")
        all_versions = read_vendors_from_pyproject(pyproject)
        vendor_list = opts.get("vendors")
        if not isinstance(vendor_list, (list, tuple)):
            vendor_list = []

        wanted: Iterable[str] = vendor_list or all_versions.keys()

        static_root = Path(getattr(settings, "STATIC_ROOT", "staticfiles")).resolve()
        if not static_root.exists():
            static_root.mkdir(parents=True, exist_ok=True)

        force: bool = bool(opts["force"])
        for name in wanted:
            if name not in all_versions:
                raise CommandError(
                    f"Vendor '{name}' not configured in "
                    f"[tool.pytition.vendors] of {pyproject}"
                )
            version = all_versions[name]
            cls = get_vendor_class(name)
            vendor = cls(name=name, version=version, static_root=static_root)
            res = vendor.ensure(force=force)
            status = "updated" if res.changed else "up-to-date"
            style_success = self.style.SUCCESS
            self.stdout.write(
                style_success(f"{name}@{version}: {status} → {res.dest_dir}")
            )
