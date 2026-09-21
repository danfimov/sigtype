import io
import zipfile
from pathlib import Path

import sigtype
import sigtype.types

# Absolute path to fixtures directory
FIXTURES = str(Path(__file__).resolve().parent / "fixtures")


class TestFileType:
    def test_guess_jpeg(self):
        img_path = FIXTURES + "/sample.jpg"
        with Path(img_path).open("rb") as fp:
            for obj in (img_path, fp):
                kind = sigtype.guess(obj)
                assert kind is not None
                assert kind.mime == "image/jpeg"
                assert kind.extension == "jpg"
            # reset reader position test
            kind = sigtype.guess(fp)
            assert kind is not None
            assert kind.mime == "image/jpeg"
            assert kind.extension == "jpg"

    def test_guess_jpx(self):
        kind = sigtype.guess(FIXTURES + "/sample.jpx")
        assert kind is not None
        assert kind.mime == "image/jpx"
        assert kind.extension == "jpx"

    def test_guess_jxl(self):
        kind = sigtype.guess(FIXTURES + "/sample.jxl")
        assert kind is not None
        assert kind.mime == "image/jxl"
        assert kind.extension == "jxl"

    def test_guess_gif(self):
        kind = sigtype.guess(FIXTURES + "/sample.gif")
        assert kind is not None
        assert kind.mime == "image/gif"
        assert kind.extension == "gif"

    def test_guess_heic(self):
        kind = sigtype.guess(FIXTURES + "/sample.heic")
        assert kind is not None
        assert kind.mime == "image/heic"
        assert kind.extension == "heic"

    def test_guess_avif(self):
        kind = sigtype.guess(FIXTURES + "/sample.avif")
        assert kind is not None
        assert kind.mime == "image/avif"
        assert kind.extension == "avif"

    def test_guess_dds(self):
        kind = sigtype.guess(FIXTURES + "/sample.dds")
        assert kind is not None
        assert kind.mime == "image/dds"
        assert kind.extension == "dds"

    def test_guess_m4a(self):
        kind = sigtype.guess(FIXTURES + "/sample.m4a")
        assert kind is not None
        assert kind.mime == "audio/mp4"
        assert kind.extension == "m4a"

    @staticmethod
    def _build_id3v2_tag(body_length: int) -> bytes:
        size_bytes = bytes([(body_length >> (7 * i)) & 0x7F for i in (3, 2, 1, 0)])
        return b"ID3" + b"\x03\x00\x00" + size_bytes + b"\x00" * body_length

    def test_guess_flac(self):
        kind = sigtype.guess(b"fLaC" + b"\x00" * 20)
        assert kind is not None
        assert kind.mime == "audio/x-flac"
        assert kind.extension == "flac"

    def test_guess_mp3(self):
        kind = sigtype.guess(b"\xff\xfb\x90\x00" + b"\x00" * 20)
        assert kind is not None
        assert kind.mime == "audio/mpeg"
        assert kind.extension == "mp3"

    def test_guess_flac_with_leading_id3v2_tag(self):
        buf = self._build_id3v2_tag(20) + b"fLaC" + b"\x00" * 20
        kind = sigtype.guess(buf)
        assert kind is not None
        assert kind.mime == "audio/x-flac"
        assert kind.extension == "flac"

    def test_guess_mp3_with_id3v2_tag_still_detected_as_mp3(self):
        buf = self._build_id3v2_tag(20) + b"\xff\xfb\x90\x00" + b"\x00" * 20
        kind = sigtype.guess(buf)
        assert kind is not None
        assert kind.mime == "audio/mpeg"
        assert kind.extension == "mp3"

    def test_guess_mp4(self):
        kind = sigtype.guess(FIXTURES + "/sample.mp4")
        assert kind is not None
        assert kind.mime == "video/mp4"
        assert kind.extension == "mp4"

    def test_guess_png(self):
        kind = sigtype.guess(FIXTURES + "/sample.png")
        assert kind is not None
        assert kind.mime == "image/png"
        assert kind.extension == "png"

    def test_guess_tif(self):
        kind = sigtype.guess(FIXTURES + "/sample.tif")
        assert kind is not None
        assert kind.mime == "image/tiff"
        assert kind.extension == "tif"

    def test_guess_dicom_with_tiff_like_preamble(self):
        preamble = b"II*\x00" + b"\x00" * 124
        buf = preamble + b"DICM" + b"\x00" * 20
        kind = sigtype.guess(buf)
        assert kind is not None
        assert kind.mime == "application/dicom"
        assert kind.extension == "dcm"

    def test_guess_mov(self):
        kind = sigtype.guess(FIXTURES + "/sample.mov")
        assert kind is not None
        assert kind.mime == "video/quicktime"
        assert kind.extension == "mov"

    def test_guess_zstd(self):
        for name in "sample.zst", "sample_skippable.zst":
            kind = sigtype.guess(FIXTURES + "/" + name)
            assert kind is not None
            assert kind.mime == "application/zstd"
            assert kind.extension == "zst"

    def test_guess_doc(self):
        for name in "sample.doc", "sample_1.doc", "sample_2.doc":
            kind = sigtype.guess(FIXTURES + "/" + name)
            assert kind is not None
            assert kind.mime == "application/msword"
            assert kind.extension == "doc"

    def test_guess_docx(self):
        for name in "sample.docx", "sample_1.docx":
            kind = sigtype.guess(FIXTURES + "/" + name)
            assert kind is not None
            expected_mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            assert kind.mime == expected_mime
            assert kind.extension == "docx"

    def test_guess_docx_with_leading_trash_entries(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("[trash]/0000.dat", b"junk")
            zf.writestr("[trash]/0002.dat", b"junk")
            zf.writestr("[trash]/0001.dat", b"junk")
            zf.writestr("word/document.xml", "<w:document/>")
            zf.writestr("word/footnotes.xml", "<w:footnotes/>")

        kind = sigtype.guess(buf.getvalue())
        assert kind is not None
        expected_mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert kind.mime == expected_mime
        assert kind.extension == "docx"

    def test_guess_zip_is_not_misdetected_as_docx(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("readme.txt", "hello")
            zf.writestr("data.bin", b"junk")

        kind = sigtype.guess(buf.getvalue())
        assert kind is not None
        assert kind.mime == "application/zip"
        assert kind.extension == "zip"

    def test_guess_odt(self):
        kind = sigtype.guess(FIXTURES + "/sample.odt")
        assert kind is not None
        assert kind.mime == "application/vnd.oasis.opendocument.text"
        assert kind.extension == "odt"

    def test_guess_xls(self):
        kind = sigtype.guess(FIXTURES + "/sample.xls")
        assert kind is not None
        assert kind.mime == "application/vnd.ms-excel"
        assert kind.extension == "xls"

    def test_guess_xlsx(self):
        kind = sigtype.guess(FIXTURES + "/sample.xlsx")
        assert kind is not None
        assert kind.mime == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert kind.extension == "xlsx"

    def test_guess_ods(self):
        kind = sigtype.guess(FIXTURES + "/sample.ods")
        assert kind is not None
        assert kind.mime == "application/vnd.oasis.opendocument.spreadsheet"
        assert kind.extension == "ods"

    def test_guess_ppt(self):
        kind = sigtype.guess(FIXTURES + "/sample.ppt")
        assert kind is not None
        assert kind.mime == "application/vnd.ms-powerpoint"
        assert kind.extension == "ppt"

    def test_guess_ppt_not_misdetected_as_xls(self):
        ole_signature = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
        buf = bytearray(600)
        buf[0:8] = ole_signature
        buf[512:516] = b"\xfd\xff\xff\xff"
        buf[518] = 0x00  # satisfies Xls's weak secondary check
        buf[522:524] = b"\x00\x00"  # satisfies Ppt's secondary check
        kind = sigtype.guess(bytes(buf))
        assert kind is not None
        assert kind.mime == "application/vnd.ms-powerpoint"
        assert kind.extension == "ppt"

    def test_guess_pptx(self):
        kind = sigtype.guess(FIXTURES + "/sample.pptx")
        assert kind is not None
        expected_mime = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        assert kind.mime == expected_mime
        assert kind.extension == "pptx"

    def test_guess_odp(self):
        kind = sigtype.guess(FIXTURES + "/sample.odp")
        assert kind is not None
        assert kind.mime == "application/vnd.oasis.opendocument.presentation"
        assert kind.extension == "odp"


class TestFontMime:
    """Font MIME types follow RFC 8081, which deprecated the `application/font-*` aliases."""

    def test_woff(self):
        kind = sigtype.guess(b"wOFF\x00\x01\x00\x00" + b"\x00" * 16)
        assert kind is not None
        assert (kind.mime, kind.extension) == ("font/woff", "woff")

    def test_woff2(self):
        kind = sigtype.guess(b"wOF2\x00\x01\x00\x00" + b"\x00" * 16)
        assert kind is not None
        assert (kind.mime, kind.extension) == ("font/woff2", "woff2")

    def test_ttf(self):
        kind = sigtype.guess(b"\x00\x01\x00\x00\x00" + b"\x00" * 16)
        assert kind is not None
        assert (kind.mime, kind.extension) == ("font/ttf", "ttf")

    def test_otf(self):
        kind = sigtype.guess(b"OTTO\x00" + b"\x00" * 16)
        assert kind is not None
        assert (kind.mime, kind.extension) == ("font/otf", "otf")

    def test_mimes_are_unique(self):
        mimes = [kind.mime for kind in sigtype.types.FONT]
        assert len(mimes) == len(set(mimes))

    def test_is_font(self):
        assert sigtype.is_font(b"OTTO\x00" + b"\x00" * 16)


class TestPdfWithLeadingJunk:
    BODY = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj\n" + b"\x00" * 64

    def test_plain(self):
        assert sigtype.guess_mime(self.BODY) == "application/pdf"

    def test_file_name_before_header(self):
        assert sigtype.guess_mime(b"firmas_t/1082774737.png" + self.BODY) == "application/pdf"

    def test_html_before_header(self):
        buf = b'<html><head><meta http-equiv="refresh" content="0;url=http://dns"></head></html>\n' + self.BODY
        assert sigtype.guess_mime(buf) == "application/pdf"

    def test_leading_newline(self):
        assert sigtype.guess_mime(b"\n" + self.BODY) == "application/pdf"

    def test_header_beyond_search_range_is_ignored(self):
        assert sigtype.guess_mime(b"\x01" * 1024 + self.BODY) is None

    def test_mention_without_version_is_ignored(self):
        assert sigtype.guess_mime(b"\x01\x02 see %PDF- spec \x03" + b"\x00" * 32) is None
