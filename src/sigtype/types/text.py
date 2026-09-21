import re
from typing import Final

from sigtype._compat import override
from sigtype.text import looks_like_text
from sigtype.types.base import Type

# Everything allowed before the root element of an XML document: BOM, whitespace, declaration, comments and DOCTYPE.
_XML_ROOT: Final = re.compile(
    rb"\A(?:\xef\xbb\xbf)?\s*"
    rb"(?:<\?xml[^>]*\?>\s*)?"
    rb"(?:<!--.*?-->\s*)*"
    rb"(?:<!DOCTYPE[^>\[]*(?:\[.*?\][^>]*)?>\s*)?"
    rb"(?:<!--.*?-->\s*)*"
    rb"<(?P<name>[A-Za-z_][\w.-]*)[\s/>]",
    re.DOTALL,
)

# RFC 5322 header field: printable US-ASCII name (no colon) followed by a colon.
_HEADER_FIELD: Final = re.compile(rb"([!-9;-~]+):")
_HEADERS_END: Final = re.compile(rb"\r?\n\r?\n")
_MESSAGE_HEADERS: Final = frozenset(
    {
        b"received",
        b"return-path",
        b"delivered-to",
        b"from",
        b"to",
        b"cc",
        b"reply-to",
        b"date",
        b"subject",
        b"message-id",
        b"mime-version",
    },
)
_MIN_MESSAGE_HEADERS: Final = 2

# Markdown constructs that are hard to mistake for something else. Headings (`# ...`) and lists (`- ...`) are
# left out on purpose: they are just as common in shell scripts and YAML, where `#` starts a comment.
_MARKDOWN: Final = re.compile(
    rb"^(?:```|~~~)"  # fenced code block
    rb"|\]\((?:https?://|mailto:|#|/|\./|\.\./)[^)\s]*\)"  # inline link or image
    rb"|(?<![\w*])\*\*(?=\S)[^*\n]+?(?<=\S)\*\*(?![\w*])",  # bold text
    re.MULTILINE,
)


def _xml_root(buf: bytes | bytearray) -> bytes | None:
    found = _XML_ROOT.match(buf)
    return found.group("name") if found is not None else None


class Svg(Type):
    """Implements the SVG image type matcher."""

    MIME: Final[str] = "image/svg+xml"
    EXTENSION: Final[str] = "svg"

    def __init__(self) -> None:
        """Initialize the Svg matcher."""
        super().__init__(mime=Svg.MIME, extension=Svg.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match an XML document whose root element is `svg`."""
        return _xml_root(buf) == b"svg"


class Fb2(Type):
    """Implements the FictionBook 2 e-book type matcher."""

    MIME: Final[str] = "application/x-fictionbook+xml"
    EXTENSION: Final[str] = "fb2"

    def __init__(self) -> None:
        """Initialize the Fb2 matcher."""
        super().__init__(mime=Fb2.MIME, extension=Fb2.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match an XML document whose root element is `FictionBook`."""
        return _xml_root(buf) == b"FictionBook"


class Eml(Type):
    """Implements the RFC 5322 e-mail message type matcher."""

    MIME: Final[str] = "message/rfc822"
    EXTENSION: Final[str] = "eml"

    def __init__(self) -> None:
        """Initialize the Eml matcher."""
        super().__init__(mime=Eml.MIME, extension=Eml.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match a header block made of well-formed header fields, several of them typical of e-mail."""
        if _HEADER_FIELD.match(buf) is None:
            return False

        end = _HEADERS_END.search(buf)
        header_block = bytes(buf[: end.start()] if end is not None else buf)
        if b"\x00" in header_block:
            return False

        names: set[bytes] = set()
        lines = header_block.splitlines()
        for index, line in enumerate(lines):
            if line[:1] in (b" ", b"\t"):  # folded continuation of the previous field
                continue
            field = _HEADER_FIELD.match(line)
            if field is not None:
                names.add(field.group(1).lower())
            elif end is not None or index != len(lines) - 1:
                return False
            # otherwise the signature window cut the last line short, which is fine

        return len(names & _MESSAGE_HEADERS) >= _MIN_MESSAGE_HEADERS


class Txt(Type):
    """Implements the plain text type matcher. Matches any non-empty input that looks like text."""

    MIME: Final[str] = "text/plain"
    EXTENSION: Final[str] = "txt"

    def __init__(self) -> None:
        """Initialize the Txt matcher."""
        super().__init__(mime=Txt.MIME, extension=Txt.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match text, see `sigtype.is_text` for what counts as text."""
        return len(buf) > 0 and looks_like_text(buf)


class Md(Type):
    """Implements the Markdown type matcher. A heuristic: text using unambiguous Markdown syntax."""

    MIME: Final[str] = "text/markdown"
    EXTENSION: Final[str] = "md"

    def __init__(self) -> None:
        """Initialize the Md matcher."""
        super().__init__(mime=Md.MIME, extension=Md.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match text containing a fenced code block, a link to a URL or path, or bold text."""
        return looks_like_text(buf) and _MARKDOWN.search(buf) is not None
