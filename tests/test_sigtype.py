from pathlib import Path

import sigtype

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
