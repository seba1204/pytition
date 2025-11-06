"""Vendor class for bs-custom-file-input static files."""

from __future__ import annotations

from .base import Vendor
from .registry import register


@register("bs-custom-file-input")
@register("bscustomfileinput")
class BsCustomFileInputVendor(Vendor):
    """Fetch bs-custom-file-input from unpkg (min JS only)."""

    def download_and_stage(self) -> None:
        """Download and stage bs-custom-file-input static file."""
        url = f"https://unpkg.com/bs-custom-file-input@{self.version}/dist/bs-custom-file-input.min.js"
        keep = self._stage_from_file_url(url, "bs-custom-file-input.min.js")
        self._clean_stage_except(keep)
