"""Tests for upload size and content-signature validation."""

import pytest

from src.upload_security import MAX_UPLOAD_BYTES, validate_upload


def test_accepts_pdf_signature():
    validate_upload(b"%PDF-1.7\nbody", "report.pdf")


def test_accepts_xlsx_zip_signature():
    validate_upload(b"PK\x03\x04fake-but-signature-valid", "report.xlsx")


def test_rejects_extension_content_mismatch():
    with pytest.raises(ValueError, match="not a PDF"):
        validate_upload(b"not a pdf", "report.pdf")


def test_rejects_oversized_upload():
    with pytest.raises(ValueError, match="20 MB"):
        validate_upload(b"x" * (MAX_UPLOAD_BYTES + 1), "report.csv")


def test_rejects_binary_csv():
    with pytest.raises(ValueError, match="null bytes"):
        validate_upload(b"col1\x00col2", "report.csv")


def test_rejects_unknown_extension():
    with pytest.raises(ValueError, match="Unsupported"):
        validate_upload(b"data", "report.exe")
