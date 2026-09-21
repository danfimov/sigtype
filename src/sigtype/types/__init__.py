from typing import Final

from sigtype.types import application, archive, audio, document, font, image, video
from sigtype.types.base import Type

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
)


# Expose supported type matchers
TYPES: Final = list(IMAGE + AUDIO + VIDEO + FONT + DOCUMENT + ARCHIVE + APPLICATION)

__all__ = [
    "APPLICATION",
    "ARCHIVE",
    "AUDIO",
    "DOCUMENT",
    "FONT",
    "IMAGE",
    "TYPES",
    "VIDEO",
    "Type",
]
