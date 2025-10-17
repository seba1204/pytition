from __future__ import annotations

from typing import Final

from .base import Vendor
from .registry import register


def _major(version: str) -> int:
    """Retourne la major version (1 pour 1.x.y, 2 pour 2.x.y, etc.)."""
    # Version tolérante: coupe sur le 1er point/trait
    head = version.strip().split(".", 1)[0]
    try:
        return int(head)
    except ValueError:
        # Ex: 'v2.11.8' ou formats non attendus
        head = head.lstrip("vV")
        return int(head.split("-", 1)[0])


class PopperVendor(Vendor):
    """Télécharge Popper (v1 = popper.js, v2 = @popperjs/core) via unpkg.

    Chemin de sortie (sans sous-dossier):
      STATIC_ROOT/vendor/popper-<version>/popper.min.js
    """

    _V1_PATH: Final[str] = "https://unpkg.com/popper.js@{ver}/dist/umd/popper.min.js"
    _V2_PATH: Final[str] = (
        "https://unpkg.com/@popperjs/core@{ver}/dist/umd/popper.min.js"
    )

    def download_and_stage(self) -> None:
        maj = _major(self.version)
        if maj >= 2:
            url = self._V2_PATH.format(ver=self.version)
        else:
            url = self._V1_PATH.format(ver=self.version)

        blob = self._http_get_bytes(url)

        # Pas de sous-dossier "js": on met le fichier à la racine du vendor versionné
        self.stage_dir.mkdir(parents=True, exist_ok=True)
        self._write_file(self.stage_dir / "popper.min.js", blob)


# Enregistrer plusieurs alias utiles
register("popper")(PopperVendor)
register("popperjs")(PopperVendor)
register("popper.js")(PopperVendor)
