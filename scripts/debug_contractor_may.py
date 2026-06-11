"""Debug the 'Contractor may t' false-positive on the Third Party Financing section."""

import pypdf, io
import pypdfium2 as pdfium
from mineros.utils.strikethrough_utils import _parse_thin_horizontal_lines
from mineros.utils.pdfium_guard import pdfium_guard
from mineros.utils.pdf_text_tool import get_page_chars

pdf_path = "demo/pdfs/22802bid03_appendixbtracked_0.pdf"
with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
with pdfium_guard():
    doc = pdfium.PdfDocument(io.BytesIO(pdf_bytes))

# Page 8 (0-indexed=7) contains section 17e Third Party Financing
pg_idx = 7
page = reader.pages[pg_idx]
page_height = float(page.mediabox.height)
thin_lines = _parse_thin_horizontal_lines(page)

with pdfium_guard():
    pdfium_page = doc[pg_idx]

page_data = get_page_chars(pdfium_page)
chars = page_data.get("chars", [])

_VERT_TOLERANCE_FACTOR = 0.40

# Find the thin lines in the "Contractor may" area
# "e. Third Party Financing" is near the top of this page
# Look for lines at y_disp ~ 50-150
print(f"Page {pg_idx+1}: {len(thin_lines)} thin lines, height={page_height}")
relevant_lines = [
    (lx0, ly, lx1) for lx0, ly, lx1, _ in thin_lines if (page_height - ly) < 200
]  # y_disp < 200
print(f"\nThin lines in top 200pt of page (display coords):")
for lx0, ly, lx1 in sorted(relevant_lines, key=lambda x: page_height - x[1]):
    print(f"  x0={lx0:.1f} y_disp={page_height-ly:.1f} x1={lx1:.1f} w={lx1-lx0:.1f}")

# Now find characters near y_disp ~80-130 (where "Contractor may" area is)
print(f"\nChars near 'Contractor may' region (y_disp 60-160):")
from mineros.utils.strikethrough_utils import _VERT_TOLERANCE_FACTOR as VTF

area_chars = []
for c in chars:
    bbox_obj = c.get("bbox")
    if not bbox_obj:
        continue
    bb = bbox_obj.bbox if hasattr(bbox_obj, "bbox") else list(bbox_obj)
    x0, y0_disp, x1, y1_disp = bb
    y_center = (y0_disp + y1_disp) / 2
    if 60 < y_center < 160:
        area_chars.append((x0, x1, y_center, c.get("char", "")))

area_chars.sort(key=lambda c: (round(c[2] / 2), c[0]))

# Show chars and which drawn lines they'd match
for x0, x1, yc, ch in area_chars:
    y0_pdf = page_height - (yc + 5)
    y1_pdf = page_height - (yc - 5)
    char_h = 10.0
    y_mid_pdf = page_height - yc
    x_mid = (x0 + x1) / 2

    matched_lines = []
    for lx0, ly, lx1 in relevant_lines:
        if abs(ly - y_mid_pdf) > char_h * VTF:
            continue
        # Current (lenient): center within lx0-2 .. lx1+2
        in_lenient = (lx0 - 2.0) <= x_mid <= (lx1 + 2.0)
        # Strict: center strictly within lx0 .. lx1
        in_strict = lx0 <= x_mid <= lx1
        if in_lenient:
            matched_lines.append(f"line[{lx0:.0f}-{lx1:.0f}] strict={in_strict}")

    if matched_lines or ch in ("t", "h", "e", "C", "o", "n", "r", "a", " ", "m", "y"):
        status = "STRUCK" if matched_lines else "clean"
        print(
            f"  {repr(ch):5s} x={x0:.1f}-{x1:.1f} xmid={x_mid:.1f} y={yc:.1f}  {status}  {matched_lines}"
        )

with pdfium_guard():
    doc.close()
