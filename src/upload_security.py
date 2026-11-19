"""Defensive validation for user-supplied financial documents.

This is an early rejection layer, not a malware scanner or parser sandbox. The
parser must still treat every document as untrusted input.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
import zipfile

MAX_UPLOAD_BYTES = 20 * 1024 * 1024
MAX_XLSX_ENTRIES = 1000
MAX_XLSX_UNCOMPRESSED_BYTES = 100 * 1024 * 1024
MAX_XLSX_COMPRESSION_RATIO = 200


def _validate_xlsx(data: bytes) -> None:
    """Validate XLSX container structure and reject obvious ZIP-bomb patterns."""
    try:
        with zipfile.ZipFile(BytesIO(data)) as archive:
            infos = archive.infolist()
            names = {info.filename for info in infos}
            if len(infos) > MAX_XLSX_ENTRIES:
                raise ValueError("XLSX contains too many ZIP entries.")
            if "[Content_Types].xml" not in names or "xl/workbook.xml" not in names:
                raise ValueError("XLSX package is missing required workbook components.")
            total_size = 0
            for info in infos:
                path = Path(info.filename)
                if path.is_absolute() or ".." in path.parts:
                    raise ValueError("XLSX contains an unsafe archive path.")
                total_size += info.file_size
                if info.file_size and info.compress_size == 0:
                    raise ValueError("XLSX contains an invalid compressed entry.")
                if info.compress_size and info.file_size / info.compress_size > MAX_XLSX_COMPRESSION_RATIO:
                    raise ValueError("XLSX compression ratio exceeds the safety limit.")
            if total_size > MAX_XLSX_UNCOMPRESSED_BYTES:
                raise ValueError("XLSX expands beyond the 100 MB safety limit.")
            bad_entry = archive.testzip()
            if bad_entry is not None:
                raise ValueError("XLSX archive failed its CRC integrity check.")
    except zipfile.BadZipFile as exc:
        raise ValueError("The file extension is XLSX, but its content is not a valid XLSX/ZIP package.") from exc


def validate_upload(data: bytes, filename: str) -> None:
    """Reject oversized uploads and obvious extension/content mismatches."""
    if not isinstance(data, bytes) or not data:
        raise ValueError("The uploaded file is empty or unreadable.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise ValueError("File exceeds the 20 MB upload limit.")

    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        if not data.startswith(b"%PDF-"):
            raise ValueError("The file extension is PDF, but its content is not a PDF.")
    elif suffix == ".xlsx":
        if not data.startswith(b"PK\x03\x04"):
            raise ValueError("The file extension is XLSX, but its content is not an XLSX/ZIP file.")
        _validate_xlsx(data)
    elif suffix == ".xls":
        if not data.startswith(bytes.fromhex("D0CF11E0A1B11AE1")):
            raise ValueError("The file extension is XLS, but its content is not an XLS file.")
    elif suffix == ".csv":
        try:
            decoded = data.decode("utf-8-sig")
        except UnicodeDecodeError:
            try:
                decoded = data.decode("utf-16")
            except UnicodeDecodeError as exc:
                raise ValueError("CSV must be valid UTF-8 or UTF-16 text.") from exc
        if "\x00" in decoded:
            raise ValueError("CSV contains binary/null bytes and was rejected.")
    else:
        raise ValueError(f"Unsupported file extension: {suffix or '(none)'}")
