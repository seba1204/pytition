"""Pipeline step to generate favicons and PWA icons."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import cairosvg  # type: ignore[import-untyped]
from PIL import Image

from .base import Context, PipelineStep
from .registry import register_step


@register_step("favicons", order=40)
class FaviconsStep(PipelineStep):
    """
    Generates a complete set of favicons and PWA icons from assets/logo.svg.

    (fallback assets/img/logo.png):
    - favicon.ico (16/32/48)
    - favicon-16x16.png, favicon-32x32.png, favicon-48x48.png
        - apple-touch-icon.png (180x180)
        - android-chrome-192x192.png, android-chrome-512x512.png
        - mstile-150x150.png
    - safari-pinned-tab.svg (copy of logo.svg)
    - site.webmanifest (alias of manifest.json)
    Output: <static_root> at the root.

    Translated with DeepL.com (free version)
    """

    def __init__(self, name: str):
        super().__init__("favicons")

    def _png_from_svg_or_png(
        self, logo_svg: Path, fallback_png: Path, size: int
    ) -> Image.Image:
        """Renders an RGBA PNG of size×size from the SVG or a fallback PNG."""
        if logo_svg.exists():
            png_bytes = cairosvg.svg2png(
                url=str(logo_svg), output_width=size, output_height=size
            )
            if png_bytes is None:
                raise ValueError("cairosvg.svg2png did not return bytes for SVG logo.")
            return Image.open(BytesIO(png_bytes)).convert("RGBA")
        if fallback_png.exists():
            return (
                Image.open(fallback_png)
                .convert("RGBA")
                .resize((size, size), Image.Resampling.LANCZOS)
            )
        raise FileNotFoundError(
            f"Neither SVG logo ({logo_svg}) nor fallback PNG ({fallback_png}) found."
        )

    def _save_multi_ico(self, images: list[Image.Image], out_path: Path) -> None:
        """Saves a multi-resolution ICO file from a list of PNG images."""
        buf = BytesIO()
        # Pillow can write a multi-resolution ICO if you pass the list of sizes.
        images[0].save(buf, format="ICO", sizes=[im.size for im in images])
        out_path.write_bytes(buf.getvalue())

    def run(self, ctx: Context) -> None:
        """Generate favicons and PWA icons in <static_root>."""
        root = Path(ctx.static_root)
        root.mkdir(parents=True, exist_ok=True)

        assets_root = Path(ctx.assets_dir)
        logo_svg = assets_root / "logo.svg"
        fallback_png = assets_root / "img" / "logo.png"

        # --- Configurable sizes / default values ---
        png_fav_sizes = getattr(ctx.settings, "ASSETS_FAVICON_SIZES", [16, 32, 48])
        apple_size = getattr(ctx.settings, "ASSETS_APPLE_TOUCH_SIZE", 180)
        android_sizes = getattr(ctx.settings, "ASSETS_ANDROID_ICON_SIZES", [192, 512])
        ms_tile_size = 150  # standard pour browserconfig.xml
        # --------------------------------------------------

        # 1) favicon-XX.png (16/32/48)
        png_outputs = []
        for s in png_fav_sizes:
            img = self._png_from_svg_or_png(logo_svg, fallback_png, s)
            out = root / f"favicon-{s}x{s}.png"
            img.save(out, format="PNG")
            png_outputs.append(img)
            self.log(ctx, f"{out.name} generated.")

        # 2) multi-resolution favicon.ico (16/32/48)
        #    Reconstruction is performed based on previous images to ensure consistency.
        if not png_outputs:
            # If user cleared ASSETS_FAVICON_SIZES, guarantee at least 16/32
            png_outputs = [
                self._png_from_svg_or_png(logo_svg, fallback_png, s)
                for s in (16, 32, 48)
            ]
        self._save_multi_ico(png_outputs, root / "favicon.ico")
        self.log(ctx, "favicon.ico generated.")

        # 3) Apple touch icon (180x180)
        apple = self._png_from_svg_or_png(logo_svg, fallback_png, apple_size)
        apple.save(root / "apple-touch-icon.png", format="PNG")
        self.log(ctx, "apple-touch-icon.png generated.")

        # 4) Android/Chrome icons (192, 512)
        for s in android_sizes:
            img = self._png_from_svg_or_png(logo_svg, fallback_png, s)
            img.save(root / f"android-chrome-{s}x{s}.png", format="PNG")
            self.log(ctx, f"android-chrome-{s}x{s}.png generated.")

        # 5) Microsoft tile (150x150)
        mstile = self._png_from_svg_or_png(logo_svg, fallback_png, ms_tile_size)
        mstile.save(root / f"mstile-{ms_tile_size}x{ms_tile_size}.png", format="PNG")
        self.log(ctx, f"mstile-{ms_tile_size}x{ms_tile_size}.png generated.")

        # 6) Safari pinned tab (copy of source SVG)
        #    Ideally monochrome; here we copy as is to avoid risky conversion.
        if logo_svg.exists():
            (root / "safari-pinned-tab.svg").write_bytes(logo_svg.read_bytes())
            self.log(ctx, "safari-pinned-tab.svg (copy) generated.")
