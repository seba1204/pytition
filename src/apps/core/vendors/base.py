from __future__ import annotations

import hashlib
import io
import os
import shutil
import tarfile
import tomllib
import zipfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from urllib.request import Request, urlopen


@dataclass
class DownloadResult:
    vendor: str
    version: str
    dest_dir: Path
    changed: bool


class Vendor(ABC):
    """Base class for all vendors.

    Subclasses must implement `download_and_stage` to fetch and copy the needed
    files into `stage_dir`.
    """

    #: where vendor files live inside STATIC_ROOT
    vendor_root_name = "vendor"

    def __init__(self, name: str, version: str, static_root: Path) -> None:
        self.name = name
        self.version = version
        self.static_root = static_root
        self.vendor_root = static_root / self.vendor_root_name
        self.dest_dir = self.vendor_root / f"{name}-{version}"
        self.stage_dir = self.dest_dir.with_suffix(".staging")

    @abstractmethod
    def download_and_stage(self) -> None:
        """Download upstream artifacts and place final files under `stage_dir`.
        Must create all subfolders; may raise on failures.
        """

    # ----------------------- helpers -----------------------
    def _http_get_bytes(
        self, url: str, user_agent: str = "PytitionVendorFetcher/1.0"
    ) -> bytes:
        req = Request(url, headers={"User-Agent": user_agent})
        with urlopen(req) as resp:  # nosec - controlled URLs from subclasses
            return bytes(resp.read())

    def _extract_zip_bytes(self, blob: bytes, into: Path) -> None:
        into.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(blob)) as zf:
            zf.extractall(into)

    def _extract_tgz_bytes(self, blob: bytes, into: Path) -> None:
        into.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
            tf.extractall(into)

    def _write_file(self, where: Path, data: bytes) -> None:
        where.parent.mkdir(parents=True, exist_ok=True)
        with Path.open(where, "wb") as f:
            f.write(data)

    def _atomic_replace_from_stage(self) -> bool:
        """Replace `dest_dir` with `stage_dir` atomically. Returns True if changed."""
        if not self.stage_dir.exists():
            raise RuntimeError(
                "stage_dir does not exist; did you run download_and_stage()?"
            )
        # Compute fingerprint of stage
        stage_hash = self._hash_tree(self.stage_dir)
        current_hash = (
            self._hash_tree(self.dest_dir) if self.dest_dir.exists() else None
        )
        changed = stage_hash != current_hash
        if changed:
            tmp_backup = self.dest_dir.with_suffix(".bak")
            if tmp_backup.exists():
                shutil.rmtree(tmp_backup, ignore_errors=True)
            if self.dest_dir.exists():
                self.dest_dir.replace(tmp_backup)
            self.stage_dir.replace(self.dest_dir)
            if tmp_backup.exists():
                shutil.rmtree(tmp_backup, ignore_errors=True)
        else:
            shutil.rmtree(self.stage_dir, ignore_errors=True)
        return changed

    def _hash_tree(self, root: Path) -> str | None:
        if not root.exists():
            return None
        h = hashlib.sha256()
        for base, _dirs, files in os.walk(root):
            for fn in sorted(files):
                p = Path(base) / fn
                h.update(str(p.relative_to(root)).encode())
                with Path.open(p, "rb") as f:
                    while True:
                        chunk = f.read(1024 * 1024)
                        if not chunk:
                            break
                        h.update(chunk)
        return h.hexdigest()

    # ----------------------- public API -----------------------
    def ensure(self, *, force: bool = False) -> DownloadResult:
        self.vendor_root.mkdir(parents=True, exist_ok=True)
        if self.dest_dir.exists() and not force:
            return DownloadResult(self.name, self.version, self.dest_dir, changed=False)
        if self.stage_dir.exists():
            shutil.rmtree(self.stage_dir, ignore_errors=True)
        self.download_and_stage()
        changed = self._atomic_replace_from_stage()
        return DownloadResult(self.name, self.version, self.dest_dir, changed=changed)


# ----------------------- utilities -----------------------


def read_vendors_from_pyproject(pyproject_path: Path) -> dict[str, str]:
    with Path.open(pyproject_path, "rb") as f:
        cfg = tomllib.load(f)
    vendors = cfg.get("tool", {}).get("pytition", {}).get("vendors", {})
    # normalize keys to kebab-case strings
    return {str(k).replace("_", "-"): str(v) for k, v in vendors.items()}
