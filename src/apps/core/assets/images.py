"""Pipeline step to process images: convert PNG/JPEG to WebP and copy SVGs."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, UnidentifiedImageError

from .base import Context, PipelineStep
from .registry import register_step


@register_step("images", order=10)
class ImagesStep(PipelineStep):
    """
    Converts PNG/JPEG to WebP in 3 sizes.

    Copies SVG files as-is.
    Source: assets/img/**/* -> <static_root>/img/
    """

    def __init__(self, name: str):
        super().__init__("images")

    def run(self, ctx: Context) -> None:
        """Process images from assets/img to <static_root>/img."""
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
            self.log(ctx, "No assets/img folder, step skipped.")
            return

        for path in src.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(src)
            if path.suffix.lower() == ".svg":
                out = dst / rel
                if out.exists():
                    self.log(ctx, f"SVG already exists, skipped: {rel}")
                    continue
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(path.read_bytes())
                self.log(ctx, f"SVG copied: {rel}")
                continue

            try:
                with Image.open(path) as im:
                    im.load()
            except UnidentifiedImageError:
                out = dst / rel
                if out.exists():
                    self.log(ctx, f"Raw copy already exists, skipped: {rel}")
                    continue
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(path.read_bytes())
                self.log(ctx, f"Raw copy {rel}")
                continue

            if im.mode in ("P", "LA", "RGBA"):
                bg = Image.new("RGBA", im.size, (255, 255, 255, 0))
                bg.paste(im, (0, 0))
                im = bg.convert("RGBA")
            else:
                im = im.convert("RGB")

            for label, width in sizes.items():
                out = (dst / rel).with_suffix(f".{label}.webp")
                if out.exists():
                    self.log(
                        ctx,
                        f"WebP {label} already exists, skipped"
                        ": {rel.with_suffix('.webp')}",
                    )
                    continue
                im_out = im.copy()
                im_out.thumbnail((width, width * 10_000), Image.Resampling.LANCZOS)
                out.parent.mkdir(parents=True, exist_ok=True)
                im_out.save(out, format="WEBP", quality=quality, method=6)
                self.log(ctx, f"WebP {label} → {rel.with_suffix('.webp')} (w≤{width})")
