from __future__ import annotations

from pathlib import Path

from cssmin import cssmin

from .base import Context, PipelineStep
from .registry import register_step


@register_step("styles", order=20)
class StylesStep(PipelineStep):
    """
    Minifie les .css de assets/css -> <static_root>/css
    (Ignore .scss : compilation hors scope demandé)
    """

    def __init__(self, name: str):
        super().__init__("styles")

    def run(self, ctx: Context) -> None:
        src = Path(ctx.assets_dir) / "css"
        dst = Path(ctx.static_root) / "css"
        dst.mkdir(parents=True, exist_ok=True)

        if not src.exists():
            self.log(ctx, "Aucun dossier assets/css, étape ignorée.")
            return

        for path in src.rglob("*.css"):
            rel = path.relative_to(src)
            out = dst / rel.with_suffix(".min.css")
            out.parent.mkdir(parents=True, exist_ok=True)
            minified = cssmin(path.read_text(encoding="utf-8"))
            out.write_text(minified, encoding="utf-8")
            self.log(ctx, f"Minifié CSS: {rel} → {out.name}")
