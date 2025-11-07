"""Vendor class for Open Iconic static files."""

from __future__ import annotations

from .base import Vendor
from .registry import register


@register("open-iconic")
class OpenIconicVendor(Vendor):
    """Fetch Open Iconic zip and stage minimal CSS+fonts."""

    def download_and_stage(self) -> None:
        """Download and stage Open Iconic static files."""
        url = f"https://github.com/iconic/open-iconic/archive/refs/tags/{self.version}.zip"
        keep = self._stage_from_zip_url(
            url,
            [
                ("font/open-iconic-bootstrap.min.css", "css"),
                ("font/fonts/*.woff2", "fonts"),
                ("font/fonts/*.woff", "fonts"),
            ],
        )
        self._clean_stage_except(keep)
