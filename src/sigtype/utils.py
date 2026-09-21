import pathlib
from collections.abc import Callable
from pathlib import Path
from typing import IO, Final, TypeVar, cast

# Number of leading bytes handed to every matcher
SIGNATURE_SIZE: Final = 8192

ReadableInput = str | Path | bytes | bytearray | memoryview | IO[bytes]

# Random access into the input: `read_at(offset, size)` returns up to `size` bytes starting at `offset`
# (fewer, or none, when the input is shorter). Lets matchers look past the first SIGNATURE_SIZE bytes.
ReadAt = Callable[[int, int], bytes | bytearray]

_Buffer = TypeVar("_Buffer", bytes, bytearray, memoryview)


def get_signature_bytes(path: str | pathlib.PurePath) -> bytearray:
    """Read file from disk and return the first 8192 bytes.

    The result represents the magic number header signature.

    Args:
        path: path string to file.

    Returns:
        First 8192 bytes of the file content as bytearray type.
    """
    with open(path, "rb") as fp:  # noqa: PTH123
        return bytearray(fp.read(SIGNATURE_SIZE))


def signature(array: _Buffer) -> _Buffer:
    """Return the first 8192 bytes of the given bytearray.

    This is part of the file header signature.

    Args:
        array: bytearray to extract the header signature.

    Returns:
        First 8192 bytes of the file content as bytearray type.
    """
    length = len(array)
    index = min(length, SIGNATURE_SIZE)

    # mypyc's per-specialization type checking cannot verify that slicing preserves the concrete buffer type across this
    # constrained TypeVar (regular mypy infers it fine, hence warn_redundant_casts is disabled for this module below).
    return cast("_Buffer", array[:index])


def get_bytes(obj: ReadableInput) -> bytes | bytearray:
    """Infer the input type and read the first 8192 bytes.

    Returns a sliced bytearray.

    Args:
        obj: path to readable, file-like object(with read() method), bytes,
        bytearray or memoryview

    Returns:
        First 8192 bytes of the file content as bytearray type.

    Raises:
        TypeError: if obj is not a supported type.
    """
    if isinstance(obj, bytearray):
        return signature(obj)

    if isinstance(obj, bytes):
        return signature(obj)

    if isinstance(obj, (str, pathlib.PurePath)):
        return get_signature_bytes(obj)

    if isinstance(obj, memoryview):
        return bytearray(signature(obj).tolist())

    if hasattr(obj, "read"):
        return _get_bytes_from_stream(obj)

    msg = f"Unsupported type as file input: {type(obj)}"
    raise TypeError(msg)


def _get_bytes_from_stream(stream: IO[bytes]) -> bytes | bytearray:
    """Read the header signature bytes from a file-like object."""
    if hasattr(stream, "tell") and hasattr(stream, "seek"):
        start_pos = stream.tell()
        stream.seek(0)
        magic_bytes = stream.read(SIGNATURE_SIZE)
        stream.seek(start_pos)
        return get_bytes(magic_bytes)
    return get_bytes(stream.read(SIGNATURE_SIZE))


def make_reader(obj: ReadableInput) -> ReadAt | None:
    """Build a random access reader for the given input.

    Args:
        obj: path to file, bytes, bytearray, memoryview or file-like object.

    Returns:
        A `read_at(offset, size)` callable. None for inputs that cannot be read back
        at arbitrary offsets, e.g. non-seekable streams.
    """
    if isinstance(obj, (bytes, bytearray)):
        return _memory_reader(obj)

    if isinstance(obj, memoryview):
        return _memory_reader(obj.tobytes())

    if isinstance(obj, (str, pathlib.PurePath)):
        return _path_reader(obj)

    if hasattr(obj, "read") and hasattr(obj, "seek") and hasattr(obj, "tell"):
        return _stream_reader(obj)

    return None


def _memory_reader(data: bytes | bytearray) -> ReadAt:
    def read_at(offset: int, size: int) -> bytes | bytearray:
        if offset < 0 or size <= 0:
            return b""
        return data[offset : offset + size]

    return read_at


def _path_reader(path: str | pathlib.PurePath) -> ReadAt:
    def read_at(offset: int, size: int) -> bytes | bytearray:
        if offset < 0 or size <= 0:
            return b""
        with open(path, "rb") as fp:  # noqa: PTH123
            fp.seek(offset)
            return fp.read(size)

    return read_at


def _stream_reader(stream: IO[bytes]) -> ReadAt:
    def read_at(offset: int, size: int) -> bytes | bytearray:
        if offset < 0 or size <= 0:
            return b""
        start_pos = stream.tell()
        try:
            stream.seek(offset)
            return stream.read(size)
        finally:
            stream.seek(start_pos)

    return read_at
