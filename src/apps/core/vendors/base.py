"""Base classes and utilities for vendor management."""

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
    """Result of a vendor download operation."""

    vendor: str
    version: str
    dest_dir: Path
    changed: bool


class Vendor(ABC):
    """
    Base class for all vendors.

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
        """
        Download upstream artifacts and place final files under `stage_dir`.

        Must create all subfolders; may raise on failures.
        """

    # ----------------------- helpers -----------------------
    def _http_get_bytes(
        self, url: str, user_agent: str = "PytitionVendorFetcher/1.0"
    ) -> bytes:
        """Fetch bytes from a URL with a custom User-Agent."""
        req = Request(url, headers={"User-Agent": user_agent})
        with urlopen(req) as resp:  # nosec - controlled URLs from subclasses
            return bytes(resp.read())

    def _extract_zip_bytes(self, blob: bytes, into: Path) -> None:
        """Extract a ZIP archive from bytes into the given directory."""
        into.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(blob)) as zf:
            zf.extractall(into)

    def _extract_tgz_bytes(self, blob: bytes, into: Path) -> None:
        """Extract a TGZ archive from bytes into the given directory."""
        into.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
            tf.extractall(into)

    def _write_file(self, where: Path, data: bytes) -> None:
        """Write bytes to a file, creating parent directories as needed."""
        where.parent.mkdir(parents=True, exist_ok=True)
        with Path.open(where, "wb") as f:
            f.write(data)

    # ----------------------- generic staging helpers -----------------------
    def _stage_from_zip_url(self, url: str, rules: list[tuple[str, str]]) -> set[Path]:
        """
        Download a zip from ``url`` and stage selected files/dirs.

        Parameters
        ----------
        url : str
            HTTPS URL to a ``.zip`` archive.
        rules : list of tuple
            (src_glob, dest_rel_dir) entries; glob is evaluated relative to the
            single top-level directory of the unpacked archive.

        Returns
        -------
        set of Path
            Absolute paths created under stage_dir.
        """
        blob = self._http_get_bytes(url)
        zip_root = self.stage_dir / "_zip"
        self._extract_zip_bytes(blob, zip_root)
        try:
            archive_root = next(p for p in zip_root.iterdir() if p.is_dir())
        except StopIteration as exc:
            raise RuntimeError(
                "Unexpected archive structure (no top-level dir)."
            ) from exc

        keep: set[Path] = set()
        for src_glob, dest_rel in rules:
            dest_dir = (self.stage_dir / dest_rel).resolve()
            dest_dir.mkdir(parents=True, exist_ok=True)
            matches = list(archive_root.rglob(src_glob))
            if not matches:
                continue
            for m in matches:
                if m.is_dir():
                    for sub in m.rglob("*"):
                        if sub.is_file():
                            rel = sub.relative_to(m)
                            dst = dest_dir / rel
                            dst.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(sub, dst)
                            keep.add(dst.resolve())
                else:
                    dst = dest_dir / m.name
                    shutil.copy2(m, dst)
                    keep.add(dst.resolve())
        return keep

    def _stage_from_file_url(self, url: str, dest_rel: str) -> set[Path]:
        """Download a single file from ``url`` into ``stage_dir/dest_rel``."""
        data = self._http_get_bytes(url)
        dst = (self.stage_dir / dest_rel).resolve()
        dst.parent.mkdir(parents=True, exist_ok=True)
        self._write_file(dst, data)
        return {dst}

    def _clean_stage_except(self, keep: set[Path]) -> None:
        """Remove everything from ``stage_dir`` except the keep set."""
        stage_root = self.stage_dir.resolve()
        keep_with_parents: set[Path] = set(keep)
        for p in list(keep):
            cur = p.parent
            while cur != stage_root and stage_root in cur.parents:
                keep_with_parents.add(cur)
                cur = cur.parent
        keep_with_parents.add(stage_root)
        for p in sorted(stage_root.rglob("*")):
            try:
                rp = p.resolve()
            except FileNotFoundError:
                continue
            if rp.is_file() and rp not in keep_with_parents:
                rp.unlink()
        for d in sorted(
            (p for p in stage_root.rglob("*") if p.is_dir()),
            key=lambda x: len(x.parts),
            reverse=True,
        ):
            try:
                next(d.iterdir())
            except StopIteration:
                if d not in keep_with_parents:
                    d.rmdir()
            except FileNotFoundError:
                continue

    def _atomic_replace_from_stage(self) -> bool:
        """
        Replace `dest_dir` with `stage_dir` atomically.

        Returns True if changed.
        """
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
        """
        Compute a SHA256 hash of all files under root.

        Returns None if root missing.
        """
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
        """
        Ensure the vendor is downloaded into `dest_dir`.

        Returns DownloadResult.
        """
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
    """Read vendor versions from pyproject.toml."""
    with Path.open(pyproject_path, "rb") as f:
        cfg = tomllib.load(f)
    vendors = cfg.get("tool", {}).get("pytition", {}).get("vendors", {})
    # normalize keys to kebab-case strings
    return {str(k).replace("_", "-"): str(v) for k, v in vendors.items()}
