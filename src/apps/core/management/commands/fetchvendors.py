from __future__ import annotations
import os
from pathlib import Path
from typing import Iterable
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.core.vendors import get_vendor_class, read_vendors_from_pyproject

class Command(BaseCommand):
    help = "Download vendor assets into STATIC_ROOT/vendor based on pyproject.toml"

    def add_arguments(self, parser):
        parser.add_argument("vendors", nargs="*", help="Optional list of vendor names to fetch.")
        parser.add_argument("--force", action="store_true", help="Force re-download even if present.")
        parser.add_argument("--pyproject", default="pyproject.toml", help="Path to pyproject.toml")

    def handle(self, *args, **opts):
        pyproject = Path(opts["pyproject"]).resolve()
        if not pyproject.exists():
            raise CommandError(f"pyproject not found at {pyproject}")
        all_versions = read_vendors_from_pyproject(pyproject)
        wanted: Iterable[str] = opts["vendors"] or all_versions.keys()

        static_root = Path(getattr(settings, "STATIC_ROOT", "staticfiles")).resolve()
        if not static_root.exists():
            static_root.mkdir(parents=True, exist_ok=True)

        force: bool = bool(opts["force"])
        for name in wanted:
            if name not in all_versions:
                raise CommandError(
                    f"Vendor '{name}' not configured in [tool.pytition.vendors] of {pyproject}"
                )
            version = all_versions[name]
            cls = get_vendor_class(name)
            vendor = cls(name=name, version=version, static_root=static_root)
            res = vendor.ensure(force=force)
            status = "updated" if res.changed else "up-to-date"
            style_success = getattr(self.style, "SUCCESS")
            self.stdout.write(style_success(f"{name}@{version}: {status} → {res.dest_dir}"))