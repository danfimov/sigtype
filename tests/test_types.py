import io
import zipfile
from pathlib import Path

import sigtype

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
