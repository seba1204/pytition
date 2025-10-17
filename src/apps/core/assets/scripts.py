from __future__ import annotations

import json
from pathlib import Path

from rjsmin import jsmin

from .base import Context, PipelineStep
from .registry import register_step


@register_step("scripts", order=30)
class ScriptsStep(PipelineStep):
    """
    Minifie les .js de assets/js -> <static_root>/js
    Génère une source map simple: mapping de départ (col 0, ligne 0) + sourcesContent.
    (Suffisant pour DevTools; si tu veux des mappings fins, on pourra l'étendre.)
    """

    def __init__(self, name: str):
        super().__init__("scripts")

    def run(self, ctx: Context) -> None:
        src = Path(ctx.assets_dir) / "js"
        dst = Path(ctx.static_root) / "js"
        dst.mkdir(parents=True, exist_ok=True)

        if not src.exists():
            self.log(ctx, "Aucun dossier assets/js, étape ignorée.")
            return

        for path in src.rglob("*.js"):
            rel = path.relative_to(src)
            code = path.read_text(encoding="utf-8")
            minified = jsmin(code)
            out_js = dst / rel.with_suffix(".min.js")
            out_js.parent.mkdir(parents=True, exist_ok=True)
            out_js.write_text(
                str(minified) + "\n//# sourceMappingURL=" + out_js.name + ".map",
                encoding="utf-8",
            )

            # Source map minimale manuelle
            source_map = {
                "version": 3,
                "file": out_js.name,
                "sources": [str(rel)],
                "sourcesContent": [code],
                "mappings": ";",  # vide (pas de mapping précis)
            }
            (dst / (out_js.name + ".map")).write_text(
                json.dumps(source_map, indent=2), encoding="utf-8"
            )
            self.log(ctx, f"Minifié JS + map: {rel} → {out_js.name}")
