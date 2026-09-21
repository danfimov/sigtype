import struct
from typing import Final

from sigtype._compat import override
from sigtype.types.base import Type


class Epub(Type):
    """Implements the EPUB archive type matcher."""

    MIME: Final[str] = "application/epub+zip"
    EXTENSION: Final[str] = "epub"

    SIGNATURE: Final = bytes([0x50, 0x4B, 0x3, 0x4])
    MIMETYPE_ENTRY: Final = b"mimetypeapplication/epub+zip"

    def __init__(self) -> None:
        """Initialize the EPUB matcher."""
        super().__init__(mime=Epub.MIME, extension=Epub.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the EPUB signature."""
        return buf[:4] == Epub.SIGNATURE and buf[30:58] == Epub.MIMETYPE_ENTRY


class Zip(Type):
    """Implements the Zip archive type matcher."""

    MIME: Final[str] = "application/zip"
    EXTENSION: Final[str] = "zip"

    MIN_LENGTH: Final = 3
    PREFIX: Final = bytes([0x50, 0x4B])
    VERSION_BYTES: Final = (0x3, 0x5, 0x7)
    FLAG_BYTES: Final = (0x4, 0x6, 0x8)

    def __init__(self) -> None:
        """Initialize the Zip matcher."""
        super().__init__(mime=Zip.MIME, extension=Zip.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the Zip signature."""
        return (
            len(buf) > Zip.MIN_LENGTH
            and buf[:2] == Zip.PREFIX
            and buf[2] in Zip.VERSION_BYTES
            and buf[3] in Zip.FLAG_BYTES
        )


class Tar(Type):
    """Implements the Tar archive type matcher."""

    MIME: Final[str] = "application/x-tar"
    EXTENSION: Final[str] = "tar"

    SIGNATURE: Final = bytes([0x75, 0x73, 0x74, 0x61, 0x72])

    def __init__(self) -> None:
        """Initialize the Tar matcher."""
        super().__init__(mime=Tar.MIME, extension=Tar.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer contains the Tar signature."""
        return buf[257:262] == Tar.SIGNATURE


class Rar(Type):
    """Implements the RAR archive type matcher."""

    MIME: Final[str] = "application/x-rar-compressed"
    EXTENSION: Final[str] = "rar"

    MIN_LENGTH: Final = 6
    SIGNATURE: Final = bytes([0x52, 0x61, 0x72, 0x21, 0x1A, 0x7])
    VERSION_BYTES: Final = (0x0, 0x1)

    def __init__(self) -> None:
        """Initialize the RAR matcher."""
        super().__init__(mime=Rar.MIME, extension=Rar.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the RAR signature."""
        return len(buf) > Rar.MIN_LENGTH and buf[:6] == Rar.SIGNATURE and buf[6] in Rar.VERSION_BYTES


class Gz(Type):
    """Implements the GZ archive type matcher."""

    MIME: Final[str] = "application/gzip"
    EXTENSION: Final[str] = "gz"

    SIGNATURE: Final = bytes([0x1F, 0x8B, 0x8])

    def __init__(self) -> None:
        """Initialize the GZ matcher."""
        super().__init__(mime=Gz.MIME, extension=Gz.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the GZ signature."""
        return buf[:3] == Gz.SIGNATURE


class Bz2(Type):
    """Implements the BZ2 archive type matcher."""

    MIME: Final[str] = "application/x-bzip2"
    EXTENSION: Final[str] = "bz2"

    SIGNATURE: Final = bytes([0x42, 0x5A, 0x68])

    def __init__(self) -> None:
        """Initialize the BZ2 matcher."""
        super().__init__(mime=Bz2.MIME, extension=Bz2.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the BZ2 signature."""
        return buf[:3] == Bz2.SIGNATURE


class SevenZ(Type):
    """Implements the SevenZ (7z) archive type matcher."""

    MIME: Final[str] = "application/x-7z-compressed"
    EXTENSION: Final[str] = "7z"

    SIGNATURE: Final = bytes([0x37, 0x7A, 0xBC, 0xAF, 0x27, 0x1C])

    def __init__(self) -> None:
        """Initialize the SevenZ matcher."""
        super().__init__(mime=SevenZ.MIME, extension=SevenZ.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the SevenZ signature."""
        return buf[:6] == SevenZ.SIGNATURE


class Pdf(Type):
    """Implements the PDF archive type matcher."""

    MIME: Final[str] = "application/pdf"
    EXTENSION: Final[str] = "pdf"

    BOM: Final = bytes([0xEF, 0xBB, 0xBF])
    SIGNATURE: Final = bytes([0x25, 0x50, 0x44, 0x46])

    def __init__(self) -> None:
        """Initialize the PDF matcher."""
        super().__init__(mime=Pdf.MIME, extension=Pdf.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the PDF signature."""
        # Detect BOM and skip first 3 bytes
        if buf[:3] == Pdf.BOM:
            buf = buf[3:]

        return buf[:4] == Pdf.SIGNATURE


class Exe(Type):
    """Implements the EXE archive type matcher."""

    MIME: Final[str] = "application/x-msdownload"
    EXTENSION: Final[str] = "exe"

    SIGNATURE: Final = bytes([0x4D, 0x5A])

    def __init__(self) -> None:
        """Initialize the EXE matcher."""
        super().__init__(mime=Exe.MIME, extension=Exe.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the EXE signature."""
        return buf[:2] == Exe.SIGNATURE


class Swf(Type):
    """Implements the SWF archive type matcher."""

    MIME: Final[str] = "application/x-shockwave-flash"
    EXTENSION: Final[str] = "swf"

    MIN_LENGTH: Final = 2
    FIRST_BYTES: Final = (0x46, 0x43, 0x5A)
    SIGNATURE_TAIL: Final = bytes([0x57, 0x53])

    def __init__(self) -> None:
        """Initialize the SWF matcher."""
        super().__init__(mime=Swf.MIME, extension=Swf.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the SWF signature."""
        return len(buf) > Swf.MIN_LENGTH and buf[0] in Swf.FIRST_BYTES and buf[1:3] == Swf.SIGNATURE_TAIL


class Rtf(Type):
    """Implements the RTF archive type matcher."""

    MIME: Final[str] = "application/rtf"
    EXTENSION: Final[str] = "rtf"

    SIGNATURE: Final = bytes([0x7B, 0x5C, 0x72, 0x74, 0x66])

    def __init__(self) -> None:
        """Initialize the RTF matcher."""
        super().__init__(mime=Rtf.MIME, extension=Rtf.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the RTF signature."""
        return buf[:5] == Rtf.SIGNATURE


class Nes(Type):
    """Implements the NES archive type matcher."""

    MIME: Final[str] = "application/x-nintendo-nes-rom"
    EXTENSION: Final[str] = "nes"

    SIGNATURE: Final = bytes([0x4E, 0x45, 0x53, 0x1A])

    def __init__(self) -> None:
        """Initialize the NES matcher."""
        super().__init__(mime=Nes.MIME, extension=Nes.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the NES signature."""
        return buf[:4] == Nes.SIGNATURE


class Crx(Type):
    """Implements the CRX archive type matcher."""

    MIME: Final[str] = "application/x-google-chrome-extension"
    EXTENSION: Final[str] = "crx"

    SIGNATURE: Final = bytes([0x43, 0x72, 0x32, 0x34])

    def __init__(self) -> None:
        """Initialize the CRX matcher."""
        super().__init__(mime=Crx.MIME, extension=Crx.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the CRX signature."""
        return buf[:4] == Crx.SIGNATURE


class Cab(Type):
    """Implements the CAB archive type matcher."""

    MIME: Final[str] = "application/vnd.ms-cab-compressed"
    EXTENSION: Final[str] = "cab"

    SIGNATURE_MSCF: Final = bytes([0x4D, 0x53, 0x43, 0x46])
    SIGNATURE_ISC: Final = bytes([0x49, 0x53, 0x63, 0x28])

    def __init__(self) -> None:
        """Initialize the CAB matcher."""
        super().__init__(mime=Cab.MIME, extension=Cab.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the CAB signature."""
        return buf[:4] == Cab.SIGNATURE_MSCF or buf[:4] == Cab.SIGNATURE_ISC


class Eot(Type):
    """Implements the EOT archive type matcher."""

    MIME: Final[str] = "application/octet-stream"
    EXTENSION: Final[str] = "eot"

    TAIL: Final = bytes([0x4C, 0x50])
    VERSION_1: Final = bytes([0x02, 0x00, 0x01])
    VERSION_2: Final = bytes([0x01, 0x00, 0x00])
    VERSION_3: Final = bytes([0x02, 0x00, 0x02])

    def __init__(self) -> None:
        """Initialize the EOT matcher."""
        super().__init__(mime=Eot.MIME, extension=Eot.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer contains the EOT signature."""
        return buf[34:36] == Eot.TAIL and (
            buf[8:11] == Eot.VERSION_1 or buf[8:11] == Eot.VERSION_2 or buf[8:11] == Eot.VERSION_3
        )


class Ps(Type):
    """Implements the PS archive type matcher."""

    MIME: Final[str] = "application/postscript"
    EXTENSION: Final[str] = "ps"

    SIGNATURE: Final = bytes([0x25, 0x21])

    def __init__(self) -> None:
        """Initialize the PS matcher."""
        super().__init__(mime=Ps.MIME, extension=Ps.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the PS signature."""
        return buf[:2] == Ps.SIGNATURE


class Xz(Type):
    """Implements the XS archive type matcher."""

    MIME: Final[str] = "application/x-xz"
    EXTENSION: Final[str] = "xz"

    SIGNATURE: Final = bytes([0xFD, 0x37, 0x7A, 0x58, 0x5A, 0x00])

    def __init__(self) -> None:
        """Initialize the Xz matcher."""
        super().__init__(mime=Xz.MIME, extension=Xz.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the Xz signature."""
        return buf[:6] == Xz.SIGNATURE


class Sqlite(Type):
    """Implements the Sqlite DB archive type matcher."""

    MIME: Final[str] = "application/x-sqlite3"
    EXTENSION: Final[str] = "sqlite"

    SIGNATURE: Final = bytes([0x53, 0x51, 0x4C, 0x69])

    def __init__(self) -> None:
        """Initialize the Sqlite matcher."""
        super().__init__(mime=Sqlite.MIME, extension=Sqlite.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the Sqlite signature."""
        return buf[:4] == Sqlite.SIGNATURE


class Deb(Type):
    """Implements the DEB archive type matcher."""

    MIME: Final[str] = "application/x-deb"
    EXTENSION: Final[str] = "deb"

    SIGNATURE: Final = bytes(
        [
            0x21,
            0x3C,
            0x61,
            0x72,
            0x63,
            0x68,
            0x3E,
            0x0A,
            0x64,
            0x65,
            0x62,
            0x69,
            0x61,
            0x6E,
            0x2D,
            0x62,
            0x69,
            0x6E,
            0x61,
            0x72,
            0x79,
        ]
    )

    def __init__(self) -> None:
        """Initialize the DEB matcher."""
        super().__init__(mime=Deb.MIME, extension=Deb.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the DEB signature."""
        return buf[:21] == Deb.SIGNATURE


class Ar(Type):
    """Implements the AR archive type matcher."""

    MIME: Final[str] = "application/x-unix-archive"
    EXTENSION: Final[str] = "ar"

    SIGNATURE: Final = bytes([0x21, 0x3C, 0x61, 0x72, 0x63, 0x68, 0x3E])

    def __init__(self) -> None:
        """Initialize the AR matcher."""
        super().__init__(mime=Ar.MIME, extension=Ar.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the AR signature."""
        return buf[:7] == Ar.SIGNATURE


class Z(Type):
    """Implements the Z archive type matcher."""

    MIME: Final[str] = "application/x-compress"
    EXTENSION: Final[str] = "Z"

    SIGNATURE_1: Final = bytes([0x1F, 0xA0])
    SIGNATURE_2: Final = bytes([0x1F, 0x9D])

    def __init__(self) -> None:
        """Initialize the Z matcher."""
        super().__init__(mime=Z.MIME, extension=Z.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the Z signature."""
        return buf[:2] == Z.SIGNATURE_1 or buf[:2] == Z.SIGNATURE_2


class Lzop(Type):
    """Implements the Lzop archive type matcher."""

    MIME: Final[str] = "application/x-lzop"
    EXTENSION: Final[str] = "lzo"

    SIGNATURE: Final = bytes([0x89, 0x4C, 0x5A, 0x4F, 0x00, 0x0D, 0x0A, 0x1A])

    def __init__(self) -> None:
        """Initialize the Lzop matcher."""
        super().__init__(mime=Lzop.MIME, extension=Lzop.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the Lzop signature."""
        return buf[:8] == Lzop.SIGNATURE


class Lz(Type):
    """Implements the Lz archive type matcher."""

    MIME: Final[str] = "application/x-lzip"
    EXTENSION: Final[str] = "lz"

    SIGNATURE: Final = bytes([0x4C, 0x5A, 0x49, 0x50])

    def __init__(self) -> None:
        """Initialize the Lz matcher."""
        super().__init__(mime=Lz.MIME, extension=Lz.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the Lz signature."""
        return buf[:4] == Lz.SIGNATURE


class Elf(Type):
    """Implements the Elf archive type matcher."""

    MIME: Final[str] = "application/x-executable"
    EXTENSION: Final[str] = "elf"

    SIGNATURE: Final = bytes([0x7F, 0x45, 0x4C, 0x46])

    def __init__(self) -> None:
        """Initialize the Elf matcher."""
        super().__init__(mime=Elf.MIME, extension=Elf.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the Elf signature."""
        return buf[:4] == Elf.SIGNATURE


class Lz4(Type):
    """Implements the Lz4 archive type matcher."""

    MIME: Final[str] = "application/x-lz4"
    EXTENSION: Final[str] = "lz4"

    SIGNATURE: Final = bytes([0x04, 0x22, 0x4D, 0x18])

    def __init__(self) -> None:
        """Initialize the Lz4 matcher."""
        super().__init__(mime=Lz4.MIME, extension=Lz4.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the Lz4 signature."""
        return buf[:4] == Lz4.SIGNATURE


class Br(Type):
    """Implements the Br image type matcher."""

    MIME: Final[str] = "application/x-brotli"
    EXTENSION: Final[str] = "br"

    SIGNATURE: Final = bytearray([0xCE, 0xB2, 0xCF, 0x81])

    def __init__(self) -> None:
        """Initialize the Br matcher."""
        super().__init__(mime=Br.MIME, extension=Br.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the Br signature."""
        return buf[:4] == Br.SIGNATURE


class Rpm(Type):
    """Implements the Rpm image type matcher."""

    MIME: Final[str] = "application/x-rpm"
    EXTENSION: Final[str] = "rpm"

    SIGNATURE: Final = bytearray([0xED, 0xAB, 0xEE, 0xDB])

    def __init__(self) -> None:
        """Initialize the Rpm matcher."""
        super().__init__(mime=Rpm.MIME, extension=Rpm.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer starts with the Rpm signature."""
        return buf[:4] == Rpm.SIGNATURE


class Zstd(Type):
    """Implements the Zstd archive type matcher.

    https://github.com/facebook/zstd/blob/dev/doc/zstd_compression_format.md.
    """

    MIME: Final[str] = "application/zstd"
    EXTENSION: Final[str] = "zst"
    MAGIC_SKIPPABLE_START: Final = 0x184D2A50
    MAGIC_SKIPPABLE_MASK: Final = 0xFFFFFFF0
    FRAME_MIN_LENGTH: Final = 3
    SKIPPABLE_HEADER_SIZE: Final = 8
    FRAME_FIRST_BYTES: Final = (0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28)
    FRAME_TAIL: Final = bytes([0xB5, 0x2F, 0xFD])

    def __init__(self) -> None:
        """Initialize the Zstd matcher."""
        super().__init__(mime=Zstd.MIME, extension=Zstd.EXTENSION)

    @staticmethod
    def _to_little_endian_int(buf: bytes | bytearray) -> int:
        """Unpack a 4-byte little-endian buffer into an int."""
        value: int = struct.unpack("<L", buf)[0]
        return value

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the buffer is a Zstandard frame."""
        # Zstandard compressed data is made of one or more frames.
        # There are two frame formats defined by Zstandard:
        # Zstandard frames and Skippable frames.
        # See more details from
        # https://tools.ietf.org/id/draft-kucherawy-dispatch-zstd-00.html#rfc.section.2
        is_zstd = len(buf) > Zstd.FRAME_MIN_LENGTH and buf[0] in Zstd.FRAME_FIRST_BYTES and buf[1:4] == Zstd.FRAME_TAIL
        if is_zstd:
            return True
        # skippable frames
        if len(buf) < Zstd.SKIPPABLE_HEADER_SIZE:
            return False
        magic = self._to_little_endian_int(buf[:4]) & Zstd.MAGIC_SKIPPABLE_MASK
        if magic == Zstd.MAGIC_SKIPPABLE_START:
            user_data_len = self._to_little_endian_int(buf[4:8])
            if len(buf) < Zstd.SKIPPABLE_HEADER_SIZE + user_data_len:
                return False
            next_frame = buf[Zstd.SKIPPABLE_HEADER_SIZE + user_data_len :]
            return self.match(next_frame)
        return False
