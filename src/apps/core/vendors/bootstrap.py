"""Vendor class for Bootstrap static files."""

from __future__ import annotations

import shutil

from .base import Vendor
from .registry import register


@register("bootstrap")
class BootstrapVendor(Vendor):
    """
    Fetch Bootstrap dist zip for a given version and install css/js maps.

    Source: GitHub releases – "bootstrap-<version>-dist.zip" assets.
    Example URL: https://github.com/twbs/bootstrap/releases/download/v5.3.3/bootstrap-5.3.3-dist.zip
    """

    def download_and_stage(self) -> None:
        """Download and stage Bootstrap files into `stage_dir`."""
        url = f"https://github.com/twbs/bootstrap/releases/download/v{self.version}/bootstrap-{self.version}-dist.zip"
        blob = self._http_get_bytes(url)
        tmp = self.stage_dir / "_zip"
        self._extract_zip_bytes(blob, tmp)
        # In the dist zip, content is under "bootstrap-<ver>-dist/"
        root = next(tmp.iterdir())
        # Copy selected folders into final layout
        # Final structure: vendor/bootstrap/{css,js}
        for folder in ("css", "js"):
            src = root / folder
            dst = self.stage_dir / folder
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
