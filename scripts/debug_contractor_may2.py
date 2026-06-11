"""Find which page has 'Contractor may' struck and show char details."""

import pypdf, io
import pypdfium2 as pdfium
from mineros.utils.strikethrough_utils import (
    _parse_thin_horizontal_lines,
    _get_struck_phrases_from_page,
)
from mineros.utils.pdfium_guard import pdfium_guard
from mineros.utils.pdf_text_tool import get_page_chars

_VERT_TOLERANCE_FACTOR = 0.40

pdf_path = "demo/pdfs/22802bid03_appendixbtracked_0.pdf"
with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
with pdfium_guard():
    doc = pdfium.PdfDocument(io.BytesIO(pdf_bytes))

# Search pages 7-11 for where "Contractor may" appears struck
for pg_idx in range(6, 12):
    page = reader.pages[pg_idx]
    page_height = float(page.mediabox.height)
    thin_lines = _parse_thin_horizontal_lines(page)
    if not thin_lines:
        continue

    with pdfium_guard():
        pdfium_page = doc[pg_idx]

    page_data = get_page_chars(pdfium_page)
    chars = page_data.get("chars", [])

    # Find struck chars on this page that include 'C','o','n','t' pattern
    struck_chars = []
    for c in chars:
        bbox_obj = c.get("bbox")
        if not bbox_obj:
            continue
        bb = bbox_obj.bbox if hasattr(bbox_obj, "bbox") else list(bbox_obj)
        x0, y0_disp, x1, y1_disp = bb
        ch = c.get("char", "")
        if not ch:
            continue

        y0_pdf = page_height - y1_disp
        y1_pdf = page_height - y0_disp
        char_h = y1_pdf - y0_pdf
        if char_h <= 0:
            continue
        y_mid_pdf = (y0_pdf + y1_pdf) / 2
        x_mid = (x0 + x1) / 2

        for lx0, ly, lx1, _ in thin_lines:
            if abs(ly - y_mid_pdf) > char_h * _VERT_TOLERANCE_FACTOR:
                continue
            if (lx0 - 2.0) <= x_mid <= (lx1 + 2.0):
                # Is it a false positive (only caught by the +2 pad)?
                strict = lx0 <= x_mid <= lx1
                struck_chars.append((x0, x1, y0_disp, ch, lx0, lx1, strict, x_mid))
                break

    # Look for "Contractor may" pattern
    struck_chars.sort(key=lambda c: (round(c[2] / 3), c[0]))
    struck_text = "".join(c[3] for c in struck_chars if c[3].strip() or True)
    if "Contractor may" in struck_text or "ontra" in struck_text:
        print(f"\n=== Page {pg_idx+1}: found 'Contractor may' in struck text ===")
        # Find the region around it
        idx = struck_text.find("Contractor")
        if idx < 0:
            idx = struck_text.find("ontra")
        context_chars = struck_chars[max(0, idx - 2) : idx + 20]
        for x0, x1, y, ch, lx0, lx1, strict, xmid in context_chars:
            flag = "" if strict else " ← ONLY CAUGHT BY +2pt PAD"
            print(
                f"  {repr(ch):4s}  x={x0:.1f}-{x1:.1f} xmid={xmid:.1f}  line=[{lx0:.1f},{lx1:.1f}]  strict={strict}{flag}"
            )

with pdfium_guard():
    doc.close()
