import io
from pathlib import Path

import pytest

import sigtype
import sigtype.types.audio
import sigtype.types.base
import sigtype.utils

from .cfb_builder import build_cfb

# Absolute path to fixtures directory
FIXTURES = str(Path(__file__).resolve().parent / "fixtures")

# In compiled (mypyc) builds `Type` is a native class that interpreted code cannot subclass
COMPILED = not sigtype.types.base.__file__.endswith(".py")
SUBCLASSING_UNSUPPORTED = pytest.mark.skipif(COMPILED, reason="interpreted classes cannot inherit from compiled Type")


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


class TestTextDetection:
    def test_ascii_and_utf8(self):
        assert sigtype.is_text(b"plain text\nwith\twhitespace\r\n")
        assert sigtype.is_text("Привет, мир! 你好 🙂".encode())
        assert sigtype.is_text(b"\xef\xbb\xbfwith a BOM")

    def test_ansi_escape_sequences_are_text(self):
        assert sigtype.is_text(b"\x1b[31mred\x1b[0m\n")

    def test_utf16_and_utf32_with_bom(self):
        assert sigtype.is_text("hello".encode("utf-16"))
        assert sigtype.is_text("hello".encode("utf-32"))
        assert sigtype.is_text(b"\xfe\xff" + "привет".encode("utf-16-be"))

    def test_binary(self):
        assert sigtype.is_binary(b"\x00\x01\x02\x03")
        assert sigtype.is_binary(b"text with a NUL\x00 inside")
        assert sigtype.is_binary(b"\x01text starting with control")
        assert sigtype.is_binary(b"\xff\xd8\xff\xe0\x00\x10JFIF")
        assert sigtype.is_binary(b"caf\xe9 is not valid utf-8")

    def test_empty_is_text(self):
        assert sigtype.is_text(b"")
        assert not sigtype.is_binary(b"")

    def test_known_binary_files(self):
        for name in ("sample.jpg", "sample.zip", "sample.doc", "sample.mp4"):
            assert sigtype.is_binary(FIXTURES + "/" + name)

    def test_multibyte_character_cut_by_signature_window(self):
        data = ("a" * (sigtype.SIGNATURE_SIZE - 1) + "я" + "b" * 100).encode()
        assert sigtype.is_text(data)
        # the same cut is an error when it is the whole input
        assert sigtype.is_binary(("a" * 10 + "я").encode()[:-1])

    def test_path_and_stream(self, tmp_path):
        path = tmp_path / "note.txt"
        path.write_text("just a note\n")
        assert sigtype.is_text(str(path))
        assert sigtype.is_text(path)
        assert sigtype.is_text(io.BytesIO(b"just a note\n"))


class TestSourceReader:
    def test_path_reader_reads_repeatedly_and_can_be_closed(self, tmp_path):
        path = tmp_path / "data.bin"
        path.write_bytes(bytes(range(100)))
        reader = sigtype.utils.make_reader(str(path))
        assert reader is not None
        assert reader(10, 3) == bytes([10, 11, 12])
        assert reader(0, 2) == bytes([0, 1])
        assert reader(98, 10) == bytes([98, 99])
        assert reader(100, 10) == b""
        reader.close()
        reader.close()
        # a closed reader reopens the file on demand
        assert reader(5, 1) == bytes([5])
        reader.close()

    def test_readers_reject_negative_offsets_and_empty_reads(self, tmp_path):
        path = tmp_path / "data.bin"
        path.write_bytes(b"abcdef")
        for source in (str(path), b"abcdef", bytearray(b"abcdef"), memoryview(b"abcdef"), io.BytesIO(b"abcdef")):
            reader = sigtype.utils.make_reader(source)
            assert reader is not None
            assert reader(-1, 3) == b""
            assert reader(2, 0) == b""
            assert reader(2, 2) == b"cd"
            reader.close()

    def test_non_seekable_input_has_no_reader(self):
        assert sigtype.utils.make_reader(object()) is None  # type: ignore[arg-type]

    @pytest.mark.skipif(not Path("/proc/self/fd").exists(), reason="needs /proc to count open files")
    def test_guess_does_not_leak_file_descriptors(self, tmp_path):
        path = tmp_path / "late.xls"
        path.write_bytes(bytes(build_cfb(["Workbook"], padding_sectors=20)))

        def open_files() -> int:
            return len(list(Path("/proc/self/fd").iterdir()))

        before = open_files()
        for _ in range(20):
            assert sigtype.guess_extension(str(path)) == "xls"
        assert open_files() == before


class TestPathInput:
    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            sigtype.guess(str(tmp_path / "missing.bin"))

    def test_pathlib_path_and_str_agree(self):
        for name in ("sample.jpg", "sample.zip", "sample.doc", "sample.xlsx"):
            assert sigtype.guess_mime(Path(FIXTURES) / name) == sigtype.guess_mime(FIXTURES + "/" + name)

    @SUBCLASSING_UNSUPPORTED
    def test_file_is_closed_when_a_matcher_raises(self, tmp_path):
        class Boom(sigtype.types.Type):
            needs_read_at = True

            def __init__(self) -> None:
                super().__init__(mime="application/boom", extension="boom")

            def match_at(self, _buf, _read_at):
                raise RuntimeError

        path = tmp_path / "x.bin"
        path.write_bytes(b"data")
        with pytest.raises(RuntimeError):
            sigtype.match(str(path), [Boom()])
        # the file must not stay open: removing it would fail on Windows, and descriptors would leak everywhere
        if Path("/proc/self/fd").exists():
            assert not any(
                str(path) == str(link.resolve()) for link in Path("/proc/self/fd").iterdir() if link.exists()
            )


class TestReadAtFlag:
    @SUBCLASSING_UNSUPPORTED
    def test_class_level_flag_is_honoured_by_custom_matchers(self):
        seen = []

        class NeedsMore(sigtype.types.Type):
            needs_read_at = True

            def __init__(self) -> None:
                super().__init__(mime="application/needs-more", extension="nm")

            def match_at(self, _buf, read_at):
                seen.append(read_at is not None)
                return read_at is not None and read_at(0, 2) == b"NM"

        class Plain(sigtype.types.Type):
            def __init__(self) -> None:
                super().__init__(mime="application/plain", extension="pl")

            def match(self, buf):
                return buf[:2] == b"PL"

        assert NeedsMore().uses_read_at
        assert not Plain().uses_read_at
        assert sigtype.match(b"NM....", [Plain(), NeedsMore()]).extension == "nm"
        assert sigtype.match(b"PL....", [NeedsMore(), Plain()]).extension == "pl"
        assert seen == [True, True]
