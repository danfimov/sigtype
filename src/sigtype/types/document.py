from typing import ClassVar, Final, cast

from sigtype._compat import override
from sigtype.types.base import Type
from sigtype.types.cfb import OLE_SIGNATURE, read_root_entry_names
from sigtype.utils import ReadAt, SourceReader

_ZIP_LOCAL_FILE_HEADER: Final = b"PK\x03\x04"
_ZIP_SEARCH_RANGE: Final = 6000
_ZIP_SIGNATURE_LENGTH: Final = 4
_MIMETYPE_ENTRY_OFFSET: Final = 0x1E
_MIMETYPE_CONTENT_OFFSET: Final = 0x26
_OOXML_ENTRIES_TO_CHECK: Final = 8
_ZIP_FILENAME_OFFSET: Final = 30
_ZIP_FILENAME_LENGTH_OFFSET: Final = 26
_ZIP_FILENAME_LENGTH_SIZE: Final = 2
_ZIP_ENTRIES_TO_SCAN: Final = 16
_ZIP_FILENAME_PREFIX_SIZE: Final = 8
_ZIP_ENTRIES_MEMO_KEY: Final = "zip.entries"
_OFD_ROOT_ENTRY: Final = b"OFD.xml"

# A scanned local file header: length of the filename and its first bytes
_ZipEntry = tuple[int, bytes]


class ZippedDocumentBase(Type):
    """Base matcher for document formats packaged as ZIP archives."""

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match documents starting with a ZIP local file header signature."""
        if not self.compare_bytes(buf, _ZIP_LOCAL_FILE_HEADER, 0):
            return False

        return self.match_document(buf)

    def match_document(self, buf: bytes | bytearray) -> bool:
        """Match the document-specific signature. Implemented by subclasses."""
        raise NotImplementedError

    def compare_bytes(
        self,
        buf: bytes | bytearray,
        subslice: bytes,
        start_offset: int,
    ) -> bool:
        """Check whether `buf` contains `subslice` at the given offset."""
        sl = len(subslice)

        if start_offset + sl > len(buf):
            return False

        return buf[start_offset : start_offset + sl] == subslice


class OpenDocument(ZippedDocumentBase):
    """Base matcher for OpenDocument formats (ODT, ODS, ODP)."""

    @override
    def match_document(self, buf: bytes | bytearray) -> bool:
        """Match by checking the ZIP-embedded mimetype file and its content."""
        # Check if first file in archive is the identifying file
        if not self.compare_bytes(buf, b"mimetype", _MIMETYPE_ENTRY_OFFSET):
            return False

        # Check content of mimetype file if it matches current mime
        return self.compare_bytes(
            buf,
            bytes(self.mime, "ASCII"),
            _MIMETYPE_CONTENT_OFFSET,
        )


def _search_signature(buf: bytes | bytearray, start: int, range_num: int) -> int:
    """Search for the ZIP local file header signature within a byte range."""
    end = min(start + range_num, len(buf))

    if start >= end:
        return -1

    try:
        return buf.index(_ZIP_LOCAL_FILE_HEADER, start, end)
    except ValueError:
        return -1


def _scan_zip_entries(buf: bytes | bytearray) -> list[_ZipEntry]:
    entries: list[_ZipEntry] = []
    idx = 0
    for _i in range(_ZIP_ENTRIES_TO_SCAN):
        length_start = idx + _ZIP_FILENAME_LENGTH_OFFSET
        name_length = int.from_bytes(buf[length_start : length_start + _ZIP_FILENAME_LENGTH_SIZE], "little")
        name_start = idx + _ZIP_FILENAME_OFFSET
        entries.append((name_length, bytes(buf[name_start : name_start + _ZIP_FILENAME_PREFIX_SIZE])))

        # Search for next file header
        idx = _search_signature(buf, idx + _ZIP_SIGNATURE_LENGTH, _ZIP_SEARCH_RANGE)
        if idx == -1:
            break
    return entries


def _zip_entries(buf: bytes | bytearray, read_at: ReadAt | None) -> list[_ZipEntry]:
    """Scan the leading local file headers of a ZIP archive.

    Several matchers (docx, xlsx, pptx, ofd) look at the same entries, so when `read_at` is a `SourceReader`
    the result is remembered on it and the scan runs once per input.
    """
    if not isinstance(read_at, SourceReader):
        return _scan_zip_entries(buf)

    cached = read_at.memo.get(_ZIP_ENTRIES_MEMO_KEY)
    if cached is not None:
        return cast("list[_ZipEntry]", cached)

    entries = _scan_zip_entries(buf)
    read_at.memo[_ZIP_ENTRIES_MEMO_KEY] = entries
    return entries


class ZipEntryDocument(ZippedDocumentBase):
    """Base matcher for ZIP based formats identified by the names of the entries in the archive."""

    # Only used to share the scan of the archive between matchers through the reader, no data past the
    # signature window is read.
    needs_read_at: ClassVar[bool] = True

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match using only the leading bytes."""
        return self.match_at(buf, None)

    @override
    def match_at(self, buf: bytes | bytearray, read_at: ReadAt | None) -> bool:
        """Match documents starting with a ZIP local file header signature and the expected entries."""
        if not self.compare_bytes(buf, _ZIP_LOCAL_FILE_HEADER, 0):
            return False

        return self.match_entries(_zip_entries(buf, read_at))

    def match_entries(self, entries: list[_ZipEntry]) -> bool:
        """Match by the scanned archive entries. Implemented by subclasses."""
        raise NotImplementedError


class OfficeOpenXml(ZipEntryDocument):
    """Base matcher for Office Open XML formats (DOCX, XLSX, PPTX)."""

    # Directory that identifies the format, e.g. `word/` for DOCX
    ENTRY_PREFIX: ClassVar[bytes] = b""

    @override
    def match_entries(self, entries: list[_ZipEntry]) -> bool:
        """Match by inspecting the ZIP-embedded entry filenames.

        Real-world OOXML files may carry unrelated entries (e.g. `[trash]/...`) ahead of the identifying `word/`, `ppt/`
        or `xl/` entry, so every entry in the checked range is inspected instead of only the first one.
        """
        return any(prefix.startswith(self.ENTRY_PREFIX) for _, prefix in entries[:_OOXML_ENTRIES_TO_CHECK])


class Ofd(ZipEntryDocument):
    """Implements the OFD (Open Fixed-layout Document, GB/T 33190) type matcher."""

    MIME: Final[str] = "application/ofd"
    EXTENSION: Final[str] = "ofd"

    def __init__(self) -> None:
        """Initialize the Ofd matcher."""
        super().__init__(mime=Ofd.MIME, extension=Ofd.EXTENSION)

    @override
    def match_entries(self, entries: list[_ZipEntry]) -> bool:
        """Match by looking for the `OFD.xml` root entry among the first ZIP entries."""
        return any(length == len(_OFD_ROOT_ENTRY) and prefix.startswith(_OFD_ROOT_ENTRY) for length, prefix in entries)


class OleDocument(Type):
    """Base matcher for formats stored in a Compound File Binary (OLE2) container.

    All of them share one container signature, so the type is decided by the streams found under the root of the
    container. When the container directory cannot be read (e.g. it lies past the available data and no `read_at`
    is given), legacy byte-offset heuristics are used instead where a subclass provides them.
    """

    needs_read_at: ClassVar[bool] = True

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match using only the leading bytes."""
        return self.match_at(buf, None)

    @override
    def match_at(self, buf: bytes | bytearray, read_at: ReadAt | None) -> bool:
        """Match by the streams stored in the container, reading the directory on demand."""
        if buf[:8] != OLE_SIGNATURE:
            return False

        names = read_root_entry_names(buf, read_at)
        if names is None:
            return self.match_signature(buf)
        return self.match_entries(names)

    def match_entries(self, names: frozenset[str]) -> bool:
        """Match by the names of the root's direct children. Implemented by subclasses."""
        raise NotImplementedError

    def match_signature(self, buf: bytes | bytearray) -> bool:  # noqa: ARG002
        """Fallback used when the container directory is unreadable. Matches nothing by default."""
        return False


_DOC_MIN_SIZE: Final = 515
_DOC_SUBHEADER_OFFSET: Final = 512
_DOC_SUBHEADER_END: Final = 516
_DOC_SUBHEADER: Final = b"\xec\xa5\xc1\x00"
_DOC_MARKER_MIN_SIZE: Final = 2142
_DOC_MARKER_START: Final = 2075
_DOC_MARKER_END: Final = 2142
_DOC_MARKER: Final = b"\x00\x0a\x00\x00\x00MSWordDoc\x00\x10\x00\x00\x00Word.Document.8\x00\xf49\xb2q"
_DOC_UTF16_MARKER_START: Final = 0x580
_DOC_UTF16_MARKER_END: Final = 0x598
_DOC_UTF16_MARKER: Final = b"W\0o\0r\0d\0D\0o\0c\0u\0m\0e\0n\0t\0"
_DOC_ROOT_ENTRY_MIN_SIZE: Final = 663
_DOC_ROOT_ENTRY_END: Final = 531
_DOC_ROOT_ENTRY: Final = b"R\x00o\x00o\x00t\x00 \x00E\x00n\x00t\x00r\x00y"
_DOC_WORDDOCUMENT_START: Final = 640
_DOC_WORDDOCUMENT_END: Final = 663
_DOC_WORDDOCUMENT: Final = b"W\x00o\x00r\x00d\x00D\x00o\x00c\x00u\x00m\x00e\x00n\x00t"


class Doc(OleDocument):
    """Implements the Microsoft Word (Office 97-2003) document type matcher."""

    MIME: Final[str] = "application/msword"
    EXTENSION: Final[str] = "doc"

    def __init__(self) -> None:
        """Initialize the Doc matcher."""
        super().__init__(mime=Doc.MIME, extension=Doc.EXTENSION)

    @override
    def match_entries(self, names: frozenset[str]) -> bool:
        """Match the Word document stream."""
        return "WordDocument" in names

    @override
    def match_signature(self, buf: bytes | bytearray) -> bool:
        """Match the OLE-based Word 97-2003 document signature."""
        if len(buf) > _DOC_MIN_SIZE and buf[0:8] == OLE_SIGNATURE:
            if buf[_DOC_SUBHEADER_OFFSET:_DOC_SUBHEADER_END] == _DOC_SUBHEADER:
                return True
            if len(buf) > _DOC_MARKER_MIN_SIZE and (
                _DOC_MARKER in buf[_DOC_MARKER_START:_DOC_MARKER_END]
                or _DOC_UTF16_MARKER in buf[_DOC_UTF16_MARKER_START:_DOC_UTF16_MARKER_END]
            ):
                return True
            if (
                len(buf) > _DOC_ROOT_ENTRY_MIN_SIZE
                and buf[_DOC_SUBHEADER_OFFSET:_DOC_ROOT_ENTRY_END] == _DOC_ROOT_ENTRY
                and buf[_DOC_WORDDOCUMENT_START:_DOC_WORDDOCUMENT_END] == _DOC_WORDDOCUMENT
            ):
                return True

        return False


class Docx(OfficeOpenXml):
    """Implements the Microsoft Word OOXML (Office 2007+) document type matcher."""

    MIME: Final[str] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    EXTENSION: Final[str] = "docx"
    ENTRY_PREFIX: ClassVar[bytes] = b"word/"

    def __init__(self) -> None:
        """Initialize the Docx matcher."""
        super().__init__(mime=Docx.MIME, extension=Docx.EXTENSION)


class Odt(OpenDocument):
    """Implements the OpenDocument Text document type matcher."""

    MIME: Final[str] = "application/vnd.oasis.opendocument.text"
    EXTENSION: Final[str] = "odt"

    def __init__(self) -> None:
        """Initialize the Odt matcher."""
        super().__init__(mime=Odt.MIME, extension=Odt.EXTENSION)


_XLS_MIN_SIZE: Final = 520
_XLS_MARKER1: Final = b"\xfd\xff\xff\xff"
_XLS_MARKER1_BYTE_OFFSET: Final = 518
_XLS_MARKER1_BYTE_A: Final = 0x00
_XLS_MARKER1_BYTE_B: Final = 0x02
_XLS_MARKER2_END: Final = 520
_XLS_MARKER2: Final = b"\x09\x08\x10\x00\x00\x06\x05\x00"
_XLS_CALC_MIN_SIZE: Final = 2095
_XLS_CALC_MARKER_START: Final = 1568
_XLS_CALC_MARKER_END: Final = 2095
_XLS_CALC_MARKER: Final = b"\xe2\x00\x00\x00\x5c\x00\x70\x00\x04\x00\x00Calc"


class Xls(OleDocument):
    """Implements the Microsoft Excel (Office 97-2003) document type matcher."""

    MIME: Final[str] = "application/vnd.ms-excel"
    EXTENSION: Final[str] = "xls"

    def __init__(self) -> None:
        """Initialize the Xls matcher."""
        super().__init__(mime=Xls.MIME, extension=Xls.EXTENSION)

    @override
    def match_entries(self, names: frozenset[str]) -> bool:
        """Match the workbook stream (`Book` is used by Excel 5.0/95)."""
        return "Workbook" in names or "Book" in names

    @override
    def match_signature(self, buf: bytes | bytearray) -> bool:
        """Match the OLE-based Excel 97-2003 document signature."""
        if len(buf) > _XLS_MIN_SIZE and buf[0:8] == OLE_SIGNATURE:
            if buf[_DOC_SUBHEADER_OFFSET:_DOC_SUBHEADER_END] == _XLS_MARKER1 and (
                buf[_XLS_MARKER1_BYTE_OFFSET] == _XLS_MARKER1_BYTE_A
                or buf[_XLS_MARKER1_BYTE_OFFSET] == _XLS_MARKER1_BYTE_B
            ):
                return True
            if buf[_DOC_SUBHEADER_OFFSET:_XLS_MARKER2_END] == _XLS_MARKER2:
                return True
            if len(buf) > _XLS_CALC_MIN_SIZE and _XLS_CALC_MARKER in buf[_XLS_CALC_MARKER_START:_XLS_CALC_MARKER_END]:
                return True

        return False


class Xlsx(OfficeOpenXml):
    """Implements the Microsoft Excel OOXML (Office 2007+) document type matcher."""

    MIME: Final[str] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    EXTENSION: Final[str] = "xlsx"
    ENTRY_PREFIX: ClassVar[bytes] = b"xl/"

    def __init__(self) -> None:
        """Initialize the Xlsx matcher."""
        super().__init__(mime=Xlsx.MIME, extension=Xlsx.EXTENSION)


class Ods(OpenDocument):
    """Implements the OpenDocument Spreadsheet document type matcher."""

    MIME: Final[str] = "application/vnd.oasis.opendocument.spreadsheet"
    EXTENSION: Final[str] = "ods"

    def __init__(self) -> None:
        """Initialize the Ods matcher."""
        super().__init__(mime=Ods.MIME, extension=Ods.EXTENSION)


_PPT_MIN_SIZE: Final = 524
_PPT_MARKER_A: Final = b"\xa0\x46\x1d\xf0"
_PPT_MARKER_B: Final = b"\x00\x6e\x1e\xf0"
_PPT_MARKER_C: Final = b"\x0f\x00\xe8\x03"
_PPT_MARKER_D: Final = b"\xfd\xff\xff\xff"
_PPT_MARKER_D_TAIL_START: Final = 522
_PPT_MARKER_D_TAIL_END: Final = 524
_PPT_MARKER_D_TAIL: Final = b"\x00\x00"
_PPT_TITLE_MIN_SIZE: Final = 2096
_PPT_TITLE_START: Final = 2072
_PPT_TITLE_END: Final = 2096
_PPT_TITLE: Final = b"\x00\xb9\x29\xe8\x11\x00\x00\x00MS PowerPoint 97"


class Ppt(OleDocument):
    """Implements the Microsoft PowerPoint (Office 97-2003) document type matcher."""

    MIME: Final[str] = "application/vnd.ms-powerpoint"
    EXTENSION: Final[str] = "ppt"

    def __init__(self) -> None:
        """Initialize the Ppt matcher."""
        super().__init__(mime=Ppt.MIME, extension=Ppt.EXTENSION)

    @override
    def match_entries(self, names: frozenset[str]) -> bool:
        """Match the PowerPoint document stream."""
        return "PowerPoint Document" in names

    @override
    def match_signature(self, buf: bytes | bytearray) -> bool:
        """Match the OLE-based PowerPoint 97-2003 document signature."""
        if len(buf) > _PPT_MIN_SIZE and buf[0:8] == OLE_SIGNATURE:
            if buf[_DOC_SUBHEADER_OFFSET:_DOC_SUBHEADER_END] == _PPT_MARKER_A:
                return True
            if buf[_DOC_SUBHEADER_OFFSET:_DOC_SUBHEADER_END] == _PPT_MARKER_B:
                return True
            if buf[_DOC_SUBHEADER_OFFSET:_DOC_SUBHEADER_END] == _PPT_MARKER_C:
                return True
            if (
                buf[_DOC_SUBHEADER_OFFSET:_DOC_SUBHEADER_END] == _PPT_MARKER_D
                and buf[_PPT_MARKER_D_TAIL_START:_PPT_MARKER_D_TAIL_END] == _PPT_MARKER_D_TAIL
            ):
                return True
            if len(buf) > _PPT_TITLE_MIN_SIZE and buf[_PPT_TITLE_START:_PPT_TITLE_END] == _PPT_TITLE:
                return True

        return False


class Pptx(OfficeOpenXml):
    """Implements the Microsoft PowerPoint OOXML (Office 2007+) matcher."""

    MIME: Final[str] = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    EXTENSION: Final[str] = "pptx"
    ENTRY_PREFIX: ClassVar[bytes] = b"ppt/"

    def __init__(self) -> None:
        """Initialize the Pptx matcher."""
        super().__init__(mime=Pptx.MIME, extension=Pptx.EXTENSION)


class Odp(OpenDocument):
    """Implements the OpenDocument Presentation document type matcher."""

    MIME: Final[str] = "application/vnd.oasis.opendocument.presentation"
    EXTENSION: Final[str] = "odp"

    def __init__(self) -> None:
        """Initialize the Odp matcher."""
        super().__init__(mime=Odp.MIME, extension=Odp.EXTENSION)


class Msg(OleDocument):
    """Implements the Microsoft Outlook message (.msg) type matcher."""

    MIME: Final[str] = "application/vnd.ms-outlook"
    EXTENSION: Final[str] = "msg"

    def __init__(self) -> None:
        """Initialize the Msg matcher."""
        super().__init__(mime=Msg.MIME, extension=Msg.EXTENSION)

    @override
    def match_entries(self, names: frozenset[str]) -> bool:
        """Match the MAPI property streams every Outlook message carries."""
        return "__properties_version1.0" in names or any(name.startswith("__substg1.0_") for name in names)


_MOBI_TYPE_OFFSET: Final = 60
_MOBI_TYPE: Final = b"BOOKMOBI"


class Mobi(Type):
    """Implements the Mobipocket e-book type matcher (also used by Kindle AZW/AZW3 files)."""

    MIME: Final[str] = "application/x-mobipocket-ebook"
    EXTENSION: Final[str] = "mobi"

    def __init__(self) -> None:
        """Initialize the Mobi matcher."""
        super().__init__(mime=Mobi.MIME, extension=Mobi.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the PalmDB type and creator fields that identify Mobipocket books."""
        return buf[_MOBI_TYPE_OFFSET : _MOBI_TYPE_OFFSET + len(_MOBI_TYPE)] == _MOBI_TYPE


_DJVU_MAGIC: Final = b"AT&TFORM"
_DJVU_FORM_OFFSET: Final = 12
_DJVU_FORMS: Final = (b"DJVU", b"DJVM")


class Djvu(Type):
    """Implements the DjVu document type matcher."""

    MIME: Final[str] = "image/vnd.djvu"
    EXTENSION: Final[str] = "djvu"

    def __init__(self) -> None:
        """Initialize the Djvu matcher."""
        super().__init__(mime=Djvu.MIME, extension=Djvu.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the IFF magic followed by a single page (DJVU) or multi-page (DJVM) form."""
        return buf[: len(_DJVU_MAGIC)] == _DJVU_MAGIC and buf[_DJVU_FORM_OFFSET : _DJVU_FORM_OFFSET + 4] in _DJVU_FORMS
