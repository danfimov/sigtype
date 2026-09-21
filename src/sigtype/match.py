import pathlib
from collections.abc import Sequence
from typing import IO

from sigtype.types import (
    APPLICATION,
    ARCHIVE,
    AUDIO,
    DOCUMENT,
    FONT,
    IMAGE,
    TYPES,
    VIDEO,
)
from sigtype.types.base import Type
from sigtype.utils import (
    SIGNATURE_SIZE,
    CallableReader,
    FileReader,
    ReadableInput,
    ReadAt,
    SourceReader,
    get_bytes,
    make_reader,
)


def match(obj: ReadableInput, matchers: Sequence[Type] = TYPES, *, read_at: ReadAt | None = None) -> Type | None:
    """Match the given input against the available file type matchers.

    Args:
        obj: path to file, bytes or bytearray.
        matchers: sequence of type matchers to check against.
        read_at: optional `read_at(offset, size)` callable giving random access to the input, used by
            matchers that need data beyond the first SIGNATURE_SIZE bytes. Built automatically for paths,
            in-memory buffers and seekable streams. Pass it for other sources, e.g. ranged HTTP requests.

    Returns:
        Type instance if type matches. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    if isinstance(obj, (str, pathlib.PurePath)):
        # The file is opened once: it supplies the signature bytes and any later reads of matchers that need more
        with open(obj, "rb") as fp:  # noqa: PTH123
            return _run_matchers(bytearray(fp.read(SIGNATURE_SIZE)), obj, matchers, read_at, fp)

    return _run_matchers(get_bytes(obj), obj, matchers, read_at, None)


def _run_matchers(
    buf: bytes | bytearray,
    obj: ReadableInput,
    matchers: Sequence[Type],
    read_at: ReadAt | None,
    fp: IO[bytes] | None,
) -> Type | None:
    # A fresh wrapper per call: the memo it carries must not outlive this input
    reader: SourceReader | None = CallableReader(read_at) if read_at is not None else None
    reader_resolved = read_at is not None
    own_reader: SourceReader | None = None

    try:
        for matcher in matchers:
            if matcher.uses_read_at:
                if not reader_resolved:
                    # built on first use and shared by every matcher of this call
                    own_reader = FileReader(fp) if fp is not None else make_reader(obj)
                    reader = own_reader
                    reader_resolved = True
                if matcher.match_at(buf, reader):
                    return matcher
            elif matcher.match(buf):
                return matcher
    finally:
        if own_reader is not None:
            own_reader.close()

    return None


def image_match(obj: ReadableInput) -> Type | None:
    """Match the given input against the available image type matchers.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        Type instance if matches. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return match(obj, IMAGE)


def font_match(obj: ReadableInput) -> Type | None:
    """Match the given input against the available font type matchers.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        Type instance if matches. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return match(obj, FONT)


def video_match(obj: ReadableInput) -> Type | None:
    """Match the given input against the available video type matchers.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        Type instance if matches. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return match(obj, VIDEO)


def audio_match(obj: ReadableInput) -> Type | None:
    """Match the given input against the available audio type matchers.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        Type instance if matches. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return match(obj, AUDIO)


def archive_match(obj: ReadableInput) -> Type | None:
    """Match the given input against the available archive type matchers.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        Type instance if matches. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return match(obj, ARCHIVE)


def application_match(obj: ReadableInput) -> Type | None:
    """Match the given input against the available application type matchers.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        Type instance if matches. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return match(obj, APPLICATION)


def document_match(obj: ReadableInput) -> Type | None:
    """Match the given input against the available document type matchers.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        Type instance if matches. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return match(obj, DOCUMENT)
