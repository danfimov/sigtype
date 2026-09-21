import io
from pathlib import Path

import sigtype
import sigtype.types.audio
import sigtype.utils

# Absolute path to fixtures directory
FIXTURES = str(Path(__file__).resolve().parent / "fixtures")


class TestFileType:
    def test_guess_file_path(self):
        kind = sigtype.guess(FIXTURES + "/sample.jpg")
        assert kind is not None
        assert kind.mime == "image/jpeg"
        assert kind.extension == "jpg"

    def test_guess_buffer(self):
        buf = bytearray([0xFF, 0xD8, 0xFF, 0x00, 0x08])
        kind = sigtype.guess(buf)
        assert kind is not None
        assert kind.mime == "image/jpeg"
        assert kind.extension == "jpg"

    def test_guess_buffer_invalid(self):
        buf = bytearray([0xFF, 0x00, 0x00, 0x00, 0x00])
        kind = sigtype.guess(buf)
        assert kind is None

    def test_guess_memoryview(self):
        buf = memoryview(bytearray([0xFF, 0xD8, 0xFF, 0x00, 0x08]))
        kind = sigtype.guess(buf)
        assert kind is not None
        assert kind.mime == "image/jpeg"
        assert kind.extension == "jpg"


class TestFileTypeExtension:
    def test_guess_extension_file_path(self):
        ext = sigtype.guess_extension(FIXTURES + "/sample.jpg")
        assert ext is not None
        assert ext == "jpg"

    def test_guess_extension_buffer(self):
        buf = bytearray([0xFF, 0xD8, 0xFF, 0x00, 0x08])
        ext = sigtype.guess_extension(buf)
        assert ext is not None
        assert ext == "jpg"

    def test_guess_extension_buffer_invalid(self):
        buf = bytearray([0xFF, 0x00, 0x00, 0x00, 0x00])
        ext = sigtype.guess_extension(buf)
        assert ext is None

    def test_guess_extension_memoryview(self):
        buf = memoryview(bytearray([0xFF, 0xD8, 0xFF, 0x00, 0x08]))
        ext = sigtype.guess_extension(buf)
        assert ext is not None
        assert ext == "jpg"


class TestFileTypeMIME:
    def test_guess_mime_file_path(self):
        mime = sigtype.guess_mime(FIXTURES + "/sample.jpg")
        assert mime is not None
        assert mime == "image/jpeg"

    def test_guess_mime_buffer(self):
        buf = bytearray([0xFF, 0xD8, 0xFF, 0x00, 0x08])
        mime = sigtype.guess_mime(buf)
        assert mime is not None
        assert mime == "image/jpeg"

    def test_guess_mime_buffer_invalid(self):
        buf = bytearray([0xFF, 0x00, 0x00, 0x00, 0x00])
        mime = sigtype.guess_mime(buf)
        assert mime is None

    def test_guess_mime_memoryview(self):
        buf = memoryview(bytearray([0xFF, 0xD8, 0xFF, 0x00, 0x08]))
        mime = sigtype.guess_mime(buf)
        assert mime is not None
        assert mime == "image/jpeg"

    def test_guess_video_invalid(self):
        buf = bytearray(
            [
                0x0,
                0x0,
                0x0,
                0x0,
                0x66,
                0x74,
                0x79,
                0x70,
                0xF2,
                0xF2,
                0xF2,
                0xF2,
                0xF6,
                0xF2,
                0xF2,
                0x90,
            ]
        )
        mime = sigtype.guess_mime(buf)
        assert mime is None

    def test_guess_image_invalid(self):
        buf = bytearray([0x49, 0x49, 0x2A, 0x0])
        mime = sigtype.guess_mime(buf)
        assert mime is None


class TestTypeComparison:
    def test_is_extension_compares_by_value(self):
        kind = sigtype.guess(FIXTURES + "/sample.jpg")
        assert kind is not None
        # runtime-built strings are not interned, so identity comparison would fail
        assert kind.is_extension("xjpg"[1:])
        assert not kind.is_extension("png")

    def test_is_mime_compares_by_value(self):
        kind = sigtype.guess(FIXTURES + "/sample.jpg")
        assert kind is not None
        assert kind.is_mime("ximage/jpeg"[1:])
        assert not kind.is_mime("image/png")


class TestSignatureSize:
    def test_constant_is_exposed(self):
        assert sigtype.SIGNATURE_SIZE == 8192

    def test_only_signature_size_bytes_are_read(self, tmp_path):
        path = tmp_path / "big.bin"
        path.write_bytes(b"\x00" * (sigtype.SIGNATURE_SIZE * 2))
        assert len(sigtype.utils.get_bytes(str(path))) == sigtype.SIGNATURE_SIZE
        assert len(sigtype.utils.get_bytes(path.read_bytes())) == sigtype.SIGNATURE_SIZE


def _flac_with_big_id3(tag_size: int = 20000) -> bytes:
    """FLAC file whose ID3v2 tag is larger than the signature window."""
    syncsafe = bytes([(tag_size >> 21) & 0x7F, (tag_size >> 14) & 0x7F, (tag_size >> 7) & 0x7F, tag_size & 0x7F])
    return b"ID3\x04\x00\x00" + syncsafe + b"\x00" * tag_size + b"fLaC" + b"\x00" * 64


class TestReadAt:
    def test_bytes_input_reads_past_signature(self):
        assert sigtype.guess_mime(_flac_with_big_id3()) == "audio/x-flac"

    def test_bytearray_and_memoryview_input(self):
        data = _flac_with_big_id3()
        assert sigtype.guess_mime(bytearray(data)) == "audio/x-flac"
        assert sigtype.guess_mime(memoryview(data)) == "audio/x-flac"

    def test_path_input(self, tmp_path):
        path = tmp_path / "tagged.flac"
        path.write_bytes(_flac_with_big_id3())
        assert sigtype.guess_mime(str(path)) == "audio/x-flac"
        assert sigtype.guess_mime(path) == "audio/x-flac"

    def test_seekable_stream_keeps_position(self):
        stream = io.BytesIO(_flac_with_big_id3())
        stream.seek(5)
        assert sigtype.guess_mime(stream) == "audio/x-flac"
        assert stream.tell() == 5

    def test_non_seekable_stream_falls_back(self):
        class Unseekable:
            def __init__(self, data: bytes) -> None:
                self._stream = io.BytesIO(data)

            def read(self, size: int = -1) -> bytes:
                return self._stream.read(size)

        # the FLAC marker is out of reach, so the leading ID3v2 tag makes it look like an MP3
        assert sigtype.guess_mime(Unseekable(_flac_with_big_id3())) == "audio/mpeg"

    def test_custom_read_at(self):
        data = _flac_with_big_id3()
        calls = []

        def read_at(offset: int, size: int) -> bytes:
            calls.append((offset, size))
            return data[offset : offset + size]

        # e.g. only the head was downloaded, the rest is fetched on demand via a ranged request
        head = data[: sigtype.SIGNATURE_SIZE]
        assert sigtype.guess_mime(head, read_at=read_at) == "audio/x-flac"
        assert calls == [(20010, 4)]

    def test_read_at_is_not_called_when_not_needed(self):
        def read_at(_offset: int, _size: int) -> bytes:
            raise AssertionError

        assert sigtype.guess_mime(bytearray([0xFF, 0xD8, 0xFF, 0x00, 0x08]), read_at=read_at) == "image/jpeg"

    def test_flac_with_small_id3_still_matches_without_reader(self):
        data = b"ID3\x04\x00\x00\x00\x00\x00\x10" + b"\x00" * 16 + b"fLaC" + b"\x00" * 64
        assert sigtype.types.audio.Flac().match(data)

    def test_truncated_flac_is_not_matched(self):
        data = _flac_with_big_id3()[:15000]
        assert sigtype.guess_mime(data) == "audio/mpeg"
