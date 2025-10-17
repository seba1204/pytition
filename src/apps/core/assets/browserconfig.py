from __future__ import annotations
from pathlib import Path
from .base import PipelineStep, Context
from .registry import register_step

@register_step("browserconfig", order=60)
class BrowserConfigStep(PipelineStep):
    """
    Génère browserconfig.xml pour Microsoft/Windows (tuiles).
    Requiert au moins une icône carrée 150x150 (on réutilise android-chrome-192x192).
    """
    def __init__(self, name: str):
        super().__init__("browserconfig")

    def run(self, ctx: Context) -> None:
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
        self.log(ctx, "Généré browserconfig.xml")
