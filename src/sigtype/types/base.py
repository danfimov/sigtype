from typing import ClassVar

from sigtype.utils import ReadAt


class Type:
    """Represents the file type object.

    Inherited by specific file type matchers. Provides convenient
    accessor and helper methods.
    """

    # Set to True by matchers that need to look past the first SIGNATURE_SIZE bytes. Such matchers
    # are invoked through `match_at()` and receive a random access reader.
    needs_read_at: ClassVar[bool] = False

    def __init__(self, mime: str, extension: str, aliases: tuple[str, ...] = ()) -> None:
        """Initialize with the MIME type and file extension it matches.

        Args:
            mime: canonical MIME type, returned as `mime`.
            extension: file extension without the dot.
            aliases: other MIME types that still identify this type, e.g. deprecated ones.
                They are accepted by `is_mime()` and `get_type()`, but never returned by `guess()`.
        """
        self.__mime = mime
        self.__extension = extension
        self.__aliases = aliases
        # Copy of the class level flag: guess() checks it for every matcher on every call, and an instance
        # attribute is much cheaper to read than a class variable in compiled (mypyc) builds.
        self.uses_read_at: bool = type(self).needs_read_at

    @property
    def mime(self) -> str:
        """Return the MIME type string."""
        return self.__mime

    @property
    def extension(self) -> str:
        """Return the file extension string."""
        return self.__extension

    def is_extension(self, extension: str) -> bool:
        """Check whether the given extension matches this type."""
        return self.__extension == extension

    @property
    def aliases(self) -> tuple[str, ...]:
        """Return the alternative MIME types accepted for this type."""
        return self.__aliases

    def is_mime(self, mime: str) -> bool:
        """Check whether the given MIME type, or one of its aliases, matches this type."""
        return self.__mime == mime or mime in self.__aliases

    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the given buffer matches this type's signature."""
        raise NotImplementedError

    def match_at(self, buf: bytes | bytearray, read_at: ReadAt | None) -> bool:  # noqa: ARG002
        """Check whether the input matches, optionally reading past the signature bytes.

        Args:
            buf: the first SIGNATURE_SIZE bytes of the input.
            read_at: random access reader for the whole input, or None when unavailable.
                Matchers must fail gracefully (or fall back to `buf`) when it is None.

        Returns:
            True if the input matches this type's signature.
        """
        return self.match(buf)
