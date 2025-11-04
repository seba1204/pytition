"""Pipeline step to generate browserconfig.xml."""

from __future__ import annotations

from pathlib import Path

from .base import Context, PipelineStep
from .registry import register_step


@register_step("browserconfig", order=60)
class BrowserConfigStep(PipelineStep):
    """
    Generates browserconfig.xml for Microsoft/Windows (tiles).

    Requires at least one 150x150 square icon (we reuse android-chrome-192x192).
    """

    def __init__(self, name: str):
        super().__init__("browserconfig")

    def run(self, ctx: Context) -> None:
        """Generate browserconfig.xml in <static_root>."""
        root = Path(ctx.static_root)
        xml = """<?xml version="1.0" encoding="utf-8"?>
<browserconfig>
  <msapplication>
    <tile>
      <square150x150logo src="/mstile-150x150.png"/>
      <TileColor>{tile_color}</TileColor>
    </tile>
  </msapplication>
</browserconfig>
""".format(tile_color=getattr(ctx.settings, "ASSETS_PWA_THEME_COLOR", "#000000"))
        (root / "browserconfig.xml").write_text(xml, encoding="utf-8")
        self.log(ctx, "browserconfig.xml generated.")
