import codecs
import re
from typing import Final

from sigtype.utils import SIGNATURE_SIZE

_UTF8_BOM: Final = b"\xef\xbb\xbf"
_UTF16_BOMS: Final = (b"\xff\xfe", b"\xfe\xff")
_UTF32_BOMS: Final = (b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff")

# Control characters that do not occur in text. Tab, line feed, vertical tab, form feed, carriage return and
# escape (used by ANSI sequences) are allowed.
_BINARY_BYTES: Final = re.compile(rb"[\x00-\x08\x0e-\x1a\x1c-\x1f]")
_BINARY_CHARS: Final = re.compile(r"[\x00-\x08\x0e-\x1a\x1c-\x1f]")


def looks_like_text(buf: bytes | bytearray) -> bool:
    """Check whether the leading bytes of an input look like human readable text.

    Text is UTF-8 (with or without BOM) or UTF-16/UTF-32 with a BOM, free of NUL bytes and of control characters
    other than whitespace and escape. An empty input is text.

    Args:
        buf: the first SIGNATURE_SIZE bytes of the input.

    Returns:
        True if the bytes look like text. Otherwise False.
    """
    if not buf:
        return True

    # A full-size buffer may end in the middle of a multi-byte character, a shorter one is the whole input.
    final = len(buf) < SIGNATURE_SIZE

    if buf[:4] in _UTF32_BOMS:
        return _decodes_as_text(buf, "utf-32", final=final)
    if buf[:2] in _UTF16_BOMS:
        return _decodes_as_text(buf, "utf-16", final=final)

    if _BINARY_BYTES.search(buf) is not None:
        return False

    if buf[:3] == _UTF8_BOM:
        buf = buf[3:]
    try:
        codecs.getincrementaldecoder("utf-8")().decode(bytes(buf), final=final)
    except UnicodeDecodeError:
        return False
    return True


def _decodes_as_text(buf: bytes | bytearray, encoding: str, *, final: bool) -> bool:
    try:
        text = codecs.getincrementaldecoder(encoding)().decode(bytes(buf), final=final)
    except UnicodeDecodeError:
        return False
    return _BINARY_CHARS.search(text) is None
