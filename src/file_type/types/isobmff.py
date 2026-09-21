import codecs
from typing import Final

from file_type.types.base import Type

_FTYP_HEADER_SIZE: Final = 16


class IsoBmff(Type):
    """Implements the ISO-BMFF base type."""

    def __init__(self, mime: str, extension: str) -> None:
        """Initialize the ISO-BMFF matcher for the given mime/extension."""
        super().__init__(mime=mime, extension=extension)

    def _is_isobmff(self, buf: bytes | bytearray) -> bool:
        if len(buf) < _FTYP_HEADER_SIZE or buf[4:8] != b"ftyp":
            return False
        return not len(buf) < int(codecs.encode(buf[0:4], "hex"), 16)

    def _get_ftyp(self, buf: bytes | bytearray) -> tuple[str, int, list[str]]:
        ftyp_len = int(codecs.encode(buf[0:4], "hex"), 16)
        major_brand = buf[8:12].decode(errors="ignore")
        minor_version = int(codecs.encode(buf[12:16], "hex"), 16)
        compatible_brands = [buf[i : i + 4].decode(errors="ignore") for i in range(_FTYP_HEADER_SIZE, ftyp_len, 4)]

        return major_brand, minor_version, compatible_brands
