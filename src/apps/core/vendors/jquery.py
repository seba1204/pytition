"""Vendor class for jQuery static files."""

from __future__ import annotations

from .base import Vendor
from .registry import register


@register("jquery")
class JQueryVendor(Vendor):
    """Fetch a single minified JS file from code.jquery.com."""

    def download_and_stage(self) -> None:
        """Download and stage jQuery static file."""
        url = f"https://code.jquery.com/jquery-{self.version}.min.js"
        keep = self._stage_from_file_url(url, "jquery.min.js")
        self._clean_stage_except(keep)
