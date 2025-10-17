from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.assets import get_steps
from apps.core.assets.base import Context


class Command(BaseCommand):
    help = "Construit les assets (images WebP, CSS/JS minifiés + sourcemaps, favicons, manifest, browserconfig) dans STATIC_ROOT."

    def add_arguments(self, parser):
        parser.add_argument(
            "--assets-dir",
            default=None,
            help="Chemin vers le dossier assets (défaut: settings.ASSETS_DIR ou <repo>/assets)",
        )
        parser.add_argument(
            "--static-root",
            default=None,
            help="Sortie (défaut: settings.ASSETS_STATIC_ROOT ou settings.STATIC_ROOT)",
        )
        parser.add_argument(
            "--only",
            nargs="*",
            default=None,
            help="Limiter à certaines étapes (ex: images styles scripts).",
        )
        parser.add_argument(
            "--skip", nargs="*", default=None, help="Ignorer certaines étapes."
        )

    def handle(self, *args, **opts):
        assets_dir = opts["assets_dir"]
        static_root = opts["static_root"]

        if assets_dir is None:
            assets_dir = getattr(
                settings, "ASSETS_DIR", Path(settings.BASE_DIR).parent / "assets"
            )
        assets_dir = Path(assets_dir)

        if static_root is None:
            static_root = getattr(settings, "ASSETS_STATIC_ROOT", settings.STATIC_ROOT)
        static_root = Path(static_root)

        static_root.mkdir(parents=True, exist_ok=True)

        only = set([s.lower() for s in (opts["only"] or [])])
        skip = set([s.lower() for s in (opts["skip"] or [])])

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
