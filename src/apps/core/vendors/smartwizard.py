from __future__ import annotations

import shutil

from .base import Vendor
from .registry import register


@register("smartwizard")
@register("jquery-smart-wizard")
class SmartWizardVendor(Vendor):
    """Download jQuery Smart Wizard 4 from GitHub (techlab/SmartWizard)."""

    def download_and_stage(self) -> None:
        v = self.version
        urls = [
            f"https://github.com/techlab/SmartWizard/archive/refs/tags/v{v}.zip",
            f"https://github.com/techlab/SmartWizard/archive/refs/tags/{v}.zip",
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
                "Impossible de récupérer SmartWizard (vérifie la version/tag)."
            )

        root = next((self.stage_dir / "_zip").iterdir())
        js_src = list(root.rglob("dist/js/jquery.smartWizard.min.js"))
        css_src = list(root.rglob("dist/css/smart_wizard*.css"))
        if not js_src:
            raise RuntimeError("Fichier JS SmartWizard introuvable dans l’archive.")
        js_dst = self.stage_dir / "js"
        css_dst = self.stage_dir / "css"
        js_dst.mkdir(parents=True, exist_ok=True)
        css_dst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(js_src[0], js_dst / "jquery.smartWizard.min.js")
        for css in css_src:
            shutil.copy2(css, css_dst / css.name)
