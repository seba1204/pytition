"""Vendor class for Bootstrap Icons static files."""

from __future__ import annotations

from .base import Vendor
from .registry import register


@register("bootstrap-icons")
@register("bootstrap-icon")
@register("bi")
class BootstrapIconsVendor(Vendor):
    """Fetch Bootstrap Icons and stage minimal assets."""

    def _normalized_version(self) -> str:
        v = self.version.strip()
        return v[1:] if v.lower().startswith("v") else v

    def download_and_stage(self) -> None:
        """Download and stage Bootstrap Icons static files."""
        v = self._normalized_version()
        url = f"https://github.com/twbs/icons/releases/download/v{v}/bootstrap-icons-{v}.zip"
        keep = self._stage_from_zip_url(
            url,
            [
                ("bootstrap-icons.min.css", "css"),
                ("fonts/*.woff2", "css/fonts"),
                ("fonts/*.woff", "css/fonts"),
            ],
        )
        self._clean_stage_except(keep)
