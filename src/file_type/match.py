from collections.abc import Sequence

from file_type.types import (
    APPLICATION,
    ARCHIVE,
    AUDIO,
    DOCUMENT,
    FONT,
    IMAGE,
    TYPES,
    VIDEO,
)
from file_type.types.base import Type
from file_type.utils import ReadableInput, get_bytes


def match(obj: ReadableInput, matchers: Sequence[Type] = TYPES) -> Type | None:
    """Match the given input against the available file type matchers.

    Args:
        obj: path to file, bytes or bytearray.
        matchers: sequence of type matchers to check against.

    Returns:
        Type instance if type matches. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    buf = get_bytes(obj)

    for matcher in matchers:
        if matcher.match(buf):
            return matcher

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
