from typing import Final, override

from file_type.types.base import Type
from file_type.types.isobmff import IsoBmff

_JPEG_SIGNATURE: Final = bytes([0xFF, 0xD8, 0xFF])
_JPX_MIN_LENGTH: Final = 50
_JPX_SIGNATURE: Final = bytes([0x00, 0x00, 0x00, 0x0C])
_JPX_FTYP: Final = b"ftypjp2 "
_JXL_CODESTREAM_SIGNATURE: Final = bytes([0xFF, 0x0A])
_JXL_CONTAINER_MIN_LENGTH: Final = 11
_JXL_CONTAINER_SIGNATURE: Final = bytes(
    [0x00, 0x00, 0x00, 0x0C, 0x4A, 0x58, 0x4C, 0x20, 0x0D, 0x0A, 0x87, 0x0A],
)
_PNG_SIGNATURE: Final = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
_PNG_SIGNATURE_LENGTH: Final = len(_PNG_SIGNATURE)
_CHUNK_LENGTH_SIZE: Final = 4
_CHUNK_TYPE_SIZE: Final = 4
_CHUNK_CRC_SIZE: Final = 4
_PNG_TAG: Final = bytes([0x89, 0x50, 0x4E, 0x47])
_GIF_TAG: Final = bytes([0x47, 0x49, 0x46])
_WEBP_MIN_LENGTH: Final = 13
_WEBP_RIFF_TAG: Final = bytes([0x52, 0x49, 0x46, 0x46])
_WEBP_WEBP_TAG: Final = bytes([0x57, 0x45, 0x42, 0x50])
_WEBP_RIFF_END: Final = 4
_WEBP_WEBP_START: Final = 8
_WEBP_WEBP_END: Final = 12
_TIFF_MIN_LENGTH: Final = 9
_TIFF_LE_TAG: Final = bytes([0x49, 0x49, 0x2A, 0x00])
_TIFF_BE_TAG: Final = bytes([0x4D, 0x4D, 0x00, 0x2A])
_CR2_TAG: Final = bytes([0x43, 0x52])
_BMP_TAG: Final = bytes([0x42, 0x4D])
_JXR_TAG: Final = bytes([0x49, 0x49, 0xBC])
_PSD_TAG: Final = bytes([0x38, 0x42, 0x50, 0x53])
_ICO_TAG: Final = bytes([0x00, 0x00, 0x01, 0x00])
_ISOBMFF_HEIC_BRANDS: Final = ("mif1", "msf1")
_DCM_OFFSET: Final = 128
_DCM_TAG: Final = bytes([0x44, 0x49, 0x43, 0x4D])
_DWG_TAG: Final = bytes([0x41, 0x43, 0x31, 0x30])
_XCF_TAG: Final = bytes([0x67, 0x69, 0x6D, 0x70, 0x20, 0x78, 0x63, 0x66, 0x20, 0x76])
_QOI_TAG: Final = bytes([0x71, 0x6F, 0x69, 0x66])
_DDS_TAG: Final = b"\x44\x44\x53\x20"


class Jpeg(Type):
    """Implements the JPEG image type matcher."""

    MIME: Final[str] = "image/jpeg"
    EXTENSION: Final[str] = "jpg"

    def __init__(self) -> None:
        """Initialize the Jpeg matcher."""
        super().__init__(mime=Jpeg.MIME, extension=Jpeg.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the JPEG file signature."""
        return len(buf) >= len(_JPEG_SIGNATURE) and buf[0:3] == _JPEG_SIGNATURE


class Jpx(Type):
    """Implements the JPEG2000 image type matcher."""

    MIME: Final[str] = "image/jpx"
    EXTENSION: Final[str] = "jpx"

    def __init__(self) -> None:
        """Initialize the Jpx matcher."""
        super().__init__(mime=Jpx.MIME, extension=Jpx.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the JPEG2000 file signature."""
        return len(buf) > _JPX_MIN_LENGTH and buf[0:4] == _JPX_SIGNATURE and buf[16:24] == _JPX_FTYP


class Jxl(Type):
    """Implements the JPEG XL image type matcher."""

    MIME: Final[str] = "image/jxl"
    EXTENSION: Final[str] = "jxl"

    def __init__(self) -> None:
        """Initialize the Jxl matcher."""
        super().__init__(mime=Jxl.MIME, extension=Jxl.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the JPEG XL codestream or container signature."""
        return (len(buf) > 1 and buf[0:2] == _JXL_CODESTREAM_SIGNATURE) or (
            len(buf) > _JXL_CONTAINER_MIN_LENGTH and buf[0:12] == _JXL_CONTAINER_SIGNATURE
        )


class Apng(Type):
    """Implements the APNG image type matcher."""

    MIME: Final[str] = "image/apng"
    EXTENSION: Final[str] = "apng"

    def __init__(self) -> None:
        """Initialize the Apng matcher."""
        super().__init__(mime=Apng.MIME, extension=Apng.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match APNG by scanning PNG chunks for an acTL chunk before IDAT."""
        is_png = len(buf) > _PNG_SIGNATURE_LENGTH and buf[:_PNG_SIGNATURE_LENGTH] == _PNG_SIGNATURE
        if is_png:
            # cursor in buf, skip already readed 8 bytes
            i = _PNG_SIGNATURE_LENGTH
            while len(buf) > i:
                data_length = int.from_bytes(
                    buf[i : i + _CHUNK_LENGTH_SIZE],
                    byteorder="big",
                )
                i += _CHUNK_LENGTH_SIZE

                chunk_type = buf[i : i + _CHUNK_TYPE_SIZE].decode(
                    "ascii",
                    errors="ignore",
                )
                i += _CHUNK_TYPE_SIZE

                # acTL chunk in APNG must appear before IDAT
                # IEND is end of PNG
                if chunk_type in {"IDAT", "IEND"}:
                    return False
                if chunk_type == "acTL":
                    return True

                # move to the next chunk by skipping data and crc (4 bytes)
                i += data_length + _CHUNK_CRC_SIZE

        return False


class Png(Type):
    """Implements the PNG image type matcher."""

    MIME: Final[str] = "image/png"
    EXTENSION: Final[str] = "png"

    def __init__(self) -> None:
        """Initialize the Png matcher."""
        super().__init__(mime=Png.MIME, extension=Png.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the PNG file signature."""
        return len(buf) >= len(_PNG_TAG) and buf[0:4] == _PNG_TAG


class Gif(Type):
    """Implements the GIF image type matcher."""

    MIME: Final[str] = "image/gif"
    EXTENSION: Final[str] = "gif"

    def __init__(self) -> None:
        """Initialize the Gif matcher."""
        super().__init__(
            mime=Gif.MIME,
            extension=Gif.EXTENSION,
        )

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the GIF file signature."""
        return len(buf) >= len(_GIF_TAG) and buf[0:3] == _GIF_TAG


class Webp(Type):
    """Implements the WEBP image type matcher."""

    MIME: Final[str] = "image/webp"
    EXTENSION: Final[str] = "webp"

    def __init__(self) -> None:
        """Initialize the Webp matcher."""
        super().__init__(
            mime=Webp.MIME,
            extension=Webp.EXTENSION,
        )

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the WEBP file signature."""
        return (
            len(buf) > _WEBP_MIN_LENGTH
            and buf[0:_WEBP_RIFF_END] == _WEBP_RIFF_TAG
            and buf[_WEBP_WEBP_START:_WEBP_WEBP_END] == _WEBP_WEBP_TAG
        )


class Cr2(Type):
    """Implements the CR2 image type matcher."""

    MIME: Final[str] = "image/x-canon-cr2"
    EXTENSION: Final[str] = "cr2"

    def __init__(self) -> None:
        """Initialize the Cr2 matcher."""
        super().__init__(
            mime=Cr2.MIME,
            extension=Cr2.EXTENSION,
        )

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the CR2 file signature."""
        return len(buf) > _TIFF_MIN_LENGTH and buf[0:4] in (_TIFF_LE_TAG, _TIFF_BE_TAG) and buf[8:10] == _CR2_TAG


class Tiff(Type):
    """Implements the TIFF image type matcher."""

    MIME: Final[str] = "image/tiff"
    EXTENSION: Final[str] = "tif"

    def __init__(self) -> None:
        """Initialize the Tiff matcher."""
        super().__init__(
            mime=Tiff.MIME,
            extension=Tiff.EXTENSION,
        )

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the TIFF file signature (excluding CR2)."""
        return len(buf) > _TIFF_MIN_LENGTH and buf[0:4] in (_TIFF_LE_TAG, _TIFF_BE_TAG) and buf[8:10] != _CR2_TAG


class Bmp(Type):
    """Implements the BMP image type matcher."""

    MIME: Final[str] = "image/bmp"
    EXTENSION: Final[str] = "bmp"

    def __init__(self) -> None:
        """Initialize the Bmp matcher."""
        super().__init__(
            mime=Bmp.MIME,
            extension=Bmp.EXTENSION,
        )

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the BMP file signature."""
        return len(buf) > 1 and buf[0:2] == _BMP_TAG


class Jxr(Type):
    """Implements the JXR image type matcher."""

    MIME: Final[str] = "image/vnd.ms-photo"
    EXTENSION: Final[str] = "jxr"

    def __init__(self) -> None:
        """Initialize the Jxr matcher."""
        super().__init__(
            mime=Jxr.MIME,
            extension=Jxr.EXTENSION,
        )

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the JXR file signature."""
        return len(buf) >= len(_JXR_TAG) and buf[0:3] == _JXR_TAG


class Psd(Type):
    """Implements the PSD image type matcher."""

    MIME: Final[str] = "image/vnd.adobe.photoshop"
    EXTENSION: Final[str] = "psd"

    def __init__(self) -> None:
        """Initialize the Psd matcher."""
        super().__init__(
            mime=Psd.MIME,
            extension=Psd.EXTENSION,
        )

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the PSD file signature."""
        return len(buf) >= len(_PSD_TAG) and buf[0:4] == _PSD_TAG


class Ico(Type):
    """Implements the ICO image type matcher."""

    MIME: Final[str] = "image/x-icon"
    EXTENSION: Final[str] = "ico"

    def __init__(self) -> None:
        """Initialize the Ico matcher."""
        super().__init__(
            mime=Ico.MIME,
            extension=Ico.EXTENSION,
        )

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the ICO file signature."""
        return len(buf) >= len(_ICO_TAG) and buf[0:4] == _ICO_TAG


class Heic(IsoBmff):
    """Implements the HEIC image type matcher."""

    MIME: Final[str] = "image/heic"
    EXTENSION: Final[str] = "heic"

    def __init__(self) -> None:
        """Initialize the Heic matcher."""
        super().__init__(mime=Heic.MIME, extension=Heic.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the HEIC ISO-BMFF brand."""
        if not self._is_isobmff(buf):
            return False

        major_brand, _minor_version, compatible_brands = self._get_ftyp(buf)
        if major_brand == "heic":
            return True
        return bool(
            major_brand in _ISOBMFF_HEIC_BRANDS and "heic" in compatible_brands,
        )


class Dcm(Type):
    """Implements the DICOM image type matcher."""

    MIME: Final[str] = "application/dicom"
    EXTENSION: Final[str] = "dcm"
    OFFSET: Final = _DCM_OFFSET

    def __init__(self) -> None:
        """Initialize the Dcm matcher."""
        super().__init__(mime=Dcm.MIME, extension=Dcm.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the DICOM file signature at the fixed preamble offset."""
        return (
            len(buf) > Dcm.OFFSET + _CHUNK_LENGTH_SIZE and buf[Dcm.OFFSET : Dcm.OFFSET + _CHUNK_LENGTH_SIZE] == _DCM_TAG
        )


class Dwg(Type):
    """Implements the Dwg image type matcher."""

    MIME: Final[str] = "image/vnd.dwg"
    EXTENSION: Final[str] = "dwg"

    def __init__(self) -> None:
        """Initialize the Dwg matcher."""
        super().__init__(mime=Dwg.MIME, extension=Dwg.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the DWG file signature."""
        return buf[:4] == bytearray(_DWG_TAG)


class Xcf(Type):
    """Implements the Xcf image type matcher."""

    MIME: Final[str] = "image/x-xcf"
    EXTENSION: Final[str] = "xcf"

    def __init__(self) -> None:
        """Initialize the Xcf matcher."""
        super().__init__(mime=Xcf.MIME, extension=Xcf.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the XCF file signature."""
        return buf[:10] == bytearray(_XCF_TAG)


class Avif(IsoBmff):
    """Implements the AVIF image type matcher."""

    MIME: Final[str] = "image/avif"
    EXTENSION: Final[str] = "avif"

    def __init__(self) -> None:
        """Initialize the Avif matcher."""
        super().__init__(mime=Avif.MIME, extension=Avif.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the AVIF ISO-BMFF brand."""
        if not self._is_isobmff(buf):
            return False

        major_brand, _minor_version, compatible_brands = self._get_ftyp(buf)
        if major_brand in ["avif", "avis"]:
            return True
        return bool(
            major_brand in _ISOBMFF_HEIC_BRANDS and "avif" in compatible_brands,
        )


class Qoi(Type):
    """Implements the QOI image type matcher."""

    MIME: Final[str] = "image/qoi"
    EXTENSION: Final[str] = "qoi"

    def __init__(self) -> None:
        """Initialize the Qoi matcher."""
        super().__init__(mime=Qoi.MIME, extension=Qoi.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the QOI file signature."""
        return len(buf) >= len(_QOI_TAG) and buf[0:4] == _QOI_TAG


class Dds(Type):
    """Implements the DDS image type matcher."""

    MIME: Final[str] = "image/dds"
    EXTENSION: Final[str] = "dds"

    def __init__(self) -> None:
        """Initialize the Dds matcher."""
        super().__init__(mime=Dds.MIME, extension=Dds.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the DDS file signature."""
        return buf.startswith(_DDS_TAG)
