"""Vendor class for Ridiculously Responsive Social Sharing Buttons (RRSSB)."""

from __future__ import annotations

from .base import Vendor
from .registry import register


@register("rrssb")
class RRSSBVendor(Vendor):
    """Fetch rrssb zip and stage minified JS + CSS files."""

    def download_and_stage(self) -> None:
        """Download and stage RRSSB static files."""
        url = f"https://github.com/kni-labs/rrssb/archive/refs/tags/{self.version}.zip"
        keep = self._stage_from_zip_url(
            url, [("**/js/rrssb.min.js", "js"), ("**/css/rrssb*.css", "css")]
        )
        self._clean_stage_except(keep)
