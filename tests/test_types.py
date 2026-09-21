import io
import zipfile
from pathlib import Path

import sigtype
import sigtype.types
import sigtype.types.document
from sigtype.types.cfb import read_root_entry_names

from .cfb_builder import build_cfb

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


class TestOleDocuments:
    """OLE2 formats are told apart by the streams in the container directory, not by byte offsets."""

    PPT_STREAMS = ("PowerPoint Document", "Current User", "\x05SummaryInformation", "\x05DocumentSummaryInformation")

    @staticmethod
    def _ext(data) -> str | None:
        return sigtype.guess_extension(bytes(data))

    def test_doc_xls_ppt_msg(self):
        assert self._ext(build_cfb(["WordDocument", "1Table"])) == "doc"
        assert self._ext(build_cfb(["Workbook"])) == "xls"
        assert self._ext(build_cfb(["PowerPoint Document"])) == "ppt"
        assert self._ext(build_cfb(["__properties_version1.0", ("__substg1.0_0037001F", [])])) == "msg"

    def test_msg_mime(self):
        kind = sigtype.guess(bytes(build_cfb(["__properties_version1.0"])))
        assert kind is not None
        assert kind.mime == "application/vnd.ms-outlook"

    def test_excel_5_book_stream(self):
        assert self._ext(build_cfb(["Book"])) == "xls"

    def test_ppt_sharing_signature_with_xls_is_not_taken_for_xls(self):
        # The FAT of this container starts with FD FF FF FF at offset 512, and the legacy Xls heuristic accepts
        # it while the legacy Ppt one rejects it.
        data = bytes(build_cfb(list(self.PPT_STREAMS)))
        assert data[512:520] == b"\xfd\xff\xff\xff\x02\x00\x00\x00"
        assert sigtype.types.document.Xls().match_signature(data)
        assert not sigtype.types.document.Ppt().match_signature(data)
        assert self._ext(data) == "ppt"

    def test_unknown_ole_container_is_not_office(self):
        data = build_cfb(["VisioDocument"])
        assert self._ext(data) is None

    def test_embedded_object_does_not_change_the_type(self):
        data = bytes(build_cfb(["WordDocument", ("ObjectPool", ["Workbook"])]))
        assert self._ext(data) == "doc"
        assert not sigtype.types.document.Xls().match(data)

    def test_4096_byte_sectors(self):
        assert self._ext(build_cfb(["WordDocument"], sector_shift=12)) == "doc"

    def test_directory_past_signature_window(self, tmp_path):
        data = bytes(build_cfb(["Workbook"], padding_sectors=20))
        assert len(data) > sigtype.SIGNATURE_SIZE * 1.3

        assert self._ext(data) == "xls"

        path = tmp_path / "late.xls"
        path.write_bytes(data)
        assert sigtype.guess_extension(str(path)) == "xls"
        assert sigtype.guess_extension(io.BytesIO(data)) == "xls"

        head = data[: sigtype.SIGNATURE_SIZE]
        assert sigtype.guess_extension(head, read_at=lambda offset, size: data[offset : offset + size]) == "xls"

    def test_directory_past_signature_window_without_reader(self):
        data = bytes(build_cfb(["Workbook"], padding_sectors=20))
        assert read_root_entry_names(data[: sigtype.SIGNATURE_SIZE], None) is None
        # nothing to go on for the directory, so the byte-offset heuristics decide and must not raise
        assert sigtype.types.document.Doc().match(data[: sigtype.SIGNATURE_SIZE]) is False

    def test_cyclic_directory_chain_terminates(self):
        data = build_cfb(list(self.PPT_STREAMS))
        data[512 + 4 * 2 : 512 + 4 * 3] = (2).to_bytes(4, "little")  # second directory sector points to itself
        assert read_root_entry_names(bytes(data), None) is None

    def test_truncated_container(self):
        data = bytes(build_cfb(["WordDocument"]))
        assert read_root_entry_names(data[:600], None) is None
        assert read_root_entry_names(data[:100], None) is None

    def test_real_fixtures(self):
        for name, ext in (("sample.doc", "doc"), ("sample.xls", "xls"), ("sample.ppt", "ppt")):
            assert sigtype.guess_extension(FIXTURES + "/" + name) == ext
            data = Path(FIXTURES + "/" + name).read_bytes()
            assert read_root_entry_names(data, None) is not None


class TestTextBasedTypes:
    SVG = b'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><rect width="10" height="10"/></svg>'

    def test_svg(self):
        kind = sigtype.guess(self.SVG)
        assert kind is not None
        assert (kind.mime, kind.extension) == ("image/svg+xml", "svg")
        assert sigtype.is_image(self.SVG)

    def test_svg_with_prolog(self):
        buf = (
            b'\xef\xbb\xbf\n<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
            b"<!-- Created with an editor -->\n"
            b'<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'
            b'<svg xmlns="http://www.w3.org/2000/svg"></svg>'
        )
        assert sigtype.guess_extension(buf) == "svg"

    def test_svg_with_internal_subset(self):
        buf = b'<?xml version="1.0"?><!DOCTYPE svg [ <!ENTITY ns "http://www.w3.org/2000/svg"> ]>\n<svg xmlns="&ns;"/>'
        assert sigtype.guess_extension(buf) == "svg"

    def test_other_xml_is_not_svg(self):
        assert sigtype.guess_extension(b'<?xml version="1.0"?><html><svg></svg></html>') is None
        assert sigtype.guess_extension(b"<svgfoo></svgfoo>") is None
        assert sigtype.guess_extension(b"just <svg> mentioned in text") is None

    def test_svg_path(self, tmp_path):
        path = tmp_path / "logo.svg"
        path.write_bytes(self.SVG)
        assert sigtype.guess_mime(str(path)) == "image/svg+xml"

    def test_fb2(self):
        buf = (
            b'<?xml version="1.0" encoding="utf-8"?>\n<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0">'
        )
        kind = sigtype.guess(buf)
        assert kind is not None
        assert (kind.mime, kind.extension) == ("application/x-fictionbook+xml", "fb2")

    def test_eml(self):
        buf = (
            b"Received: from mail.example.com (mail.example.com [192.0.2.1])\r\n"
            b"\tby mx.example.org with ESMTP id abc123\r\n"
            b"From: Alice <alice@example.com>\r\n"
            b"To: Bob <bob@example.org>\r\n"
            b"Subject: Hello\r\n"
            b"Date: Mon, 21 Sep 2026 10:00:00 +0000\r\n"
            b"\r\n"
            b"Body with \xff\xfe bytes\r\n"
        )
        kind = sigtype.guess(buf)
        assert kind is not None
        assert (kind.mime, kind.extension) == ("message/rfc822", "eml")

    def test_eml_cut_mid_line_by_signature_window(self):
        buf = b"From: a@example.com\nTo: b@example.org\nSubject: a long subje"
        assert sigtype.guess_extension(buf) == "eml"

    def test_headers_alone_are_not_enough_for_eml(self):
        assert sigtype.guess_extension(b"Content-Type: text/plain\nContent-Length: 5\n\nhello") is None
        assert sigtype.guess_extension(b"Subject: only one known header\nX-Custom: 1\n\nhello") is None

    def test_prose_is_not_eml(self):
        assert sigtype.guess_extension(b"From: the beginning\nthis is just prose\nTo: nobody\n") is None

    def test_binary_is_not_eml(self):
        assert sigtype.guess_extension(b"From:\x00\x01\x02To:\x00\x00Subject:\x00") is None


class TestPlainText:
    @staticmethod
    def _guess(data: bytes):
        return sigtype.match(data, [*sigtype.types.TYPES, *sigtype.types.PLAIN_TEXT])

    def test_plain_text(self):
        kind = self._guess(b"Just some notes.\nAnother line.\n")
        assert kind is not None
        assert (kind.mime, kind.extension) == ("text/plain", "txt")

    def test_markdown(self):
        for data in (
            b"# Title\n\nSee [the docs](https://example.com/docs) for more.\n",
            b"Intro\n\n```python\nprint('hi')\n```\n",
            b"Some **important** words.\n",
            b"![logo](./logo.png)\n",
        ):
            kind = self._guess(data)
            assert kind is not None
            assert (kind.mime, kind.extension) == ("text/markdown", "md"), data

    def test_code_and_config_are_not_markdown(self):
        for data in (
            b"# comment\n- item\n- other\nkey: value\n",
            b"#!/bin/sh\n# comment\necho done\n",
            b"# Title-looking comment\nx = a**2 + b**3\n",
            b"handlers[name](arg)\n",
            b"__init__ and __all__\n",
        ):
            kind = self._guess(data)
            assert kind is not None
            assert kind.extension == "txt", data

    def test_binary_is_not_text(self):
        assert self._guess(b"\x00\x01\x02") is None
        assert self._guess(b"") is None

    def test_default_guess_does_not_return_text(self):
        assert sigtype.guess(b"Just some notes.\nAnother line.\n") is None
        assert sigtype.guess(b"# Title\n\n```\ncode\n```\n") is None

    def test_binary_types_win_over_text(self):
        kind = self._guess(b'<svg xmlns="http://www.w3.org/2000/svg"/>')
        assert kind is not None
        assert kind.extension == "svg"


class TestOfd:
    @staticmethod
    def _zip(*names: str, compress: bool = False) -> bytes:
        buf = io.BytesIO()
        method = zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED
        with zipfile.ZipFile(buf, "w", method) as zf:
            for name in names:
                zf.writestr(name, "<xml>" + name * 20 + "</xml>")
        return buf.getvalue()

    def test_ofd(self):
        kind = sigtype.guess(self._zip("OFD.xml", "Doc_0/Document.xml", "Doc_0/Pages/Page_0/Content.xml"))
        assert kind is not None
        assert (kind.mime, kind.extension) == ("application/ofd", "ofd")

    def test_ofd_root_entry_not_first(self):
        data = self._zip("Doc_0/Document.xml", "Doc_0/Res/PublicRes.xml", "OFD.xml", compress=True)
        assert sigtype.guess_extension(data) == "ofd"

    def test_plain_zip_is_not_ofd(self):
        assert sigtype.guess_extension(self._zip("a.txt", "b.txt")) == "zip"

    def test_nested_ofd_xml_is_not_the_root_entry(self):
        assert sigtype.guess_extension(self._zip("docs/OFD.xml", "docs/x.xml")) == "zip"
        assert sigtype.guess_extension(self._zip("NOTOFD.xml", "x.xml")) == "zip"


class TestEbooks:
    def test_mobi(self):
        data = b"Some Book Title".ljust(60, b"\x00") + b"BOOKMOBI" + b"\x00" * 100
        kind = sigtype.guess(data)
        assert kind is not None
        assert (kind.mime, kind.extension) == ("application/x-mobipocket-ebook", "mobi")
        assert sigtype.is_document(data)

    def test_mobi_needs_the_marker_at_its_offset(self):
        assert sigtype.guess_extension(b"BOOKMOBI" + b"\x00" * 100) is None
        assert sigtype.guess_extension(b"x" * 61 + b"BOOKMOBI" + b"\x00" * 100) is None

    def test_djvu(self):
        for form in (b"DJVU", b"DJVM"):
            data = b"AT&TFORM\x00\x00\x12\x34" + form + b"\x00" * 100
            kind = sigtype.guess(data)
            assert kind is not None
            assert (kind.mime, kind.extension) == ("image/vnd.djvu", "djvu")

    def test_iff_form_that_is_not_djvu(self):
        assert sigtype.guess_extension(b"AT&TFORM\x00\x00\x12\x34DJVX" + b"\x00" * 100) is None


class TestOpus:
    @staticmethod
    def _ogg_page(first_packet: bytes, segments: int = 1) -> bytes:
        header = b"OggS\x00\x02" + b"\x00" * 20 + bytes([segments])
        table = bytes([len(first_packet)]) + b"\x00" * (segments - 1)
        return header + table + first_packet

    def test_opus(self):
        data = self._ogg_page(b"OpusHead\x01\x02\x38\x01\x80\xbb\x00\x00\x00\x00\x00")
        kind = sigtype.guess(data)
        assert kind is not None
        assert (kind.mime, kind.extension) == ("audio/opus", "opus")
        assert sigtype.is_audio(data)

    def test_opus_with_several_segments(self):
        assert sigtype.guess_extension(self._ogg_page(b"OpusHead\x01\x02", segments=3)) == "opus"

    def test_vorbis_stays_ogg(self):
        kind = sigtype.guess(self._ogg_page(b"\x01vorbis\x00\x00\x00\x00\x02"))
        assert kind is not None
        assert (kind.mime, kind.extension) == ("audio/ogg", "ogg")

    def test_truncated_ogg_page(self):
        assert sigtype.guess_extension(b"OggS\x00\x02" + b"\x00" * 20) == "ogg"
        assert sigtype.guess_extension(b"OggS\x00\x02" + b"\x00" * 20 + b"\xff") == "ogg"
