"""Builds minimal Compound File Binary (OLE2) containers for tests."""

import struct

FREESECT = 0xFFFFFFFF
ENDOFCHAIN = 0xFFFFFFFE
FATSECT = 0xFFFFFFFD
NOSTREAM = 0xFFFFFFFF

ROOT = 5
STORAGE = 1
STREAM = 2

Child = str | tuple[str, list[str]]


def _entry(name: str, obj_type: int, right: int = NOSTREAM, child: int = NOSTREAM) -> bytes:
    raw = name.encode("utf-16-le")
    head = raw.ljust(64, b"\x00") + struct.pack("<H", len(raw) + 2 if name else 0) + bytes([obj_type, 1])
    return head + struct.pack("<III", NOSTREAM, right, child) + b"\x00" * 48


def build_cfb(children: list[Child], *, padding_sectors: int = 0, sector_shift: int = 9) -> bytearray:
    """Build a container whose root holds `children`.

    A child is either a stream name or a `(storage name, [stream names])` pair. `padding_sectors` inserts unused
    sectors before the directory, pushing it further into the file.
    """
    sector_size = 1 << sector_shift

    # Directory entries: the root, then its children chained through right siblings, then nested streams.
    top = len(children)
    entries = [_entry("Root Entry", ROOT, child=1 if top else NOSTREAM)]
    nested: list[bytes] = []
    for i, child in enumerate(children):
        right = i + 2 if i + 1 < top else NOSTREAM
        if isinstance(child, str):
            entries.append(_entry(child, STREAM, right=right))
        else:
            name, streams = child
            first = 1 + top + len(nested)
            entries.append(_entry(name, STORAGE, right=right, child=first))
            nested.extend(
                _entry(stream, STREAM, right=first + j + 1 if j + 1 < len(streams) else NOSTREAM)
                for j, stream in enumerate(streams)
            )
    entries.extend(nested)

    per_sector = sector_size // 128
    while len(entries) % per_sector:
        entries.append(_entry("", 0))
    directory = b"".join(entries)
    directory_sectors = len(directory) // sector_size

    # Sector 0 is the FAT, then the padding, then the directory chain.
    fat = [FATSECT] + [ENDOFCHAIN] * padding_sectors
    first_directory = 1 + padding_sectors
    fat += [first_directory + i + 1 for i in range(directory_sectors - 1)] + [ENDOFCHAIN]
    fat += [FREESECT] * (sector_size // 4 - len(fat))

    header = bytearray(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1")
    header += b"\x00" * 16
    header += struct.pack("<HHHHH", 0x3E, 3 if sector_shift == 9 else 4, 0xFFFE, sector_shift, 6)
    header += b"\x00" * 6
    header += struct.pack("<IIIIIIIII", 0, 1, first_directory, 0, 4096, ENDOFCHAIN, 0, ENDOFCHAIN, 0)
    header += struct.pack("<109I", 0, *([FREESECT] * 108))
    header = header.ljust(sector_size, b"\x00")

    return bytearray(
        header + struct.pack(f"<{len(fat)}I", *fat) + b"\x00" * sector_size * padding_sectors + directory,
    )
