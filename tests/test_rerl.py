import struct

import pytest
from core import rerl


def _resource_with_rerl(name: str, resource_id: int = 0x1122334455667788) -> bytes:
    name_bytes = name.encode("utf-8") + b"\x00"
    rerl_payload = struct.pack("<IIQii", 8, 1, resource_id, 8, 0) + name_bytes
    data_payload = b"DATA-PAYLOAD"

    block_count = 2
    table_start = 16
    table_size = block_count * 12
    rerl_offset = table_start + table_size
    data_offset = rerl_offset + len(rerl_payload)

    total_size = data_offset + len(data_payload)
    buf = bytearray(total_size)
    struct.pack_into("<IHHII", buf, 0, total_size, 12, 1, 8, block_count)

    rerl_entry_pos = table_start
    data_entry_pos = table_start + 12
    struct.pack_into(
        "<4sII",
        buf,
        rerl_entry_pos,
        b"RERL",
        rerl_offset - (rerl_entry_pos + 4),
        len(rerl_payload),
    )
    struct.pack_into(
        "<4sII",
        buf,
        data_entry_pos,
        b"DATA",
        data_offset - (data_entry_pos + 4),
        len(data_payload),
    )

    buf[rerl_offset : rerl_offset + len(rerl_payload)] = rerl_payload
    buf[data_offset : data_offset + len(data_payload)] = data_payload
    return bytes(buf)


def test_patch_resource_rerl_redirects_name_without_changing_layout_or_id():
    source = "materials/models/props_tree/tree_oak_leaves_05.vmat"
    target = "materials/models/props_tree/tree_oak_leaves_00.vmat"
    original = _resource_with_rerl(source)

    patched, count = rerl.patch_resource_rerl(original, {source: target})

    assert count == 1
    assert len(patched) == len(original)
    assert patched[:4] == original[:4]
    entries = rerl.read_rerl(patched)
    assert [(entry.id, entry.name) for entry in entries] == [(0x1122334455667788, target)]


def test_patch_resource_rerl_no_match_is_byte_identical():
    original = _resource_with_rerl("materials/models/props_tree/tree_oak_leaves_blank.vmat")

    patched, count = rerl.patch_resource_rerl(
        original,
        {
            "materials/models/props_tree/tree_oak_leaves_05.vmat":
                "materials/models/props_tree/tree_oak_leaves_00.vmat"
        },
    )

    assert count == 0
    assert bytes(patched) == original


def test_patch_resource_rerl_rejects_length_change():
    original = _resource_with_rerl("a.vmat")

    with pytest.raises(ValueError, match="preserve UTF-8 byte length"):
        rerl.patch_resource_rerl(original, {"a.vmat": "longer.vmat"})


def test_read_rerl_rejects_bad_header_version():
    original = bytearray(_resource_with_rerl("a.vmat"))
    struct.pack_into("<H", original, 4, 11)

    with pytest.raises(ValueError, match="header version"):
        rerl.read_rerl(original)


def test_read_rerl_rejects_out_of_bounds_block():
    original = bytearray(_resource_with_rerl("a.vmat"))
    struct.pack_into("<I", original, 24, 0x7FFFFFFF)

    with pytest.raises(ValueError, match="extends past EOF"):
        rerl.read_rerl(original)
