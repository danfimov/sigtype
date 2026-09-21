from sigtype.filetype import (
    add_type,
    get_type,
    guess,
    guess_extension,
    guess_mime,
)
from sigtype.helpers import (
    is_archive,
    is_audio,
    is_document,
    is_extension_supported,
    is_font,
    is_image,
    is_mime_supported,
    is_video,
)
from sigtype.match import (
    application_match,
    archive_match,
    audio_match,
    document_match,
    font_match,
    image_match,
    match,
    video_match,
)

__version__ = "0.1.0"
version = __version__


__all__ = [
    "add_type",
    "application_match",
    "archive_match",
    "audio_match",
    "document_match",
    "font_match",
    "get_type",
    "guess",
    "guess_extension",
    "guess_mime",
    "image_match",
    "is_archive",
    "is_audio",
    "is_document",
    "is_extension_supported",
    "is_font",
    "is_image",
    "is_mime_supported",
    "is_video",
    "match",
    "video_match",
]
