"""Check page with Third Party Financing for false positive chars."""

import pypdf, io
import pypdfium2 as pdfium
from mineru.utils.strikethrough_utils import (
    _parse_thin_horizontal_lines,
    _get_struck_phrases_from_page,
)
from mineru.utils.pdfium_guard import pdfium_guard

pdf_path = "demo/pdfs/22802bid03_appendixbtracked_0.pdf"
with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
with pdfium_guard():
    doc = pdfium.PdfDocument(io.BytesIO(pdf_bytes))

# Page 9 is where "Third Party Financing" appears (0-indexed = 8)
pg_idx = 8
page = reader.pages[pg_idx]
page_height = float(page.mediabox.height)
thin_lines = _parse_thin_horizontal_lines(page)
print(f"Page {pg_idx+1}: {len(thin_lines)} thin lines")

with pdfium_guard():
    pdfium_page = doc[pg_idx]

phrases = _get_struck_phrases_from_page(pdfium_page, thin_lines, page_height)
print(f"{len(phrases)} struck phrases:")
for p, y0, y1 in phrases:
    print(f"  y=[{y0:.0f},{y1:.0f}]  {repr(p)}")

with pdfium_guard():
    doc.close()
