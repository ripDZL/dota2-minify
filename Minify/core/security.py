"""Shared security primitives for untrusted mod/download/archive inputs."""

from __future__ import annotations

import hashlib
import os
import stat
import tarfile
import tempfile
import zipfile
import zlib
from collections.abc import Callable, Iterable

ARCHIVE_MAX_ENTRIES = 4096
ARCHIVE_MAX_FILE_BYTES = 2 * 1024 * 1024 * 1024
ARCHIVE_MAX_TOTAL_BYTES = 4 * 1024 * 1024 * 1024
ARCHIVE_MAX_COMPRESSION_RATIO = 250.0
D2PFX_MAX_MANIFEST_BYTES = 8 * 1024 * 1024

# Digests are from the pinned upstream GitHub release assets. Keys are exact
# archive basenames so a version/architecture change fails closed until reviewed.
EXPECTED_DOWNLOAD_SHA256 = {
    # ValveResourceFormat 20.0
    "cli-linux-arm.zip": "5348f5b6cc2eb5686f15c19b07803b3723977b72b0efe6df5e22baa987279f48",
    "cli-linux-arm64.zip": "adcfeac823e25ebdaebe0b6c4b3132546afa3978d23fca37bb522da1fe5cb2e5",
    "cli-linux-x64.zip": "3e8af47cd6ce52e8068904f2aa1dda23c56a6b96a8310b25090f0711cda76a8a",
    "cli-macos-arm64.zip": "fa3fc51ab8ed8c96899a64cf8977c2c4810342605868f37044e85a412ff4e0cd",
    "cli-macos-x64.zip": "9b430e8233fa498c34c00cf5cf4da48d854c8f255b1208557861802d9e16a19c",
    "cli-windows-arm64.zip": "df2a52372fee1ce8284abd2cd8a09f65e7259778290b5facfcfa07ef75f4ea1a",
    "cli-windows-x64.zip": "d32ab327b8bbb42a2528866afb03bb582bdb779d0005488da32b90292afd3ff5",
    # ripgrep 15.2.0
    "ripgrep-15.2.0-aarch64-apple-darwin.tar.gz": "3750b2e93f37e0c692657da574d7019a101c0084da05a790c83fd335bad973e4",
    "ripgrep-15.2.0-x86_64-apple-darwin.tar.gz": "af7825fcc69a2afc7a7aea55fc9af90e26421d8f20fe59df32e233c0b8a231c1",
    "ripgrep-15.2.0-aarch64-unknown-linux-gnu.tar.gz": "a740b91c82eaf9914cfedd353572f2791cbe0162c84101ee0951058f4dcbc90d",
    "ripgrep-15.2.0-armv7-unknown-linux-gnueabihf.tar.gz": "d859589734d9d802107ad9eff6a78cfd9b0080d2fecb0ad8772605b35e373199",
    "ripgrep-15.2.0-s390x-unknown-linux-gnu.tar.gz": "b61a442344f0591321960def6adb8c828b68a448301d1ed93959656fcd3b79c2",
    "ripgrep-15.2.0-x86_64-unknown-linux-musl.tar.gz": "33e15bcf1624b25cdd2a55813a47a2f95dbe126268203e76aa6a585d1e7b149c",
    "ripgrep-15.2.0-i686-pc-windows-msvc.zip": "9bf73bdb3fda9ad4b0235e1295b02c717031c986afa4d7c05dd0af8b74010a95",
    "ripgrep-15.2.0-x86_64-pc-windows-msvc.zip": "71b2fef860abe467217a538ff31de02f5258807c0129f771846f87bd029aafc5",
}


def sha256_file(path: str, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_expected_download(path: str, source_url: str = "") -> str:
    """Verify a freshly downloaded pinned dependency archive.

    Unknown asset names fail closed: adding/updating an auto-downloaded binary
    requires an explicit digest review in this file.
    """
    basename = os.path.basename(path) or os.path.basename(source_url)
    expected = EXPECTED_DOWNLOAD_SHA256.get(basename)
    if not expected:
        try:
            os.remove(path)
        except OSError:
            pass
        raise ValueError(f"No trusted SHA-256 is configured for dependency archive {basename!r}.")
    actual = sha256_file(path)
    if actual.casefold() != expected.casefold():
        try:
            os.remove(path)
        except OSError:
            pass
        raise ValueError(
            f"SHA-256 mismatch for dependency archive {basename!r}: expected {expected}, got {actual}."
        )
    return actual


def safe_relative_path(value: str) -> str:
    """Normalize an untrusted archive/VPK path and reject filesystem escapes."""
    raw = str(value or "")
    if "\x00" in raw:
        raise ValueError("Path contains a NUL byte.")
    raw = raw.strip().strip('"').strip("'").replace("\\", "/")
    if not raw:
        raise ValueError("Path is empty.")
    if raw.startswith("/") or raw.startswith("//"):
        raise ValueError(f"Absolute path is not allowed: {value!r}")
    first = raw.split("/", 1)[0]
    if ":" in first:
        raise ValueError(f"Drive-qualified path is not allowed: {value!r}")

    parts: list[str] = []
    for part in raw.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            raise ValueError(f"Parent traversal is not allowed: {value!r}")
        parts.append(part)
    if not parts:
        raise ValueError("Path resolves to an empty location.")
    return "/".join(parts)


def confined_destination(root: str, relative: str) -> tuple[str, str]:
    normalized = safe_relative_path(relative)
    root_abs = os.path.abspath(root)
    root_real = os.path.realpath(root_abs)
    destination = os.path.abspath(os.path.join(root_abs, *normalized.split("/")))
    # Resolve existing symlink components too. This matters when extracting into
    # a directory that an attacker can partially influence before extraction.
    destination_real = os.path.realpath(destination)
    try:
        common = os.path.commonpath((root_real, destination_real))
    except ValueError as exc:
        raise ValueError(f"Path escapes destination root: {relative!r}") from exc
    if common != root_real:
        raise ValueError(f"Path escapes destination root: {relative!r}")
    return normalized, destination


def bounded_zlib_decompress(
    compressed: bytes,
    *,
    max_output: int = D2PFX_MAX_MANIFEST_BYTES,
    wbits_options: Iterable[int] = (-zlib.MAX_WBITS, zlib.MAX_WBITS, zlib.MAX_WBITS | 16),
) -> bytes:
    """Decompress while bounding memory before an oversized payload is materialized."""
    if max_output < 1:
        raise ValueError("max_output must be positive")
    last_error: Exception | None = None
    for wbits in wbits_options:
        decompressor = zlib.decompressobj(wbits)
        try:
            decoded = decompressor.decompress(compressed, max_output + 1)
            if len(decoded) > max_output or decompressor.unconsumed_tail:
                raise ValueError("The decompressed payload exceeds the safety limit.")
            decoded += decompressor.flush(max_output + 1 - len(decoded))
            if len(decoded) > max_output:
                raise ValueError("The decompressed payload exceeds the safety limit.")
            if not decompressor.eof:
                raise ValueError("The compressed payload is truncated or exceeds the safety limit.")
            return decoded
        except zlib.error as exc:
            last_error = exc
            continue
    raise ValueError("The compressed payload could not be decompressed.") from last_error


def _zip_is_symlink(info: zipfile.ZipInfo) -> bool:
    mode = (info.external_attr >> 16) & 0xFFFF
    return stat.S_ISLNK(mode)


def _validate_zip_infos(
    infos: list[zipfile.ZipInfo],
    *,
    max_entries: int,
    max_file_bytes: int,
    max_total_bytes: int,
    max_ratio: float,
) -> None:
    if len(infos) > max_entries:
        raise ValueError(f"Archive contains more than {max_entries} entries.")
    total = 0
    for info in infos:
        if _zip_is_symlink(info):
            raise ValueError(f"ZIP symlinks are not allowed: {info.filename}")
        safe_relative_path(info.filename)
        if info.is_dir():
            continue
        size = int(info.file_size)
        compressed = int(info.compress_size)
        if size < 0 or compressed < 0:
            raise ValueError(f"Invalid ZIP size metadata: {info.filename}")
        if size > max_file_bytes:
            raise ValueError(f"ZIP entry exceeds the per-file safety limit: {info.filename}")
        total += size
        if total > max_total_bytes:
            raise ValueError("ZIP archive exceeds the total extracted-size safety limit.")
        if size and compressed == 0:
            raise ValueError(f"ZIP entry has an invalid zero compressed size: {info.filename}")
        if compressed and size / compressed > max_ratio:
            raise ValueError(f"ZIP entry has a suspicious compression ratio: {info.filename}")


def safe_extract_zip(
    zip_path: str,
    target: str,
    *,
    target_file: str | None = None,
    max_entries: int = ARCHIVE_MAX_ENTRIES,
    max_file_bytes: int = ARCHIVE_MAX_FILE_BYTES,
    max_total_bytes: int = ARCHIVE_MAX_TOTAL_BYTES,
    max_ratio: float = ARCHIVE_MAX_COMPRESSION_RATIO,
    predicate: Callable[[zipfile.ZipInfo], bool] | None = None,
) -> list[str]:
    """Safely and manually extract ZIP entries under ``target``."""
    target_abs = os.path.abspath(target)
    os.makedirs(target_abs, exist_ok=True)
    extracted: list[str] = []
    actual_total = 0

    with zipfile.ZipFile(zip_path) as archive:
        infos = archive.infolist()
        _validate_zip_infos(
            infos,
            max_entries=max_entries,
            max_file_bytes=max_file_bytes,
            max_total_bytes=max_total_bytes,
            max_ratio=max_ratio,
        )
        wanted = None if target_file is None else safe_relative_path(target_file)

        for info in infos:
            normalized, destination = confined_destination(target_abs, info.filename)
            if wanted is not None and normalized != wanted:
                continue
            if predicate is not None and not predicate(info):
                continue
            if info.is_dir():
                os.makedirs(destination, exist_ok=True)
                continue

            os.makedirs(os.path.dirname(destination), exist_ok=True)
            written = 0
            fd, temporary = tempfile.mkstemp(prefix=".minify-extract-", dir=os.path.dirname(destination))
            try:
                with os.fdopen(fd, "wb") as output, archive.open(info) as source:
                    while True:
                        chunk = source.read(1024 * 1024)
                        if not chunk:
                            break
                        written += len(chunk)
                        actual_total += len(chunk)
                        if written > max_file_bytes or written > int(info.file_size):
                            raise ValueError(f"ZIP entry expanded beyond declared/safe size: {info.filename}")
                        if actual_total > max_total_bytes:
                            raise ValueError("ZIP extraction exceeded the total size safety limit.")
                        output.write(chunk)
                os.replace(temporary, destination)
            except Exception:
                try:
                    os.remove(temporary)
                except FileNotFoundError:
                    pass
                raise
            extracted.append(normalized)

        if wanted is not None and wanted not in extracted:
            raise FileNotFoundError(f"Requested archive member was not found: {target_file}")
    return extracted


def safe_extract_tar(
    archive_path: str,
    target: str,
    *,
    target_file: str | None = None,
    max_entries: int = ARCHIVE_MAX_ENTRIES,
    max_file_bytes: int = ARCHIVE_MAX_FILE_BYTES,
    max_total_bytes: int = ARCHIVE_MAX_TOTAL_BYTES,
    max_ratio: float = ARCHIVE_MAX_COMPRESSION_RATIO,
) -> list[str]:
    """Extract regular files/directories from a tar.gz with bounded expansion."""
    target_abs = os.path.abspath(target)
    os.makedirs(target_abs, exist_ok=True)
    extracted: list[str] = []
    wanted = None if target_file is None else safe_relative_path(target_file)

    with tarfile.open(archive_path, "r:gz") as archive:
        members = archive.getmembers()
        if len(members) > max_entries:
            raise ValueError(f"Archive contains more than {max_entries} entries.")

        # Validate the complete archive before writing the first byte so a bad
        # late member cannot leave a partially extracted tree behind.
        declared_total = 0
        normalized_members: list[tuple[tarfile.TarInfo, str, str]] = []
        for member in members:
            normalized, destination = confined_destination(target_abs, member.name)
            if member.issym() or member.islnk() or member.isdev() or member.isfifo():
                raise ValueError(f"Unsafe tar member type: {member.name}")
            if member.isfile():
                size = int(member.size)
                if size < 0 or size > max_file_bytes:
                    raise ValueError(f"Tar entry exceeds the per-file safety limit: {member.name}")
                declared_total += size
                if declared_total > max_total_bytes:
                    raise ValueError("Tar archive exceeds the total extracted-size safety limit.")
            normalized_members.append((member, normalized, destination))

        compressed_size = os.path.getsize(archive_path)
        if declared_total and compressed_size <= 0:
            raise ValueError("Tar archive has an invalid compressed size.")
        if compressed_size and declared_total / compressed_size > max_ratio:
            raise ValueError("Tar archive has a suspicious compression ratio.")

        actual_total = 0
        for member, normalized, destination in normalized_members:
            if wanted is not None and normalized != wanted:
                continue
            if member.isdir():
                os.makedirs(destination, exist_ok=True)
                continue
            if not member.isfile():
                continue

            size = int(member.size)
            source = archive.extractfile(member)
            if source is None:
                raise ValueError(f"Could not read tar member: {member.name}")
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            fd, temporary = tempfile.mkstemp(prefix=".minify-extract-", dir=os.path.dirname(destination))
            try:
                written = 0
                with os.fdopen(fd, "wb") as output, source:
                    while True:
                        chunk = source.read(1024 * 1024)
                        if not chunk:
                            break
                        written += len(chunk)
                        actual_total += len(chunk)
                        if written > size or written > max_file_bytes:
                            raise ValueError(f"Tar entry expanded beyond declared/safe size: {member.name}")
                        if actual_total > max_total_bytes:
                            raise ValueError("Tar extraction exceeded the total size safety limit.")
                        output.write(chunk)
                os.replace(temporary, destination)
            except Exception:
                try:
                    os.remove(temporary)
                except FileNotFoundError:
                    pass
                raise
            extracted.append(normalized)

    if wanted is not None and wanted not in extracted:
        raise FileNotFoundError(f"Requested archive member was not found: {target_file}")
    return extracted


def safe_extract_archive(archive_path: str, target: str = ".", target_file: str | None = None) -> list[str]:
    if archive_path.casefold().endswith(".zip"):
        return safe_extract_zip(archive_path, target, target_file=target_file)
    if archive_path.casefold().endswith((".tar.gz", ".tgz")):
        return safe_extract_tar(archive_path, target, target_file=target_file)
    raise ValueError(f"Unsupported archive format: {archive_path}")
