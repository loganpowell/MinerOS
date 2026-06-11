"""
Calibrated matching: drawn lines (PDF coords, y=0 bottom) vs pdfminer lines.
Then verify against pdftext span coords too.
"""

from pathlib import Path
import pypdf
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTChar, LTAnno, LTTextBox, LTTextLine
import pypdfium2 as pdfium
from mineros.utils.pdf_text_tool import get_page_chars
from mineros.utils.pdfium_guard import pdfium_guard
from pdftext.pdf.pages import assign_scripts, get_blocks, get_lines, get_spans

pdf_path = Path(__file__).parent.parent / "demo/pdfs/strikethrough.pdf"
reader = pypdf.PdfReader(str(pdf_path))
doc = pdfium.PdfDocument(str(pdf_path))


def get_page_content(page):
    c = page.get_contents()
    if c is None:
        return b""
    if isinstance(c, (list, tuple)):
        return b"".join(x.get_data() for x in c)
    return c.get_data()


def parse_drawn_lines(content_bytes):
    """Return thin horizontal lines in PDF coords (y=0 at bottom)."""
    stream = content_bytes.decode("latin-1", errors="replace")
    tokens = stream.split()
    lines = []
    stack = []
    last_move = None
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        try:
            stack.append(float(tok))
            i += 1
            continue
        except ValueError:
            pass
        if tok == "m" and len(stack) >= 2:
            y, x = stack.pop(), stack.pop()
            last_move = (x, y)
            stack.clear()
        elif tok == "l" and len(stack) >= 2 and last_move:
            y, x = stack.pop(), stack.pop()
            x0, y0 = last_move
            x1, y1 = x, y
            if abs(y1 - y0) < 3 and abs(x1 - x0) > 5:
                lines.append((min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))
            stack.clear()
        elif tok == "re" and len(stack) >= 4:
            h, w, y, x = stack.pop(), stack.pop(), stack.pop(), stack.pop()
            if h < 3 and w > 5:
                lines.append((x, y, x + w, y + h))
            stack.clear()
        else:
            stack.clear()
        i += 1
    return lines


PAGE_IDX = 3
page_pdf = reader.pages[PAGE_IDX]
page_h = float(page_pdf.mediabox.height)

thin_lines = parse_drawn_lines(get_page_content(page_pdf))
print(f"Page {PAGE_IDX+1}: {len(thin_lines)} thin lines (PDF coords)")

# ── Check pdftext span coords ──────────────────────────────────────────────────
pdfium_page = doc[PAGE_IDX]
with pdfium_guard():
    chars_data = get_page_chars(pdfium_page)

pdftext_spans = get_spans(chars_data["chars"])
pdftext_lines = get_lines(pdftext_spans)

print("\nFirst 5 pdftext spans and their bbox format:")
for line in pdftext_lines[:3]:
    for sp in line.get("spans", [])[:2]:
        text = sp.get("text", "").strip()
        bbox = sp.get("bbox")
        if text and bbox:
            bb = bbox.bbox if hasattr(bbox, "bbox") else bbox
            print(f"  text={repr(text[:30]):35s}  bbox={[round(x,1) for x in bb]}")

print()

# ── Match lines to pdfminer text lines ──────────────────────────────────────
# pdfminer uses PDF coords (y=0 at bottom), same as drawn lines
matched_lines = []
all_text_lines = []
for page_layout in extract_pages(str(pdf_path), page_numbers=[PAGE_IDX]):
    for element in page_layout:
        if not isinstance(element, LTTextBox):
            continue
        for line in element:
            if not isinstance(line, LTTextLine):
                continue
            text = line.get_text().strip()
            if not text:
                continue
            all_text_lines.append(
                {
                    "text": text,
                    "x0": line.x0,
                    "y0": line.y0,
                    "x1": line.x1,
                    "y1": line.y1,
                }
            )


def spans_struck(tl, thin_lines, page_height):
    """Check if any drawn line passes through the vertical middle of this text line."""
    text_y_mid = (tl["y0"] + tl["y1"]) / 2
    text_height = tl["y1"] - tl["y0"]
    for lx0, ly0, lx1, ly1 in thin_lines:
        line_y = (ly0 + ly1) / 2  # typically zero-height so y0==y1
        # Line must be within ±40% of the text line's height band
        if abs(line_y - text_y_mid) > text_height * 0.5:
            continue
        # Line must horizontally overlap the text line by >20%
        horiz_overlap = max(0, min(lx1, tl["x1"]) - max(lx0, tl["x0"]))
        text_width = tl["x1"] - tl["x0"]
        if text_width > 0 and horiz_overlap / text_width > 0.2:
            return True
    return False


struck = [tl for tl in all_text_lines if spans_struck(tl, thin_lines, page_h)]
print(f"Text lines matched to drawn strikethrough lines: {len(struck)}")
for tl in struck[:30]:
    print(f"  ~~{tl['text'][:70]}~~")

doc.close()
