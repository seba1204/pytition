from __future__ import annotations

from pathlib import Path

from PIL import Image, UnidentifiedImageError

from .base import Context, PipelineStep
from .registry import register_step


@register_step("images", order=10)
class ImagesStep(PipelineStep):
    """
    Convertit PNG/JPEG en WebP dans 3 tailles.
    Copie les SVG tels quels.
    Source: assets/img/**/* -> <static_root>/img/
    """

    def __init__(self, name: str):
        super().__init__("images")

    def run(self, ctx: Context) -> None:
        src = Path(ctx.assets_dir) / "img"
        dst = Path(ctx.static_root) / "img"
        dst.mkdir(parents=True, exist_ok=True)

        sizes = getattr(
            ctx.settings,
            "ASSETS_IMAGE_SIZES",
            {"thumbnail": 200, "standard": 800, "retina": 1600},
        )
        quality = getattr(ctx.settings, "ASSETS_IMAGE_QUALITY", 85)

        if not src.exists():
            self.log(ctx, "Aucun dossier assets/img, étape ignorée.")
            return

        for path in src.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(src)
            if path.suffix.lower() == ".svg":
                # copie brute
                out = dst / rel
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(path.read_bytes())
                self.log(ctx, f"Copié SVG: {rel}")
                continue

            try:
                with Image.open(path) as im:
                    im.load()
            except UnidentifiedImageError:
                # copie brute si format non géré par Pillow
                out = dst / rel
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(path.read_bytes())
                self.log(ctx, f"Copié (brut) {rel}")
                continue

            # normalisation en RGB (WebP ne gère pas tous les modes)
            if im.mode in ("P", "LA", "RGBA"):
                bg = Image.new("RGBA", im.size, (255, 255, 255, 0))
                bg.paste(im, (0, 0))
                im = bg.convert("RGBA")
            else:
                im = im.convert("RGB")

            for label, width in sizes.items():
                im_out = im.copy()
                im_out.thumbnail((width, width * 10_000), Image.Resampling.LANCZOS)
                out = (dst / rel).with_suffix(f".{label}.webp")
                out.parent.mkdir(parents=True, exist_ok=True)
                im_out.save(out, format="WEBP", quality=quality, method=6)
                self.log(ctx, f"WebP {label} → {rel.with_suffix('.webp')} (w≤{width})")
