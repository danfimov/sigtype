from typing import Final

from sigtype._compat import override
from sigtype.types.base import Type
from sigtype.types.isobmff import IsoBmff

_MP4_COMPATIBLE_BRANDS: Final = ("mp41", "mp42", "isom")


class Mp4(IsoBmff):
    """Implements the MP4 video type matcher."""

    MIME: Final[str] = "video/mp4"
    EXTENSION: Final[str] = "mp4"

    def __init__(self) -> None:
        """Initialize the Mp4 matcher."""
        super().__init__(mime=Mp4.MIME, extension=Mp4.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the MP4 file signature."""
        if not self._is_isobmff(buf):
            return False

        major_brand, _minor_version, compatible_brands = self._get_ftyp(buf)
        for brand in compatible_brands:
            if brand in _MP4_COMPATIBLE_BRANDS:
                return True
        return major_brand in _MP4_COMPATIBLE_BRANDS


_M4V_MIN_LENGTH: Final = 10
_M4V_SIGNATURE: Final = (0x0, 0x0, 0x0, 0x1C, 0x66, 0x74, 0x79, 0x70, 0x4D, 0x34, 0x56)


class M4v(Type):
    """Implements the M4V video type matcher."""

    MIME: Final[str] = "video/x-m4v"
    EXTENSION: Final[str] = "m4v"

    def __init__(self) -> None:
        """Initialize the M4v matcher."""
        super().__init__(mime=M4v.MIME, extension=M4v.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the M4V file signature."""
        return (
            len(buf) > _M4V_MIN_LENGTH
            and buf[0] == _M4V_SIGNATURE[0]
            and buf[1] == _M4V_SIGNATURE[1]
            and buf[2] == _M4V_SIGNATURE[2]
            and buf[3] == _M4V_SIGNATURE[3]
            and buf[4] == _M4V_SIGNATURE[4]
            and buf[5] == _M4V_SIGNATURE[5]
            and buf[6] == _M4V_SIGNATURE[6]
            and buf[7] == _M4V_SIGNATURE[7]
            and buf[8] == _M4V_SIGNATURE[8]
            and buf[9] == _M4V_SIGNATURE[9]
            and buf[10] == _M4V_SIGNATURE[10]
        )


class Mkv(Type):
    """Implements the MKV video type matcher."""

    MIME: Final[str] = "video/x-matroska"
    EXTENSION: Final[str] = "mkv"

    def __init__(self) -> None:
        """Initialize the Mkv matcher."""
        super().__init__(mime=Mkv.MIME, extension=Mkv.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the MKV file signature."""
        # Check the cheap EBML header first: searching the whole buffer for the doctype is far more expensive
        # and would otherwise run for every input that reaches this matcher.
        return buf.startswith(b"\x1a\x45\xdf\xa3") and buf.find(b"\x42\x82\x88matroska") > -1


class Webm(Type):
    """Implements the WebM video type matcher."""

    MIME: Final[str] = "video/webm"
    EXTENSION: Final[str] = "webm"

    def __init__(self) -> None:
        """Initialize the Webm matcher."""
        super().__init__(mime=Webm.MIME, extension=Webm.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the WebM file signature."""
        return buf.startswith(b"\x1a\x45\xdf\xa3") and buf.find(b"\x42\x82\x84webm") > -1


class Mov(IsoBmff):
    """Implements the MOV video type matcher."""

    MIME: Final[str] = "video/quicktime"
    EXTENSION: Final[str] = "mov"

    def __init__(self) -> None:
        """Initialize the Mov matcher."""
        super().__init__(mime=Mov.MIME, extension=Mov.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the MOV file signature."""
        if not self._is_isobmff(buf):
            return False

        major_brand, _minor_version, _compatible_brands = self._get_ftyp(buf)
        return major_brand == "qt  "


_AVI_MIN_LENGTH: Final = 11
_AVI_RIFF_SIGNATURE: Final = (0x52, 0x49, 0x46, 0x46)
_AVI_AVI_SIGNATURE: Final = (0x41, 0x56, 0x49, 0x20)


class Avi(Type):
    """Implements the AVI video type matcher."""

    MIME: Final[str] = "video/x-msvideo"
    EXTENSION: Final[str] = "avi"

    def __init__(self) -> None:
        """Initialize the Avi matcher."""
        super().__init__(mime=Avi.MIME, extension=Avi.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the AVI file signature."""
        return (
            len(buf) > _AVI_MIN_LENGTH
            and buf[0] == _AVI_RIFF_SIGNATURE[0]
            and buf[1] == _AVI_RIFF_SIGNATURE[1]
            and buf[2] == _AVI_RIFF_SIGNATURE[2]
            and buf[3] == _AVI_RIFF_SIGNATURE[3]
            and buf[8] == _AVI_AVI_SIGNATURE[0]
            and buf[9] == _AVI_AVI_SIGNATURE[1]
            and buf[10] == _AVI_AVI_SIGNATURE[2]
            and buf[11] == _AVI_AVI_SIGNATURE[3]
        )


_WMV_MIN_LENGTH: Final = 9
_WMV_SIGNATURE: Final = (0x30, 0x26, 0xB2, 0x75, 0x8E, 0x66, 0xCF, 0x11, 0xA6, 0xD9)


class Wmv(Type):
    """Implements the WMV video type matcher."""

    MIME: Final[str] = "video/x-ms-wmv"
    EXTENSION: Final[str] = "wmv"

    def __init__(self) -> None:
        """Initialize the Wmv matcher."""
        super().__init__(mime=Wmv.MIME, extension=Wmv.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the WMV file signature."""
        return (
            len(buf) > _WMV_MIN_LENGTH
            and buf[0] == _WMV_SIGNATURE[0]
            and buf[1] == _WMV_SIGNATURE[1]
            and buf[2] == _WMV_SIGNATURE[2]
            and buf[3] == _WMV_SIGNATURE[3]
            and buf[4] == _WMV_SIGNATURE[4]
            and buf[5] == _WMV_SIGNATURE[5]
            and buf[6] == _WMV_SIGNATURE[6]
            and buf[7] == _WMV_SIGNATURE[7]
            and buf[8] == _WMV_SIGNATURE[8]
            and buf[9] == _WMV_SIGNATURE[9]
        )


_FLV_MIN_LENGTH: Final = 3
_FLV_SIGNATURE: Final = (0x46, 0x4C, 0x56, 0x01)


class Flv(Type):
    """Implements the FLV video type matcher."""

    MIME: Final[str] = "video/x-flv"
    EXTENSION: Final[str] = "flv"

    def __init__(self) -> None:
        """Initialize the Flv matcher."""
        super().__init__(mime=Flv.MIME, extension=Flv.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the FLV file signature."""
        return (
            len(buf) > _FLV_MIN_LENGTH
            and buf[0] == _FLV_SIGNATURE[0]
            and buf[1] == _FLV_SIGNATURE[1]
            and buf[2] == _FLV_SIGNATURE[2]
            and buf[3] == _FLV_SIGNATURE[3]
        )


_MPEG_MIN_LENGTH: Final = 3
_MPEG_SIGNATURE: Final = (0x0, 0x0, 0x1)
_MPEG_STREAM_ID_MIN: Final = 0xB0
_MPEG_STREAM_ID_MAX: Final = 0xBF


class Mpeg(Type):
    """Implements the MPEG video type matcher."""

    MIME: Final[str] = "video/mpeg"
    EXTENSION: Final[str] = "mpg"

    def __init__(self) -> None:
        """Initialize the Mpeg matcher."""
        super().__init__(mime=Mpeg.MIME, extension=Mpeg.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the MPEG file signature."""
        return (
            len(buf) > _MPEG_MIN_LENGTH
            and buf[0] == _MPEG_SIGNATURE[0]
            and buf[1] == _MPEG_SIGNATURE[1]
            and buf[2] == _MPEG_SIGNATURE[2]
            and _MPEG_STREAM_ID_MIN <= buf[3] <= _MPEG_STREAM_ID_MAX
        )


_M3GP_MIN_LENGTH: Final = 10
_M3GP_SIGNATURE: Final = (0x66, 0x74, 0x79, 0x70, 0x33, 0x67, 0x70)


class M3gp(Type):
    """Implements the 3gp video type matcher."""

    MIME: Final[str] = "video/3gpp"
    EXTENSION: Final[str] = "3gp"

    def __init__(self) -> None:
        """Initialize the M3gp matcher."""
        super().__init__(mime=M3gp.MIME, extension=M3gp.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the 3GP file signature."""
        return (
            len(buf) > _M3GP_MIN_LENGTH
            and buf[4] == _M3GP_SIGNATURE[0]
            and buf[5] == _M3GP_SIGNATURE[1]
            and buf[6] == _M3GP_SIGNATURE[2]
            and buf[7] == _M3GP_SIGNATURE[3]
            and buf[8] == _M3GP_SIGNATURE[4]
            and buf[9] == _M3GP_SIGNATURE[5]
            and buf[10] == _M3GP_SIGNATURE[6]
        )
