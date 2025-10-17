from __future__ import annotations
from .base import Vendor
from .registry import register

@register("bs-custom-file-input")
@register("bscustomfileinput")
class BsCustomFileInputVendor(Vendor):
    """Download bs-custom-file-input (Johann-S) from GitHub, fallback unpkg."""

    def download_and_stage(self) -> None:
        v = self.version
        urls = [
            f"https://github.com/Johann-S/bs-custom-file-input/archive/refs/tags/v{v}.zip",
            f"https://github.com/Johann-S/bs-custom-file-input/archive/refs/tags/{v}.zip",
        ]
        blob: bytes | None = None
        for url in urls:
            try:
                blob = self._http_get_bytes(url)
                tmp = self.stage_dir / "_zip"
                self._extract_zip_bytes(blob, tmp)
                root = next(tmp.iterdir())
                # chemins possibles
                candidates = list(root.rglob("dist/bs-custom-file-input.min.js")) + \
                             list(root.rglob("bs-custom-file-input.min.js"))
                if candidates:
                    self.stage_dir.mkdir(parents=True, exist_ok=True)
                    self._write_file(self.stage_dir / "bs-custom-file-input.min.js", candidates[0].read_bytes())
                    return
            except Exception:
                continue

        # Fallback: unpkg (npm)
        url = f"https://unpkg.com/bs-custom-file-input@{v}/dist/bs-custom-file-input.min.js"
        data = self._http_get_bytes(url)
        self.stage_dir.mkdir(parents=True, exist_ok=True)
        self._write_file(self.stage_dir / "bs-custom-file-input.min.js", data)
