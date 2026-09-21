# sigtype

Small, dependency-free, fast Python package to infer binary file types checking the magic numbers signature.

It works by looking at the first bytes of a file, buffer or stream, so it doesn't rely on file
extensions and can correctly identify files even when they are renamed or have no extension at all.
Images, video, audio, archives, documents and fonts are supported out of the box.

## Installation

```bash
pip install sigtype
```

## Usage

### Guess a file type

`guess()` accepts a path, `bytes`, `bytearray`, `memoryview` or a file-like object, and returns a
`Type` instance (with `.mime` and `.extension`) or `None` if the type could not be determined.

```python
import sigtype

kind = sigtype.guess("sample.jpg")

if kind is None:
    print("Cannot guess file type!")
else:
    print(f"File extension: {kind.extension}")
    print(f"File MIME type: {kind.mime}")
```

The same works with raw bytes:

```python
import sigtype

buf = bytearray([0xFF, 0xD8, 0xFF, 0x00, 0x08])
kind = sigtype.guess(buf)

print(kind.mime)  # image/jpeg
print(kind.extension)  # jpg
```

If you only need the MIME type or the extension, use the dedicated shortcuts:

```python
import sigtype

sigtype.guess_mime("sample.jpg")  # "image/jpeg"
sigtype.guess_extension("sample.jpg")  # "jpg"
```

### Check a specific file family

Helpers are available to check whether a file belongs to a given family without inspecting the
result manually:

```python
import sigtype

sigtype.is_image("sample.jpg")  # True
sigtype.is_archive("sample.zip")  # True
sigtype.is_video("sample.mp4")  # True
sigtype.is_audio("sample.mp3")  # True
sigtype.is_font("sample.ttf")  # True
sigtype.is_document("sample.docx")  # True
```

You can also check whether a MIME type or an extension is supported at all:

```python
import sigtype

sigtype.is_mime_supported("image/jpeg")  # True
sigtype.is_extension_supported("jpg")  # True
```

### Command line interface

`sigtype` also ships a small CLI to inspect files directly from the terminal:

```bash
python -m sigtype sample.jpg sample.zip
```

```
sample.jpg: image/jpeg (jpg)
sample.zip: application/zip (zip)
```

Wildcards are supported, since arguments are expanded with `glob`:

```bash
python -m sigtype ./fixtures/*
```

### Adding a custom type matcher

You can register your own matcher by subclassing `sigtype.types.Type` and registering an instance
with `add_type()`:

```python
import sigtype
from sigtype.types import Type


class Foo(Type):
    MIME = "application/foo"
    EXTENSION = "foo"

    def __init__(self) -> None:
        super().__init__(mime=Foo.MIME, extension=Foo.EXTENSION)

    def match(self, buf: bytes | bytearray) -> bool:
        return len(buf) > 2 and buf[0] == 0x46 and buf[1] == 0x4F and buf[2] == 0x4F


sigtype.add_type(Foo())

kind = sigtype.guess_mime("sample.foo")
print(kind)  # "application/foo"
```

## Supported types

- **Image**: jpg, jpx, jxl, apng, png, gif, webp, tiff, cr2, bmp, jxr, psd, ico, heic, dcm, avif, qoi, dds, dwg, xcf
- **Video**: mp4, m4v, mkv, webm, mov, avi, wmv, mpg, flv, m3gp
- **Audio**: aac, mid, mp3, m4a, ogg, flac, wav, amr, aiff
- **Archive**: br, rpm, dcm, epub, zip, tar, rar, gz, bz2, 7z, pdf, exe, swf, rtf, nes, crx, cab, eot, ps, xz, sqlite, deb, ar, z, lzop, lz, elf, lz4, zst
- **Font**: woff, woff2, ttf, otf
- **Document**: doc, docx, odt, xls, xlsx, ods, ppt, pptx, odp
- **Application**: wasm
