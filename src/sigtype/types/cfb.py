import struct
from typing import Final

from sigtype.utils import ReadAt

OLE_SIGNATURE: Final = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"

_HEADER_SIZE: Final = 512
_SECTOR_SHIFT_OFFSET: Final = 30
_FIRST_DIRECTORY_SECTOR_OFFSET: Final = 48
_DIFAT_OFFSET: Final = 76
_DIFAT_ENTRIES: Final = 109
_SECTOR_SHIFTS: Final = (9, 12)
_DIRECTORY_ENTRY_SIZE: Final = 128
_MAX_DIRECTORY_SECTORS: Final = 32

_END_OF_CHAIN: Final = 0xFFFFFFFE
_MAX_REGULAR_SECTOR: Final = 0xFFFFFFFA
_NO_STREAM: Final = 0xFFFFFFFF

_NAME_MAX_LENGTH: Final = 64
_NAME_TERMINATOR_SIZE: Final = 2
_ROOT_STORAGE: Final = 5

# Directory entry fields following the 64-byte name: name length, object type, colour flag (skipped),
# left sibling, right sibling and child.
_ENTRY_FIELDS: Final = struct.Struct("<HBxIII")
_ENTRY_FIELDS_OFFSET: Final = 64


def read_root_entry_names(buf: bytes | bytearray, read_at: ReadAt | None) -> frozenset[str] | None:
    """Read the names of the entries directly under the root of a Compound File Binary (OLE2) container.

    OLE2 based formats (doc, xls, ppt, msg, ...) share one container signature and are told apart by the streams
    they hold, e.g. `WordDocument` or `Workbook`. The directory can sit anywhere in the file, so sectors outside
    `buf` are fetched through `read_at`.

    Args:
        buf: the first bytes of the input.
        read_at: random access reader for the whole input, or None when unavailable.

    Returns:
        Names of the root's direct children, or None if the directory could not be read completely.
    """
    if len(buf) < _HEADER_SIZE or buf[:8] != OLE_SIGNATURE:
        return None

    shift = _u16(buf, _SECTOR_SHIFT_OFFSET)
    if shift not in _SECTOR_SHIFTS:
        return None

    directory = _read_directory(buf, read_at, shift)
    if directory is None:
        return None

    _, root_type, _, _, root_child = _ENTRY_FIELDS.unpack_from(directory, _ENTRY_FIELDS_OFFSET)
    if root_type != _ROOT_STORAGE:
        return None

    # Entries form a red-black tree of siblings per storage. Walk the root's children only, so that
    # e.g. a Workbook embedded in a Word document does not make the Word document look like a spreadsheet.
    entry_count = len(directory) // _DIRECTORY_ENTRY_SIZE
    names: set[str] = set()
    visited: set[int] = set()
    stack = [root_child]
    while stack:
        index = stack.pop()
        if index == _NO_STREAM or index >= entry_count or index in visited:
            continue
        visited.add(index)

        start = index * _DIRECTORY_ENTRY_SIZE
        name_length, _, left, right, _ = _ENTRY_FIELDS.unpack_from(directory, start + _ENTRY_FIELDS_OFFSET)
        if _NAME_TERMINATOR_SIZE <= name_length <= _NAME_MAX_LENGTH:
            # the stored length counts the terminating NUL
            raw_name = directory[start : start + name_length - _NAME_TERMINATOR_SIZE]
            names.add(bytes(raw_name).decode("utf-16-le", errors="replace"))
        stack.extend((left, right))

    return frozenset(names)


def _read_directory(buf: bytes | bytearray, read_at: ReadAt | None, shift: int) -> bytes | None:
    """Return the raw directory: the concatenated sectors of the directory chain, or None if unreadable."""
    sector_size = 1 << shift

    fat_sectors: dict[int, bytes | bytearray] = {}
    sectors: list[bytes | bytearray] = []
    visited: set[int] = set()
    sector = _u32(buf, _FIRST_DIRECTORY_SECTOR_OFFSET)

    for _ in range(_MAX_DIRECTORY_SECTORS):
        if sector > _MAX_REGULAR_SECTOR or sector in visited:
            return None
        visited.add(sector)

        data = _read(buf, read_at, (sector + 1) << shift, sector_size)
        if data is None:
            return None
        sectors.append(data)

        next_sector = _next_sector(buf, read_at, fat_sectors, sector, shift)
        if next_sector is None:
            return None
        if next_sector == _END_OF_CHAIN:
            return b"".join(sectors)
        sector = next_sector

    return None


def _next_sector(
    buf: bytes | bytearray,
    read_at: ReadAt | None,
    fat_sectors: dict[int, bytes | bytearray],
    sector: int,
    shift: int,
) -> int | None:
    """Look up the sector following `sector` in the FAT chain, or None if the FAT cannot be read."""
    entries_per_fat_sector = (1 << shift) // 4

    # FAT sectors beyond the 109 listed in the header (very large files) are not supported.
    fat_index = sector // entries_per_fat_sector
    if fat_index >= _DIFAT_ENTRIES:
        return None

    if fat_index not in fat_sectors:
        fat_sector = _u32(buf, _DIFAT_OFFSET + 4 * fat_index)
        if fat_sector > _MAX_REGULAR_SECTOR:
            return None
        fat = _read(buf, read_at, (fat_sector + 1) << shift, 1 << shift)
        if fat is None:
            return None
        fat_sectors[fat_index] = fat

    return _u32(fat_sectors[fat_index], (sector % entries_per_fat_sector) * 4)


def _read(buf: bytes | bytearray, read_at: ReadAt | None, offset: int, size: int) -> bytes | bytearray | None:
    if offset + size <= len(buf):
        return buf[offset : offset + size]
    if read_at is None:
        return None
    data = read_at(offset, size)
    return data if len(data) == size else None


def _u16(data: bytes | bytearray, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 2], "little")


def _u32(data: bytes | bytearray, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "little")
