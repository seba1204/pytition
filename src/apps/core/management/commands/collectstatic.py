from __future__ import annotations
from django.contrib.staticfiles.management.commands.collectstatic import Command as CollectStatic
from django.core.management import call_command

class Command(CollectStatic):
    help = "Fetch vendor assets into STATIC_ROOT/vendor then run collectstatic."

    def handle(self, *args, **opts):
        # Allow passthrough of verbosity, etc. to subcommand as needed
        self.stdout.write("→ Fetching vendor assets (fetchvendors)…")
        call_command("fetchvendors")
        self.stdout.write("→ Running collectstatic…")
        return super().handle(*args, **opts)