from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser

from apps.core.assets import get_steps
from apps.core.assets.base import Context


class Command(BaseCommand):
    help = (
        "Builds assets (WebP images, minified CSS/JS + sourcemaps, favicons,"
        "manifest, browserconfig) in STATIC_ROOT."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--assets-dir",
            default=None,
            help=(
                "Path to the assets folder "
                "(default: settings.ASSETS_DIR or <repo>/assets)"
            ),
        )
        parser.add_argument(
            "--static-root",
            default=None,
            help="Out (default: settings.ASSETS_STATIC_ROOT or settings.STATIC_ROOT)",
        )
        parser.add_argument(
            "--only",
            nargs="*",
            default=None,
            help="Limit to certain stages (e.g., images, styles, scripts).",
        )
        parser.add_argument(
            "--skip", nargs="*", default=None, help="Skip certain steps."
        )

    def handle(self, *args: object, **opts: object) -> None:
        opts = dict(opts)  # Ensure opts is a dict
        assets_dir = opts["assets_dir"]
        static_root = opts["static_root"]

        if assets_dir is None:
            assets_dir = getattr(
                settings, "ASSETS_DIR", Path(settings.BASE_DIR).parent / "assets"
            )
        assets_dir = Path(str(assets_dir))

        if static_root is None:
            static_root = getattr(settings, "ASSETS_STATIC_ROOT", settings.STATIC_ROOT)
        static_root = Path(str(static_root))

        static_root.mkdir(parents=True, exist_ok=True)

        only_list = opts.get("only")
        if not isinstance(only_list, (list, tuple)):
            only_list = []
        only = {s.lower() for s in only_list}

        skip_list = opts.get("skip")
        if not isinstance(skip_list, (list, tuple)):
            skip_list = []
        skip = {s.lower() for s in skip_list}

        ctx = Context(
            assets_dir=assets_dir,
            static_root=static_root,
            settings=settings,
            stdout=self.stdout,
            stderr=self.stderr,
        )

        steps = get_steps()
        if only:
            steps = [(n, cls) for (n, cls) in steps if n in only]
        if skip:
            steps = [(n, cls) for (n, cls) in steps if n not in skip]

        self.stdout.write(f"→ Build assets from: {assets_dir}")
        self.stdout.write(f"→ Output to: {static_root}")

        for name, cls in steps:
            step = cls(name)
            self.stdout.write(f"• {name}…")
            step.run(ctx)

        style_success = self.style.SUCCESS
        self.stdout.write(style_success("✓ Assets built successfully."))
