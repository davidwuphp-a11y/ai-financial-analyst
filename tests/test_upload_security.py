"""Tests for upload size, content-signature and XLSX package validation."""

from io import BytesIO
import zipfile

import pytest

from src.upload_security import MAX_UPLOAD_BYTES, validate_upload


def _xlsx_bytes():
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", "<Types/>")
        archive.writestr("xl/workbook.xml", "<workbook/>")
    return buffer.getvalue()


def test_accepts_pdf_signature():
    validate_upload(b"%PDF-1.7\nbody", "report.pdf")


def test_accepts_valid_xlsx_package():
    validate_upload(_xlsx_bytes(), "report.xlsx")


def test_rejects_malformed_xlsx_package():
    with pytest.raises(ValueError, match="valid XLSX"):
        validate_upload(b"PK\x03\x04not-a-zip", "report.xlsx")


def test_rejects_xlsx_missing_workbook_parts():
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("random.txt", "not a workbook")
    with pytest.raises(ValueError, match="missing required"):
        validate_upload(buffer.getvalue(), "report.xlsx")


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
