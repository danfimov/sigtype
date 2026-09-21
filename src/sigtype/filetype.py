from typing import Any

from sigtype.match import match
from sigtype.types import TYPES, Type
from sigtype.utils import ReadableInput


def guess(obj: ReadableInput) -> Type | None:
    """Infer the type of the given input.

    Function is overloaded to accept multiple types in input
    and perform the needed type inference based on it.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        The matched type instance. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return match(obj) if obj else None


def guess_mime(obj: ReadableInput) -> str | None:
    """Infer the file type of the given input and return its MIME type.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        The matched MIME type as string. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    kind = guess(obj)
    return kind.mime if kind is not None else None


def guess_extension(obj: ReadableInput) -> str | None:
    """Infer the file type of the given input and return its RFC file extension.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        The matched file extension as string. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    kind = guess(obj)
    return kind.extension if kind is not None else None


def get_type(mime: str | None = None, ext: str | None = None) -> Type | None:
    """Return the file type instance searching by MIME type or file extension.

    Args:
        ext: file extension string. E.g: jpg, png, mp4, mp3
        mime: MIME string. E.g: image/jpeg, video/mpeg

    Returns:
        The matched file type instance. Otherwise None.
    """
    for kind in TYPES:
        if kind.extension == ext or kind.mime == mime:
            return kind
    return None


def add_type(instance: Any) -> None:  # noqa: ANN401
    """Add a new type matcher instance to the supported types.

    Args:
        instance: Type inherited instance.

    Returns:
        None
    """
    if not isinstance(instance, Type):
        msg = "instance must inherit from sigtype.types.Type"
        raise TypeError(msg)

    TYPES.insert(0, instance)
