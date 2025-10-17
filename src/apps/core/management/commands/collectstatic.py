from __future__ import annotations

from django.contrib.staticfiles.management.commands.collectstatic import (
    Command as CollectStatic,
)
from django.core.management import call_command


class Command(CollectStatic):
    help = "Build assets, fetch vendor assets, puis exécute collectstatic."

    def handle(self, *args, **opts):
        self.stdout.write("→ Building app assets (buildassets)…")
        # On laisse passer la verbosité à la commande fille si nécessaire
        call_command("buildassets", verbosity=opts.get("verbosity", 1))

        self.stdout.write("→ Fetching vendor assets (fetchvendors)…")
        call_command("fetchvendors", verbosity=opts.get("verbosity", 1))

        self.stdout.write("→ Running collectstatic…")
        return super().handle(*args, **opts)
