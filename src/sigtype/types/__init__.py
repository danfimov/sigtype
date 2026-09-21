from typing import Final

from sigtype.types import application, archive, audio, document, font, image, text, video
from sigtype.types.base import Type

# Text based formats are recognized by parsing their content, which costs more than comparing a signature.
# They are members of their families (so is_image() and is_document() know them) but are tried last by guess().
_SVG: Final = text.Svg()
_FB2: Final = text.Fb2()
_EML: Final = text.Eml()

# Supported image types
IMAGE: Final = (
    image.Dwg(),
    image.Xcf(),
    image.Jpeg(),
    image.Jpx(),
    image.Jxl(),
    image.Apng(),
    image.Png(),
    image.Gif(),
    image.Webp(),
    image.Dcm(),
    image.Tiff(),
    image.Cr2(),
    image.Bmp(),
    image.Jxr(),
    image.Psd(),
    image.Ico(),
    image.Heic(),
    image.Avif(),
    image.Qoi(),
    image.Dds(),
    _SVG,
)

# Supported video types
VIDEO: Final = (
    video.M3gp(),
    video.Mp4(),
    video.M4v(),
    video.Mkv(),
    video.Mov(),
    video.Avi(),
    video.Wmv(),
    video.Mpeg(),
    video.Webm(),
    video.Flv(),
)

# Supported audio types
AUDIO: Final = (
    audio.Aac(),
    audio.Midi(),
    audio.Flac(),
    audio.Mp3(),
    audio.M4a(),
    audio.Opus(),
    audio.Ogg(),
    audio.Wav(),
    audio.Amr(),
    audio.Aiff(),
)

# Supported font types
FONT: Final = (font.Woff(), font.Woff2(), font.Ttf(), font.Otf())

# Supported archive container types
ARCHIVE: Final = (
    archive.Br(),
    archive.Rpm(),
    archive.Epub(),
    archive.Zip(),
    archive.Tar(),
    archive.Rar(),
    archive.Gz(),
    archive.Bz2(),
    archive.SevenZ(),
    archive.Pdf(),
    archive.Exe(),
    archive.Swf(),
    archive.Rtf(),
    archive.Nes(),
    archive.Crx(),
    archive.Cab(),
    archive.Eot(),
    archive.Ps(),
    archive.Xz(),
    archive.Sqlite(),
    archive.Deb(),
    archive.Ar(),
    archive.Z(),
    archive.Lzop(),
    archive.Lz(),
    archive.Elf(),
    archive.Lz4(),
    archive.Zstd(),
)

# Supported archive container types
APPLICATION: Final = (application.Wasm(),)

# Supported document types
DOCUMENT: Final = (
    document.Doc(),
    document.Docx(),
    document.Odt(),
    document.Ppt(),
    document.Pptx(),
    document.Odp(),
    document.Xls(),
    document.Xlsx(),
    document.Ods(),
    document.Msg(),
    document.Ofd(),
    document.Mobi(),
    document.Djvu(),
    _FB2,
    _EML,
)

# Plain text matchers. Not part of TYPES, since any text file would match them and guess() would stop returning
# None for unknown data. Pass them explicitly: `sigtype.match(obj, [*TYPES, *PLAIN_TEXT])`. Md must precede Txt.
PLAIN_TEXT: Final = (text.Md(), text.Txt())

# Expose supported type matchers
_TEXT_BASED: Final[tuple[Type, ...]] = (_SVG, _FB2, _EML)
TYPES: Final[list[Type]] = [
    *(kind for kind in (*IMAGE, *AUDIO, *VIDEO, *FONT, *DOCUMENT, *ARCHIVE, *APPLICATION) if kind not in _TEXT_BASED),
    *_TEXT_BASED,
]

__all__ = [
    "APPLICATION",
    "ARCHIVE",
    "AUDIO",
    "DOCUMENT",
    "FONT",
    "IMAGE",
    "PLAIN_TEXT",
    "TYPES",
    "VIDEO",
    "Type",
]
