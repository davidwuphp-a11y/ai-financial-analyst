"""Defensive validation for user-supplied financial documents.

This is an early rejection layer, not a complete malware scanner or parser sandbox.
The parser must still treat every document as untrusted input.
"""

from __future__ import annotations

from pathlib import Path

MAX_UPLOAD_BYTES = 20 * 1024 * 1024


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
        if not data.startswith(b"PK\\x03\\x04"):
            raise ValueError("The file extension is XLSX, but its content is not an XLSX/ZIP file.")
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
        if "\\x00" in decoded:
            raise ValueError("CSV contains binary/null bytes and was rejected.")
    else:
        raise ValueError(f"Unsupported file extension: {suffix or '(none)'}")
