"""Minimal Source 2 RERL reader/rewriter for same-length redirects."""

from __future__ import annotations

import struct
from dataclasses import dataclass

KNOWN_HEADER_VERSION = 12
_HEADER_SIZE = 16
_BLOCK_ENTRY_SIZE = 12
_RERL_ENTRY_SIZE = 16


@dataclass(frozen=True)
class ResourceBlock:
    entry_pos: int
    type_name: str
    rel_offset: int
    abs_offset: int
    size: int


@dataclass(frozen=True)
class RERLEntry:
    id: int
    name: str
    string_offset: int
    string_length: int


@dataclass(frozen=True)
class CompiledResource:
    file_size: int
    header_version: int
    version: int
    block_offset: int
    block_count: int
    blocks: tuple[ResourceBlock, ...]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def parse_resource(data: bytes | bytearray) -> CompiledResource:
    """Parse and bounds-check the Source 2 resource header/block table."""
    _require(len(data) >= _HEADER_SIZE, "Compiled resource is shorter than its header.")

    file_size, header_version, version, block_offset, block_count = struct.unpack_from("<IHHII", data, 0)
    _require(header_version == KNOWN_HEADER_VERSION, f"Unsupported Source 2 header version: {header_version}.")
    _require(file_size == len(data), f"Compiled resource size mismatch: header={file_size}, actual={len(data)}.")

    table_start = 8 + block_offset
    table_size = block_count * _BLOCK_ENTRY_SIZE
    table_end = table_start + table_size
    _require(table_start >= _HEADER_SIZE, "Compiled resource block table starts inside the header.")
    _require(table_end <= len(data), "Compiled resource block table extends past EOF.")

    blocks: list[ResourceBlock] = []
    for index in range(block_count):
        entry_pos = table_start + index * _BLOCK_ENTRY_SIZE
        block_type, rel_offset, size = struct.unpack_from("<4sII", data, entry_pos)
        try:
            type_name = block_type.decode("ascii")
        except UnicodeDecodeError as exc:
            raise ValueError(f"Block {index} has a non-ASCII type.") from exc

        abs_offset = entry_pos + 4 + rel_offset
        block_end = abs_offset + size
        _require(abs_offset >= table_end, f"Block {type_name!r} overlaps the block table.")
        _require(abs_offset <= len(data), f"Block {type_name!r} starts past EOF.")
        _require(block_end <= len(data), f"Block {type_name!r} extends past EOF.")
        blocks.append(
            ResourceBlock(
                entry_pos=entry_pos,
                type_name=type_name,
                rel_offset=rel_offset,
                abs_offset=abs_offset,
                size=size,
            )
        )

    return CompiledResource(
        file_size=file_size,
        header_version=header_version,
        version=version,
        block_offset=block_offset,
        block_count=block_count,
        blocks=tuple(blocks),
    )


def read_rerl(data: bytes | bytearray) -> list[RERLEntry]:
    """Read external-reference mappings from a compiled resource's RERL block."""
    resource = parse_resource(data)
    rerl_block = next((block for block in resource.blocks if block.type_name == "RERL"), None)
    if rerl_block is None or rerl_block.size == 0:
        return []

    block_start = rerl_block.abs_offset
    block_end = block_start + rerl_block.size
    _require(rerl_block.size >= 8, "RERL block is shorter than its header.")

    entries_offset, count = struct.unpack_from("<II", data, block_start)
    if count == 0:
        return []

    entries_start = block_start + entries_offset
    entries_end = entries_start + count * _RERL_ENTRY_SIZE
    _require(entries_offset >= 8, "RERL entry table overlaps its header.")
    _require(entries_end <= block_end, "RERL entry table extends past the RERL block.")

    entries: list[RERLEntry] = []
    for index in range(count):
        entry_pos = entries_start + index * _RERL_ENTRY_SIZE
        resource_id, string_rel_offset, padding = struct.unpack_from("<Qii", data, entry_pos)
        _require(padding == 0, f"RERL entry {index} has unexpected padding value {padding}.")

        string_offset = entry_pos + 8 + string_rel_offset
        _require(entries_end <= string_offset < block_end, f"RERL entry {index} string offset is out of range.")

        terminator = data.find(b"\x00", string_offset, block_end)
        _require(terminator != -1, f"RERL entry {index} string is not NUL-terminated inside the block.")

        raw_name = bytes(data[string_offset:terminator])
        try:
            name = raw_name.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"RERL entry {index} name is not valid UTF-8.") from exc

        entries.append(
            RERLEntry(
                id=resource_id,
                name=name,
                string_offset=string_offset,
                string_length=len(raw_name),
            )
        )

    return entries


def patch_resource_rerl(
    data: bytes | bytearray,
    redirect_map: dict[str, str],
) -> tuple[bytearray, int]:
    """Redirect RERL names in place without changing IDs or resource layout.

    Only same-byte-length UTF-8 replacements are accepted. This intentionally
    avoids resizing or relocating Source 2 blocks.
    """
    if not redirect_map:
        return bytearray(data), 0

    normalized: dict[str, bytes] = {}
    for source, target in redirect_map.items():
        if not isinstance(source, str) or not isinstance(target, str):
            raise ValueError("RERL redirects must map strings to strings.")
        if not source or not target:
            raise ValueError("RERL redirect paths must be non-empty.")
        if "\x00" in source or "\x00" in target:
            raise ValueError("RERL redirect paths cannot contain NUL bytes.")

        source_bytes = source.encode("utf-8")
        target_bytes = target.encode("utf-8")
        if len(source_bytes) != len(target_bytes):
            raise ValueError(f"RERL redirect must preserve UTF-8 byte length: {source!r} -> {target!r}.")
        normalized[source] = target_bytes

    entries = read_rerl(data)
    patched = bytearray(data)
    replacement_count = 0
    for entry in entries:
        replacement = normalized.get(entry.name)
        if replacement is None:
            continue
        if len(replacement) != entry.string_length:
            raise ValueError(f"RERL entry length mismatch for {entry.name!r}.")
        patched[entry.string_offset : entry.string_offset + entry.string_length] = replacement
        replacement_count += 1

    if replacement_count:
        # Fail closed if the in-place mutation produced a resource we can no longer parse.
        read_rerl(patched)

    return patched, replacement_count
