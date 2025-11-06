"""Vendor class for jQuery Smart Wizard static files."""

from __future__ import annotations

from .base import Vendor
from .registry import register


@register("smartwizard")
@register("jquery-smart-wizard")
class SmartWizardVendor(Vendor):
    """Fetch SmartWizard zip and stage JS+CSS minimal set."""

    def download_and_stage(self) -> None:
        """Download and stage SmartWizard static files."""
        url = f"https://github.com/techlab/SmartWizard/archive/refs/tags/v{self.version}.zip"
        keep = self._stage_from_zip_url(
            url,
            [
                ("dist/js/jquery.smartWizard.min.js", "js"),
                ("dist/css/smart_wizard*.css", "css"),
            ],
        )
        self._clean_stage_except(keep)
