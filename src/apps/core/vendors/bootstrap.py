"""Vendor class for Bootstrap static files."""

from __future__ import annotations

from .base import Vendor
from .registry import register


@register("bootstrap")
class BootstrapVendor(Vendor):
    """Fetch Bootstrap dist and stage minimal assets."""

    def download_and_stage(self) -> None:
        """Download and stage Bootstrap static files."""
        url = f"https://github.com/twbs/bootstrap/releases/download/v{self.version}/bootstrap-{self.version}-dist.zip"
        keep = self._stage_from_zip_url(
            url,
            [
                ("css/bootstrap.min.css", "css"),
                ("css/bootstrap.min.css.map", "css"),
                ("js/bootstrap.bundle.min.js", "js"),
                ("js/bootstrap.bundle.min.js.map", "js"),
            ],
        )
        self._clean_stage_except(keep)
