from sigtype.match import (
    archive_match,
    audio_match,
    document_match,
    font_match,
    image_match,
    video_match,
)
from sigtype.text import looks_like_text
from sigtype.types import TYPES
from sigtype.utils import ReadableInput, get_bytes


def is_extension_supported(ext: str) -> bool:
    """Check if the given extension string is one of the supported matchers.

    Args:
        ext (str): file extension string. E.g: jpg, png, mp4, mp3

    Returns:
        True if the file extension is supported.
        Otherwise False.
    """
    return any(kind.extension == ext for kind in TYPES)


def is_mime_supported(mime: str) -> bool:
    """Check if the given MIME type string is one of the supported matchers.

    Args:
        mime (str): MIME string. E.g: image/jpeg, video/mpeg

    Returns:
        True if the MIME type is supported.
        Otherwise False.
    """
    return any(kind.is_mime(mime) for kind in TYPES)


def is_image(obj: ReadableInput) -> bool:
    """Check if a given input is a supported type image.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        True if obj is a valid image. Otherwise False.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return image_match(obj) is not None


def is_archive(obj: ReadableInput) -> bool:
    """Check if a given input is a supported type archive.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        True if obj is a valid archive. Otherwise False.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return archive_match(obj) is not None


def is_audio(obj: ReadableInput) -> bool:
    """Check if a given input is a supported type audio.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        True if obj is a valid audio. Otherwise False.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return audio_match(obj) is not None


def is_video(obj: ReadableInput) -> bool:
    """Check if a given input is a supported type video.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        True if obj is a valid video. Otherwise False.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return video_match(obj) is not None


def is_font(obj: ReadableInput) -> bool:
    """Check if a given input is a supported type font.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        True if obj is a valid font. Otherwise False.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return font_match(obj) is not None


def is_document(obj: ReadableInput) -> bool:
    """Check if a given input is a supported type document.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        True if obj is a valid document. Otherwise False.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return document_match(obj) is not None


def is_text(obj: ReadableInput) -> bool:
    """Check if a given input looks like human readable text.

    Only the first SIGNATURE_SIZE bytes are inspected. Text is UTF-8 (with or without BOM) or
    UTF-16/UTF-32 with a BOM, without NUL bytes or control characters other than whitespace.
    An empty input counts as text.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        True if obj looks like text. Otherwise False.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return looks_like_text(get_bytes(obj))


def is_binary(obj: ReadableInput) -> bool:
    """Check if a given input looks like binary data, i.e. is not text.

    See `is_text` for what counts as text. An empty input is not binary.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        True if obj does not look like text. Otherwise False.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return not is_text(obj)
