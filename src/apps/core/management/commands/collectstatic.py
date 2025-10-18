from __future__ import annotations

from django.contrib.staticfiles.management.commands.collectstatic import (
    Command as CollectStatic,
)
from django.core.management import call_command


class Command(CollectStatic):
    help = "Build assets, fetch vendor assets, then run collectstatic."

    def handle(self, *args: object, **opts: object) -> None:
        self.stdout.write("→ Building app assets (buildassets)…")
        call_command("buildassets", verbosity=opts.get("verbosity", 1))

        self.stdout.write("→ Fetching vendor assets (fetchvendors)…")
        call_command("fetchvendors", verbosity=opts.get("verbosity", 1))

        self.stdout.write("→ Running collectstatic…")
        super().handle(*args, **opts)
