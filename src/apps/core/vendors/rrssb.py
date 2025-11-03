from __future__ import annotations

import shutil

from .base import Vendor
from .registry import register


@register("rrssb")
class RRSSBVendor(Vendor):
    """Download RRSSB (kni-labs/rrssb) from GitHub."""

    def download_and_stage(self) -> None:
        v = self.version
        urls = [
            f"https://github.com/kni-labs/rrssb/archive/refs/tags/v{v}.zip",
            f"https://github.com/kni-labs/rrssb/archive/refs/tags/{v}.zip",
        ]
        blob: bytes | None = None
        for url in urls:
            try:
                blob = self._http_get_bytes(url)
                tmp = self.stage_dir / "_zip"
                self._extract_zip_bytes(blob, tmp)
                break
            except Exception:
                continue
        if blob is None:
            raise RuntimeError(
                "Impossible de récupérer RRSSB (vérifie la version/tag)."
            )

        root = next((self.stage_dir / "_zip").iterdir())
        js_src = list(root.rglob("js/rrssb.min.js"))
        css_src = list(root.rglob("css/rrssb*.css"))

        if not js_src:
            raise RuntimeError("rrssb.min.js introuvable dans l’archive.")
        (self.stage_dir / "js").mkdir(parents=True, exist_ok=True)
        (self.stage_dir / "css").mkdir(parents=True, exist_ok=True)

        shutil.copy2(js_src[0], self.stage_dir / "js" / "rrssb.min.js")
        # Copie toutes les CSS rrssb*.css disponibles (minifiées ou non)
        for css in css_src:
            shutil.copy2(css, self.stage_dir / "css" / css.name)
