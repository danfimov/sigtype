from typing import Final

from sigtype._compat import override
from sigtype.types.base import Type

_WOFF_TAG: Final = bytes([0x77, 0x4F, 0x46, 0x46])
_WOFF2_TAG: Final = bytes([0x77, 0x4F, 0x46, 0x32])
_SFNT_VERSION_TRUETYPE: Final = bytes([0x00, 0x01, 0x00, 0x00])
_SFNT_VERSION_OPENTYPE_CFF: Final = bytes([0x4F, 0x54, 0x54, 0x4F])
_SFNT_VERSION_TRUE: Final = bytes([0x74, 0x72, 0x75, 0x65])
_TTF_SIGNATURE: Final = bytes([0x00, 0x01, 0x00, 0x00, 0x00])
_OTF_SIGNATURE: Final = bytes([0x4F, 0x54, 0x54, 0x4F, 0x00])
_WOFF_MIN_LENGTH: Final = 7
_SFNT_MIN_LENGTH: Final = 4


class Woff(Type):
    """Implements the WOFF font type matcher."""

    MIME: Final[str] = "application/font-woff"
    EXTENSION: Final[str] = "woff"

    def __init__(self) -> None:
        """Initialize the Woff matcher."""
        super().__init__(mime=Woff.MIME, extension=Woff.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the WOFF font signature."""
        return (
            len(buf) > _WOFF_MIN_LENGTH
            and buf[0:4] == _WOFF_TAG
            and buf[4:8]
            in (
                _SFNT_VERSION_TRUETYPE,
                _SFNT_VERSION_OPENTYPE_CFF,
                _SFNT_VERSION_TRUE,
            )
        )


class Woff2(Type):
    """Implements the WOFF2 font type matcher."""

    MIME: Final[str] = "application/font-woff"
    EXTENSION: Final[str] = "woff2"

    def __init__(self) -> None:
        """Initialize the Woff2 matcher."""
        super().__init__(mime=Woff2.MIME, extension=Woff2.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the WOFF2 font signature."""
        return (
            len(buf) > _WOFF_MIN_LENGTH
            and buf[0:4] == _WOFF2_TAG
            and buf[4:8]
            in (
                _SFNT_VERSION_TRUETYPE,
                _SFNT_VERSION_OPENTYPE_CFF,
                _SFNT_VERSION_TRUE,
            )
        )


class Ttf(Type):
    """Implements the TTF font type matcher."""

    MIME: Final[str] = "application/font-sfnt"
    EXTENSION: Final[str] = "ttf"

    def __init__(self) -> None:
        """Initialize the Ttf matcher."""
        super().__init__(mime=Ttf.MIME, extension=Ttf.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the TTF font signature."""
        return len(buf) > _SFNT_MIN_LENGTH and buf[0:5] == _TTF_SIGNATURE


class Otf(Type):
    """Implements the OTF font type matcher."""

    MIME: Final[str] = "application/font-sfnt"
    EXTENSION: Final[str] = "otf"

    def __init__(self) -> None:
        """Initialize the Otf matcher."""
        super().__init__(mime=Otf.MIME, extension=Otf.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the OTF font signature."""
        return len(buf) > _SFNT_MIN_LENGTH and buf[0:5] == _OTF_SIGNATURE
