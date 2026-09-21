from typing import Final, override

from file_type.types.base import Type

_MIDI_MIN_LENGTH: Final = 3
_MIDI_SIGNATURE: Final = (0x4D, 0x54, 0x68, 0x64)


class Midi(Type):
    """Implements the Midi audio type matcher."""

    MIME: Final[str] = "audio/midi"
    EXTENSION: Final[str] = "midi"

    def __init__(self) -> None:
        """Initialize the Midi matcher."""
        super().__init__(mime=Midi.MIME, extension=Midi.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the Midi file signature."""
        return (
            len(buf) > _MIDI_MIN_LENGTH
            and buf[0] == _MIDI_SIGNATURE[0]
            and buf[1] == _MIDI_SIGNATURE[1]
            and buf[2] == _MIDI_SIGNATURE[2]
            and buf[3] == _MIDI_SIGNATURE[3]
        )


_MP3_MIN_LENGTH: Final = 2
_MP3_ID3_SIGNATURE: Final = (0x49, 0x44, 0x33)
_MP3_FRAME_SYNC: Final = 0xFF
_MP3_FRAME_SECOND_BYTES: Final = (0xE2, 0xE3, 0xF2, 0xF3, 0xFA, 0xFB)


class Mp3(Type):
    """Implements the MP3 audio type matcher."""

    MIME: Final[str] = "audio/mpeg"
    EXTENSION: Final[str] = "mp3"

    def __init__(self) -> None:
        """Initialize the Mp3 matcher."""
        super().__init__(mime=Mp3.MIME, extension=Mp3.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the MP3 file signature."""
        if len(buf) > _MP3_MIN_LENGTH:
            if buf[0] == _MP3_ID3_SIGNATURE[0] and buf[1] == _MP3_ID3_SIGNATURE[1] and buf[2] == _MP3_ID3_SIGNATURE[2]:
                return True

            if buf[0] == _MP3_FRAME_SYNC and buf[1] in _MP3_FRAME_SECOND_BYTES:
                # MPEG 2.5/2/1, with/without error protection
                return True
        return False


_M4A_MIN_LENGTH: Final = 10
_M4A_FTYP_SIGNATURE: Final = (0x66, 0x74, 0x79, 0x70, 0x4D, 0x34, 0x41)
_M4A_BARE_SIGNATURE: Final = (0x4D, 0x34, 0x41, 0x20)


class M4a(Type):
    """Implements the M4A audio type matcher."""

    MIME: Final[str] = "audio/mp4"
    EXTENSION: Final[str] = "m4a"

    def __init__(self) -> None:
        """Initialize the M4a matcher."""
        super().__init__(mime=M4a.MIME, extension=M4a.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the M4A file signature."""
        return len(buf) > _M4A_MIN_LENGTH and (
            (
                buf[4] == _M4A_FTYP_SIGNATURE[0]
                and buf[5] == _M4A_FTYP_SIGNATURE[1]
                and buf[6] == _M4A_FTYP_SIGNATURE[2]
                and buf[7] == _M4A_FTYP_SIGNATURE[3]
                and buf[8] == _M4A_FTYP_SIGNATURE[4]
                and buf[9] == _M4A_FTYP_SIGNATURE[5]
                and buf[10] == _M4A_FTYP_SIGNATURE[6]
            )
            or (
                buf[0] == _M4A_BARE_SIGNATURE[0]
                and buf[1] == _M4A_BARE_SIGNATURE[1]
                and buf[2] == _M4A_BARE_SIGNATURE[2]
                and buf[3] == _M4A_BARE_SIGNATURE[3]
            )
        )


_OGG_MIN_LENGTH: Final = 3
_OGG_SIGNATURE: Final = (0x4F, 0x67, 0x67, 0x53)


class Ogg(Type):
    """Implements the OGG audio type matcher."""

    MIME: Final[str] = "audio/ogg"
    EXTENSION: Final[str] = "ogg"

    def __init__(self) -> None:
        """Initialize the Ogg matcher."""
        super().__init__(mime=Ogg.MIME, extension=Ogg.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the OGG file signature."""
        return (
            len(buf) > _OGG_MIN_LENGTH
            and buf[0] == _OGG_SIGNATURE[0]
            and buf[1] == _OGG_SIGNATURE[1]
            and buf[2] == _OGG_SIGNATURE[2]
            and buf[3] == _OGG_SIGNATURE[3]
        )


_FLAC_MIN_LENGTH: Final = 3
_FLAC_SIGNATURE: Final = (0x66, 0x4C, 0x61, 0x43)


class Flac(Type):
    """Implements the FLAC audio type matcher."""

    MIME: Final[str] = "audio/x-flac"
    EXTENSION: Final[str] = "flac"

    def __init__(self) -> None:
        """Initialize the Flac matcher."""
        super().__init__(mime=Flac.MIME, extension=Flac.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the FLAC file signature."""
        return (
            len(buf) > _FLAC_MIN_LENGTH
            and buf[0] == _FLAC_SIGNATURE[0]
            and buf[1] == _FLAC_SIGNATURE[1]
            and buf[2] == _FLAC_SIGNATURE[2]
            and buf[3] == _FLAC_SIGNATURE[3]
        )


_WAV_MIN_LENGTH: Final = 11
_WAV_RIFF_SIGNATURE: Final = (0x52, 0x49, 0x46, 0x46)
_WAV_WAVE_SIGNATURE: Final = (0x57, 0x41, 0x56, 0x45)


class Wav(Type):
    """Implements the WAV audio type matcher."""

    MIME: Final[str] = "audio/x-wav"
    EXTENSION: Final[str] = "wav"

    def __init__(self) -> None:
        """Initialize the Wav matcher."""
        super().__init__(mime=Wav.MIME, extension=Wav.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the WAV file signature."""
        return (
            len(buf) > _WAV_MIN_LENGTH
            and buf[0] == _WAV_RIFF_SIGNATURE[0]
            and buf[1] == _WAV_RIFF_SIGNATURE[1]
            and buf[2] == _WAV_RIFF_SIGNATURE[2]
            and buf[3] == _WAV_RIFF_SIGNATURE[3]
            and buf[8] == _WAV_WAVE_SIGNATURE[0]
            and buf[9] == _WAV_WAVE_SIGNATURE[1]
            and buf[10] == _WAV_WAVE_SIGNATURE[2]
            and buf[11] == _WAV_WAVE_SIGNATURE[3]
        )


_AMR_MIN_LENGTH: Final = 11
_AMR_SIGNATURE: Final = (0x23, 0x21, 0x41, 0x4D, 0x52, 0x0A)


class Amr(Type):
    """Implements the AMR audio type matcher."""

    MIME: Final[str] = "audio/amr"
    EXTENSION: Final[str] = "amr"

    def __init__(self) -> None:
        """Initialize the Amr matcher."""
        super().__init__(mime=Amr.MIME, extension=Amr.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the AMR file signature."""
        return (
            len(buf) > _AMR_MIN_LENGTH
            and buf[0] == _AMR_SIGNATURE[0]
            and buf[1] == _AMR_SIGNATURE[1]
            and buf[2] == _AMR_SIGNATURE[2]
            and buf[3] == _AMR_SIGNATURE[3]
            and buf[4] == _AMR_SIGNATURE[4]
            and buf[5] == _AMR_SIGNATURE[5]
        )


class Aac(Type):
    """Implements the Aac audio type matcher."""

    MIME: Final[str] = "audio/aac"
    EXTENSION: Final[str] = "aac"

    def __init__(self) -> None:
        """Initialize the Aac matcher."""
        super().__init__(mime=Aac.MIME, extension=Aac.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the AAC file signature."""
        return buf[:2] == bytearray([0xFF, 0xF1]) or buf[:2] == bytearray([0xFF, 0xF9])


_AIFF_MIN_LENGTH: Final = 11
_AIFF_FORM_SIGNATURE: Final = (0x46, 0x4F, 0x52, 0x4D)
_AIFF_AIFF_SIGNATURE: Final = (0x41, 0x49, 0x46, 0x46)


class Aiff(Type):
    """Implements the AIFF audio type matcher."""

    MIME: Final[str] = "audio/x-aiff"
    EXTENSION: Final[str] = "aiff"

    def __init__(self) -> None:
        """Initialize the Aiff matcher."""
        super().__init__(mime=Aiff.MIME, extension=Aiff.EXTENSION)

    @override
    def match(self, buf: bytes | bytearray) -> bool:
        """Match the AIFF file signature."""
        return (
            len(buf) > _AIFF_MIN_LENGTH
            and buf[0] == _AIFF_FORM_SIGNATURE[0]
            and buf[1] == _AIFF_FORM_SIGNATURE[1]
            and buf[2] == _AIFF_FORM_SIGNATURE[2]
            and buf[3] == _AIFF_FORM_SIGNATURE[3]
            and buf[8] == _AIFF_AIFF_SIGNATURE[0]
            and buf[9] == _AIFF_AIFF_SIGNATURE[1]
            and buf[10] == _AIFF_AIFF_SIGNATURE[2]
            and buf[11] == _AIFF_AIFF_SIGNATURE[3]
        )
