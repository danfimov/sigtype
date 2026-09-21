from pathlib import Path

import pytest

import file_type

# Absolute path to fixtures directory
FIXTURES = str(Path(__file__).resolve().parent / "fixtures")


@pytest.mark.benchmark
def test_infer_image_from_disk():
    file_type.guess(FIXTURES + "/sample.jpg")


@pytest.mark.benchmark
def test_infer_video_from_disk():
    file_type.guess(FIXTURES + "/sample.mp4")


@pytest.mark.benchmark
def test_infer_zip_from_disk():
    file_type.guess(FIXTURES + "/sample.zip")


@pytest.mark.benchmark
def test_infer_tar_from_disk():
    file_type.guess(FIXTURES + "/sample.tar")


@pytest.mark.benchmark
def test_infer_image_from_bytes():
    file_type.guess(bytearray([0xFF, 0xD8, 0xFF, 0x00, 0x08]))


@pytest.mark.benchmark
def test_infer_video_from_bytes():
    file_type.guess(bytearray([0x1A, 0x45, 0xDF, 0xA3, 0x08]))


@pytest.mark.benchmark
def test_infer_audio_from_bytes():
    file_type.guess(bytearray([0x4D, 0x54, 0x68, 0xA3, 0x64]))
