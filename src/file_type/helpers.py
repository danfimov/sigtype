from file_type.match import (
    archive_match,
    audio_match,
    document_match,
    font_match,
    image_match,
    video_match,
)
from file_type.types import TYPES
from file_type.utils import ReadableInput


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
    return any(kind.mime == mime for kind in TYPES)


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
