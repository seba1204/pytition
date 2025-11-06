"""Vendor class for Popper.js static files."""

from __future__ import annotations

from typing import Final

from .base import Vendor
from .registry import register


def _major(version: str) -> int:
    head = version.strip().split(".", 1)[0]
    try:
        return int(head)
    except ValueError:
        return 0


V2 = 2


@register("popper")
@register("popperjs")
@register("popper.js")
class PopperVendor(Vendor):
    """Fetch Popper minified file for v1 or v2."""

    _V2_PATH: Final[str] = (
        "https://unpkg.com/@popperjs/core@{ver}/dist/umd/popper.min.js"
    )
    _V1_PATH: Final[str] = "https://unpkg.com/popper.js@{ver}/dist/umd/popper.min.js"

    def download_and_stage(self) -> None:
        """Download and stage Popper.js static file."""
        url = (
            self._V2_PATH.format(ver=self.version)
            if _major(self.version) >= V2
            else self._V1_PATH.format(ver=self.version)
        )
        keep = self._stage_from_file_url(url, "popper.min.js")
        self._clean_stage_except(keep)
