from __future__ import annotations

import json
from pathlib import Path

from rjsmin import jsmin  # type: ignore[import-untyped]

from .base import Context, PipelineStep
from .registry import register_step


@register_step("scripts", order=30)
class ScriptsStep(PipelineStep):
    """
    Minifies .js files from assets/js -> <static_root>/js
    Generates a simple source map: starting mapping (col 0, line 0) + sourcesContent.
    (Sufficient for DevTools; if you want fine mappings, we can extend it.)
    """

    def __init__(self, name: str):
        super().__init__("scripts")

    def run(self, ctx: Context) -> None:
        src = Path(ctx.assets_dir) / "js"
        dst = Path(ctx.static_root) / "js"
        dst.mkdir(parents=True, exist_ok=True)

        if not src.exists():
            self.log(ctx, "No assets/js folder, step skipped.")
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

            # Minimal manual source map
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
            self.log(ctx, f"Minified JS + map: {rel} → {out_js.name}")
