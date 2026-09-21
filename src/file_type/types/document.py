from typing import Final, override

from file_type.types.base import Type

_ZIP_SEARCH_RANGE: Final = 6000
_ZIP_SIGNATURE_LENGTH: Final = 4
_MIMETYPE_ENTRY_OFFSET: Final = 0x1E
_MIMETYPE_CONTENT_OFFSET: Final = 0x26
_OOXML_ENTRIES_TO_CHECK: Final = 4
_OOXML_FILENAME_OFFSET: Final = 30


class ZippedDocumentBase(Type):
    """Base matcher for document formats packaged as ZIP archives."""

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match documents starting with a ZIP local file header signature."""
        # start by checking for ZIP local file header signature
        idx = self.search_signature(buf, 0, _ZIP_SEARCH_RANGE)
        if idx != 0:
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

    def search_signature(
        self,
        buf: bytes | bytearray,
        start: int,
        range_num: int,
    ) -> int:
        """Search for the ZIP local file header signature within a byte range."""
        signature = b"PK\x03\x04"
        length = len(buf)

        end = start + range_num
        end = min(end, length)

        if start >= end:
            return -1

        try:
            return buf.index(signature, start, end)
        except ValueError:
            return -1


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


class OfficeOpenXml(ZippedDocumentBase):
    """Base matcher for Office Open XML formats (DOCX, XLSX, PPTX)."""

    @override
    def match_document(self, buf: bytes | bytearray) -> bool:
        """Match by inspecting the ZIP-embedded entry filenames."""
        # Check if first file in archive is the identifying file
        ft = self.match_filename(buf, _MIMETYPE_ENTRY_OFFSET)
        if ft:
            return ft

        # Otherwise check that the fist file is one of these
        if (
            not self.compare_bytes(buf, b"[Content_Types].xml", _MIMETYPE_ENTRY_OFFSET)
            and not self.compare_bytes(buf, b"_rels/.rels", _MIMETYPE_ENTRY_OFFSET)
            and not self.compare_bytes(buf, b"docProps", _MIMETYPE_ENTRY_OFFSET)
        ):
            return False

        # Loop through next 3 files and check if they match
        # NOTE: OpenOffice/Libreoffice orders ZIP entry differently,
        # so check the 4th file
        # https://github.com/h2non/filetype/blob/d730d98ad5c990883148485b6fd5adbdd378364a/matchers/document.go#L134
        idx = 0
        for _i in range(_OOXML_ENTRIES_TO_CHECK):
            # Search for next file header
            idx = self.search_signature(
                buf,
                idx + _ZIP_SIGNATURE_LENGTH,
                _ZIP_SEARCH_RANGE,
            )
            if idx == -1:
                return False

            # Filename is at file header + 30
            ft = self.match_filename(buf, idx + _OOXML_FILENAME_OFFSET)
            if ft:
                return ft
        return False

    def match_filename(self, buf: bytes | bytearray, offset: int) -> bool:
        """Determine the OOXML kind from the entry filename at `offset`."""
        if self.compare_bytes(buf, b"word/", offset):
            return self.mime == ("application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        if self.compare_bytes(buf, b"ppt/", offset):
            return self.mime == ("application/vnd.openxmlformats-officedocument.presentationml.presentation")
        if self.compare_bytes(buf, b"xl/", offset):
            return self.mime == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        return False


_OLE_SIGNATURE: Final = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"

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


class Doc(Type):
    """Implements the Microsoft Word (Office 97-2003) document type matcher."""

    MIME: Final[str] = "application/msword"
    EXTENSION: Final[str] = "doc"

    def __init__(self) -> None:
        """Initialize the Doc matcher."""
        super().__init__(mime=Doc.MIME, extension=Doc.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the OLE-based Word 97-2003 document signature."""
        if len(buf) > _DOC_MIN_SIZE and buf[0:8] == _OLE_SIGNATURE:
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


class Xls(Type):
    """Implements the Microsoft Excel (Office 97-2003) document type matcher."""

    MIME: Final[str] = "application/vnd.ms-excel"
    EXTENSION: Final[str] = "xls"

    def __init__(self) -> None:
        """Initialize the Xls matcher."""
        super().__init__(mime=Xls.MIME, extension=Xls.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the OLE-based Excel 97-2003 document signature."""
        if len(buf) > _XLS_MIN_SIZE and buf[0:8] == _OLE_SIGNATURE:
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


class Ppt(Type):
    """Implements the Microsoft PowerPoint (Office 97-2003) document type matcher."""

    MIME: Final[str] = "application/vnd.ms-powerpoint"
    EXTENSION: Final[str] = "ppt"

    def __init__(self) -> None:
        """Initialize the Ppt matcher."""
        super().__init__(mime=Ppt.MIME, extension=Ppt.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the OLE-based PowerPoint 97-2003 document signature."""
        if len(buf) > _PPT_MIN_SIZE and buf[0:8] == _OLE_SIGNATURE:
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
