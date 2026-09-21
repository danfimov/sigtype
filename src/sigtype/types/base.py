class Type:
    """Represents the file type object.

    Inherited by specific file type matchers. Provides convenient
    accessor and helper methods.
    """

    def __init__(self, mime: str, extension: str) -> None:
        """Initialize with the MIME type and file extension it matches."""
        self.__mime = mime
        self.__extension = extension

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

    def is_mime(self, mime: str) -> bool:
        """Check whether the given MIME type matches this type."""
        return self.__mime == mime

    def match(self, buf: bytes | bytearray) -> bool:
        """Check whether the given buffer matches this type's signature."""
        raise NotImplementedError
