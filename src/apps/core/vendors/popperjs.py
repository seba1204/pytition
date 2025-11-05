"""Vendor class for Popper.js static files."""

from __future__ import annotations

from typing import Final

from .base import Vendor
from .registry import register


def _major(version: str) -> int:
    """Extract the major version number from a version string."""
    head = version.strip().split(".", 1)[0]
    try:
        return int(head)
    except ValueError:
        head = head.lstrip("vV")
        return int(head.split("-", 1)[0])


class PopperVendor(Vendor):
    """Vendor class for Popper.js static files."""

    _V1_PATH: Final[str] = "https://unpkg.com/popper.js@{ver}/dist/umd/popper.min.js"
    _V2_PATH: Final[str] = (
        "https://unpkg.com/@popperjs/core@{ver}/dist/umd/popper.min.js"
    )

    def download_and_stage(self) -> None:
        """Download and stage Popper.js into `stage_dir`."""

        V2_MAJOR = 2

        maj = _major(self.version)
        if maj >= V2_MAJOR:
            url = self._V2_PATH.format(ver=self.version)
        else:
            url = self._V1_PATH.format(ver=self.version)

        blob = self._http_get_bytes(url)

        self.stage_dir.mkdir(parents=True, exist_ok=True)
        self._write_file(self.stage_dir / "popper.min.js", blob)


# Support multiple names
register("popper")(PopperVendor)
register("popperjs")(PopperVendor)
register("popper.js")(PopperVendor)
