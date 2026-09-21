import pathlib
from collections.abc import Callable
from pathlib import Path
from typing import IO, Final, TypeVar, cast

from sigtype._compat import override

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


class SourceReader:
    """Random access reader over an input, usable as a `ReadAt` callable.

    Readers built by `make_reader()` may hold an open file, so callers must `close()` them when done.

    A reader belongs to a single input. `memo` lets matchers share a computed result, such as a parsed container
    directory, between each other for as long as the reader lives.
    """

    def __init__(self) -> None:
        """Create a reader with an empty memo."""
        self.memo: dict[str, object] = {}

    def __call__(self, offset: int, size: int) -> bytes | bytearray:
        """Return up to `size` bytes starting at `offset`."""
        raise NotImplementedError

    def close(self) -> None:
        """Release any resources held by the reader. The reader stays usable and reacquires them on demand."""


class _MemoryReader(SourceReader):
    def __init__(self, data: bytes | bytearray) -> None:
        super().__init__()
        self._data = data

    @override
    def __call__(self, offset: int, size: int) -> bytes | bytearray:
        if offset < 0 or size <= 0:
            return b""
        return self._data[offset : offset + size]


class _PathReader(SourceReader):
    """Opens the file on the first read and keeps it open until closed, so several reads cost a single open."""

    def __init__(self, path: str | pathlib.PurePath) -> None:
        super().__init__()
        self._path = path
        self._fp: IO[bytes] | None = None

    @override
    def __call__(self, offset: int, size: int) -> bytes | bytearray:
        if offset < 0 or size <= 0:
            return b""
        if self._fp is None:
            self._fp = open(self._path, "rb")  # noqa: PTH123, SIM115
        self._fp.seek(offset)
        return self._fp.read(size)

    @override
    def close(self) -> None:
        if self._fp is not None:
            self._fp.close()
            self._fp = None


class _StreamReader(SourceReader):
    """Reads from a seekable stream, restoring its position afterwards. The stream is owned by the caller."""

    def __init__(self, stream: IO[bytes]) -> None:
        super().__init__()
        self._stream = stream

    @override
    def __call__(self, offset: int, size: int) -> bytes | bytearray:
        if offset < 0 or size <= 0:
            return b""
        start_pos = self._stream.tell()
        try:
            self._stream.seek(offset)
            return self._stream.read(size)
        finally:
            self._stream.seek(start_pos)


class CallableReader(SourceReader):
    """Adapts a caller supplied `read_at` callable, giving matchers the shared `memo` of a reader."""

    def __init__(self, read_at: ReadAt) -> None:
        """Wrap the given `read_at` callable."""
        super().__init__()
        self._read_at = read_at

    @override
    def __call__(self, offset: int, size: int) -> bytes | bytearray:
        """Delegate to the wrapped callable."""
        return self._read_at(offset, size)


def make_reader(obj: ReadableInput) -> SourceReader | None:
    """Build a random access reader for the given input.

    Args:
        obj: path to file, bytes, bytearray, memoryview or file-like object.

    Returns:
        A reader to be used as a `read_at(offset, size)` callable, which the caller must `close()`.
        None for inputs that cannot be read back at arbitrary offsets, e.g. non-seekable streams.
    """
    if isinstance(obj, (bytes, bytearray)):
        return _MemoryReader(obj)

    if isinstance(obj, memoryview):
        return _MemoryReader(obj.tobytes())

    if isinstance(obj, (str, pathlib.PurePath)):
        return _PathReader(obj)

    if hasattr(obj, "read") and hasattr(obj, "seek") and hasattr(obj, "tell"):
        return _StreamReader(obj)

    return None
