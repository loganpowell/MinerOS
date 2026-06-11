import pypdf, io
import pypdfium2 as pdfium
from mineru.utils.strikethrough_utils import (
    _parse_thin_horizontal_lines,
    _get_struck_phrases_from_page,
)
from mineru.utils.pdfium_guard import pdfium_guard
from mineru.utils.pdf_text_tool import get_page_chars

pdf_path = "demo/pdfs/22802bid03_appendixbtracked_0.pdf"
with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
with pdfium_guard():
    doc = pdfium.PdfDocument(io.BytesIO(pdf_bytes))

for pg_idx in [1, 4]:
    page = reader.pages[pg_idx]
    mbox = page.mediabox
    page_height = float(mbox.height)
    thin_lines = _parse_thin_horizontal_lines(page)

    with pdfium_guard():
        pdfium_page = doc[pg_idx]

    print(f"\n=== Page {pg_idx+1} | height={page_height} ===")
    print(f"  Thin lines ({len(thin_lines)} total):")
    for l in sorted(thin_lines, key=lambda x: -x[1]):
        lx0, ly, lx1, _ = l
        print(
            f"    x0={lx0:.1f} y_pdf={ly:.1f} y_disp={page_height-ly:.1f} x1={lx1:.1f} w={lx1-lx0:.1f}"
        )

    # Check chars in the "t." area (page 5) or near top headers (page 2)
    page_data = get_page_chars(pdfium_page)
    chars = page_data.get("chars", [])
    print(f"  Total chars: {len(chars)}")

    # For page 5, look at chars around y_disp=525-535 (PDF y=257-267) — the "Licensed Software" area
    # For page 2, look at chars around y_disp=65-80 (PDF y=712-727) — the TOC header area
    if pg_idx == 4:
        y_disp_min, y_disp_max = 515, 545
        label = "Licensed Software area"
    else:
        y_disp_min, y_disp_max = 60, 85
        label = "TOC header area"

    print(f"\n  Chars in {label} (y_disp {y_disp_min}-{y_disp_max}):")
    area_chars = []
    for c in chars:
        bbox_obj = c.get("bbox")
        if bbox_obj is None:
            continue
        bb = bbox_obj.bbox if hasattr(bbox_obj, "bbox") else list(bbox_obj)
        x0, y0_disp, x1, y1_disp = bb
        y_center_disp = (y0_disp + y1_disp) / 2
        if y_disp_min <= y_center_disp <= y_disp_max:
            area_chars.append((x0, y_center_disp, c.get("char", ""), y0_disp, y1_disp))
    area_chars.sort(key=lambda c: (round(c[1] / 3), c[0]))
    txt = "".join(c[2] for c in area_chars)
    print(f"    Text: {repr(txt)}")
    for cx0, cy, ch, cy0, cy1 in area_chars[:5]:
        y_pdf_mid = page_height - (cy0 + cy1) / 2
        char_h = cy1 - cy0
        print(
            f"    char={repr(ch)} x={cx0:.1f} y_disp={cy:.1f} y_pdf_mid={y_pdf_mid:.1f} h={char_h:.1f}"
        )

    phrases = _get_struck_phrases_from_page(pdfium_page, thin_lines, page_height)
    print(f"\n  Struck phrases ({len(phrases)}):")
    for p in phrases[:30]:
        print(f"    {repr(p)}")

with pdfium_guard():
    doc.close()
