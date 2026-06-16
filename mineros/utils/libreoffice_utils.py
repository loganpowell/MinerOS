import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import requests
from loguru import logger


def find_libreoffice() -> str | None:
    """Return the first usable LibreOffice/soffice binary path, or None."""
    candidates = [
        "libreoffice",
        "soffice",
        # macOS default install location
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        # common Linux locations
        "/usr/lib/libreoffice/program/soffice",
        "/usr/bin/libreoffice",
        # Windows
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.is_absolute():
            if path.exists():
                return str(path)
        elif shutil.which(candidate):
            return candidate
    return None


def _office_to_pdf_via_http(file_bytes: bytes, source_suffix: str, server_url: str) -> bytes:
    """Convert via a running unoserver HTTP endpoint."""
    resp = requests.post(
        server_url.rstrip("/") + "/",
        files={"file": (f"input.{source_suffix}", file_bytes)},
        data={"convert_to": "pdf"},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.content


def office_to_pdf_bytes(file_bytes: bytes, source_suffix: str) -> bytes:
    """Convert a PPTX or XLSX file to PDF bytes.

    Conversion strategy (first available wins):

    1. **Remote unoserver** — if ``MINEROS_LO_SERVER`` is set, POST to that URL.
       Run ``mineros-lo-server`` locally or deploy the ``libreoffice-server``
       Container App to use this path.
    2. **Local LibreOffice binary** — ``libreoffice`` / ``soffice`` on PATH or
       common install locations.

    Each slide (PPTX) or sheet (XLSX) becomes a page in the output PDF, which
    then flows into the normal VLM pipeline.

    Args:
        file_bytes: Raw bytes of the source file.
        source_suffix: File extension without dot, e.g. ``"pptx"`` or ``"xlsx"``.

    Returns:
        PDF bytes ready to feed into the VLM pipeline.

    Raises:
        RuntimeError: if neither a remote server nor a local binary is available,
            or if the conversion fails.
    """
    lo_server = os.getenv("MINEROS_LO_SERVER")
    if lo_server:
        logger.info(f"Converting .{source_suffix.upper()} via remote unoserver: {lo_server}")
        return _office_to_pdf_via_http(file_bytes, source_suffix, lo_server)

    lo = find_libreoffice()
    if lo is None:
        raise RuntimeError(
            f"LibreOffice is required to convert .{source_suffix} files to PDF. "
            "Either set MINEROS_LO_SERVER to a running unoserver URL, or install "
            "LibreOffice from https://www.libreoffice.org/download/ and ensure "
            "`libreoffice` or `soffice` is on your PATH."
        )

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / f"input.{source_suffix}"
        input_path.write_bytes(file_bytes)

        result = subprocess.run(
            [
                lo,
                "--headless",
                "--convert-to", "pdf",
                "--outdir", tmpdir,
                str(input_path),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"LibreOffice conversion failed (exit {result.returncode}): "
                f"{result.stderr.strip()}"
            )

        pdf_path = Path(tmpdir) / "input.pdf"
        if not pdf_path.exists():
            raise RuntimeError(
                f"LibreOffice ran but produced no PDF. stdout: {result.stdout.strip()}"
            )

        pdf_bytes = pdf_path.read_bytes()
        logger.info(
            f"Converted .{source_suffix.upper()} → PDF via LibreOffice "
            f"({len(pdf_bytes):,} bytes)"
        )
        return pdf_bytes
