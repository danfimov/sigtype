from typing import Final

from file_type._compat import override
from file_type.types.base import Type

_WASM_SIGNATURE: Final = bytearray([0x00, 0x61, 0x73, 0x6D, 0x01, 0x00, 0x00, 0x00])


class Wasm(Type):
    """Implements the Wasm image type matcher."""

    MIME: Final[str] = "application/wasm"
    EXTENSION: Final[str] = "wasm"

    def __init__(self) -> None:
        """Initialize the Wasm matcher."""
        super().__init__(mime=Wasm.MIME, extension=Wasm.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the Wasm file signature."""
        return buf[:8] == _WASM_SIGNATURE
