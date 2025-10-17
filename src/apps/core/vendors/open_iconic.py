from __future__ import annotations

import shutil

from .base import Vendor
from .registry import register


@register("open-iconic")
class OpenIconicVendor(Vendor):
    """Fetch Open Iconic and install font files + CSS.

    Source: GitHub tags as a zip archive.
    Example URL: https://github.com/iconic/open-iconic/archive/refs/tags/1.1.1.zip
    """

    def download_and_stage(self) -> None:
        url = f"https://github.com/iconic/open-iconic/archive/refs/tags/{self.version}.zip"
        blob = self._http_get_bytes(url)
        tmp = self.stage_dir / "_zip"
        self._extract_zip_bytes(blob, tmp)
        # Zip unpacks to open-iconic-<version>/
        root = next(tmp.iterdir())  # e.g., open-iconic-1.1.1
        # Copy CSS, fonts and png to a consistent layout
        css_src = root / "font" / "css"
        fonts_src = root / "font" / "fonts"
        png_src = root / "png"
        css_dst = self.stage_dir / "css"
        fonts_dst = self.stage_dir / "fonts"
        png_dst = self.stage_dir / "png"
        if png_dst.exists():
            shutil.rmtree(png_dst)
        if css_dst.exists():
            shutil.rmtree(css_dst)
        if fonts_dst.exists():
            shutil.rmtree(fonts_dst)
        shutil.copytree(css_src, css_dst)
        shutil.copytree(fonts_src, fonts_dst)
        shutil.copytree(png_src, png_dst)
