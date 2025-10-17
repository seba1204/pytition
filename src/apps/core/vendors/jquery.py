from __future__ import annotations

from .base import Vendor
from .registry import register


@register("jquery")
class JQueryVendor(Vendor):
    """Télécharge jQuery depuis code.jquery.com et le place à la racine du vendor."""

    def download_and_stage(self) -> None:
        url = f"https://code.jquery.com/jquery-{self.version}.min.js"
        js = self._http_get_bytes(url)
        self.stage_dir.mkdir(parents=True, exist_ok=True)
        self._write_file(self.stage_dir / "jquery.min.js", js)
