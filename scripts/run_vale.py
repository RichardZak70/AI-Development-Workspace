#!/usr/bin/env python3
"""Run Vale with a pinned, self-managed installation.

Why this exists:
- We want prose linting to be enforceable locally via pre-commit.
- We don't want to rely on each developer having Vale installed.
- CI also runs Vale, but local feedback should be fast.

This script downloads a pinned Vale release, verifies it against the published
checksums, caches it under `.tools/vale/<version>/`, and then executes it.

The checks are applied using `.vale.ini`.
"""

from __future__ import annotations

import hashlib
import os
import platform
import shutil
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

VALE_VERSION = "3.13.0"
REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = REPO_ROOT / ".tools" / "vale" / VALE_VERSION


@dataclass(frozen=True)
class Asset:
    """Downloadable Vale release asset (filename + URL)."""

    filename: str
    url: str


def _detect_asset() -> Asset:
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "windows":
        filename = f"vale_{VALE_VERSION}_Windows_64-bit.zip"
    elif system == "linux":
        # GitHub Actions runners are amd64; most dev machines are too.
        if machine in {"aarch64", "arm64"}:
            filename = f"vale_{VALE_VERSION}_Linux_arm64.tar.gz"
        else:
            filename = f"vale_{VALE_VERSION}_Linux_64-bit.tar.gz"
    elif system == "darwin":
        if machine in {"arm64"}:
            filename = f"vale_{VALE_VERSION}_macOS_arm64.tar.gz"
        else:
            filename = f"vale_{VALE_VERSION}_macOS_64-bit.tar.gz"
    else:
        raise RuntimeError(f"Unsupported OS for Vale bootstrap: {platform.system()}")

    base = f"https://github.com/errata-ai/vale/releases/download/v{VALE_VERSION}"
    return Asset(filename=filename, url=f"{base}/{filename}")


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as resp:  # noqa: S310
        dest.write_bytes(resp.read())


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _expected_checksum(asset_filename: str) -> str:
    checksums_url = (
        f"https://github.com/errata-ai/vale/releases/download/v{VALE_VERSION}/"
        f"vale_{VALE_VERSION}_checksums.txt"
    )
    tmp = TOOLS_DIR / "_downloads" / f"vale_{VALE_VERSION}_checksums.txt"
    if not tmp.exists():
        _download(checksums_url, tmp)

    for line in tmp.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or "  " not in line:
            continue
        digest, name = line.split("  ", 1)
        if name.strip() == asset_filename:
            return digest.strip()

    raise RuntimeError(f"Checksum not found for asset: {asset_filename}")


def _extract_archive(archive: Path, install_dir: Path) -> Path:
    install_dir.mkdir(parents=True, exist_ok=True)

    if archive.suffix.lower() == ".zip":
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(install_dir)
    else:
        # tar.gz
        import tarfile

        with tarfile.open(archive, "r:gz") as tf:
            tf.extractall(install_dir)

    exe = install_dir / ("vale.exe" if os.name == "nt" else "vale")
    if not exe.exists():
        raise RuntimeError(f"Vale executable not found after extraction: {exe}")

    if os.name != "nt":
        exe.chmod(0o755)

    return exe


def ensure_vale() -> Path:
    """Ensure the pinned Vale binary is installed locally.

    Returns:
        Path to the Vale executable.
    """
    exe = TOOLS_DIR / ("vale.exe" if os.name == "nt" else "vale")
    if exe.exists():
        return exe

    asset = _detect_asset()
    downloads = TOOLS_DIR / "_downloads"
    archive = downloads / asset.filename

    _download(asset.url, archive)

    expected = _expected_checksum(asset.filename)
    actual = _sha256(archive)
    if actual.lower() != expected.lower():
        raise RuntimeError(
            f"Vale download checksum mismatch. expected={expected} actual={actual} file={archive}"
        )

    extracted_exe = _extract_archive(archive, TOOLS_DIR)

    # Best-effort cleanup of downloads to keep the repo tidy.
    shutil.rmtree(downloads, ignore_errors=True)

    return extracted_exe


def main() -> int:
    """Run Vale against README.md and docs/ using the repo's .vale.ini.

    Returns:
        Vale process exit code.
    """
    exe = ensure_vale()
    config = REPO_ROOT / ".vale.ini"
    if not config.exists():
        raise RuntimeError(".vale.ini not found at repo root")

    # Lint only the doc surfaces we care about.
    targets = ["README.md", "docs"]

    import subprocess

    proc = subprocess.run([str(exe), "--config", str(config), *targets], cwd=REPO_ROOT)
    return int(proc.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
