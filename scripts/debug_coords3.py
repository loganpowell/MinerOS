"""
Correct coordinate-aware matching: drawn lines (PDF coords y=0 bottom)
vs pdftext spans (display coords y=0 top). Prove it works on page 4.
"""

from pathlib import Path
import pypdf
import pypdfium2 as pdfium
from mineru.utils.pdf_text_tool import get_page_chars
from mineru.utils.pdfium_guard import pdfium_guard
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


def parse_strikethrough_lines(content_bytes):
    """
    Parse content stream for thin horizontal lines.
    Returns list of (x0, y0_pdf, x1, y1_pdf) in PDF coords (y=0 at bottom).
    """
    tokens = content_bytes.decode("latin-1", errors="replace").split()
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
            h = abs(y1 - y0)
            w = abs(x1 - x0)
            if h < 3 and w > 5:
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


def tag_struck_spans(pdftext_lines, thin_lines_pdf, page_height):
    """
    Tag pdftext spans that are covered by drawn strikethrough lines.
    pdftext bbox = [x0, y0_disp, x1, y1_disp]  (y=0 at top of page)
    drawn lines  = (x0, y0_pdf, x1, y1_pdf)     (y=0 at bottom of page)
    Convert: y_disp = page_height - y_pdf
    """
    struck_spans = []
    for line in pdftext_lines:
        for span in line.get("spans", []):
            text = span.get("text", "").strip()
            if not text:
                continue
            bbox_obj = span.get("bbox")
            if bbox_obj is None:
                continue
            bb = bbox_obj.bbox if hasattr(bbox_obj, "bbox") else list(bbox_obj)
            sx0, sy0_disp, sx1, sy1_disp = bb  # display coords

            # Convert span display coords → PDF coords for comparison
            sy0_pdf = page_height - sy1_disp  # note: display y0 < y1, but pdf y0 > y1
            sy1_pdf = page_height - sy0_disp
            span_y_mid_pdf = (sy0_pdf + sy1_pdf) / 2
            span_h = sy1_pdf - sy0_pdf

            for lx0, ly0, lx1, ly1 in thin_lines_pdf:
                line_y_pdf = (ly0 + ly1) / 2

                # Vertical: line must pass through middle third of span's height
                if abs(line_y_pdf - span_y_mid_pdf) > span_h * 0.55:
                    continue

                # Horizontal: line must cover >25% of span width
                horiz_overlap = max(0, min(lx1, sx1) - max(lx0, sx0))
                span_w = sx1 - sx0
                if span_w > 0 and horiz_overlap / span_w > 0.25:
                    struck_spans.append(
                        {
                            "text": text,
                            "bbox": bb,
                            "line_y_pdf": line_y_pdf,
                        }
                    )
                    break

    return struck_spans


# ── Test on page 4 ───────────────────────────────────────────────────────────
PAGE_IDX = 3
page_pdf_obj = reader.pages[PAGE_IDX]
page_h = float(page_pdf_obj.mediabox.height)

thin_lines = parse_strikethrough_lines(get_page_content(page_pdf_obj))
print(
    f"Page {PAGE_IDX+1} ({page_h:.0f}pt tall): {len(thin_lines)} drawn horizontal lines"
)
print(
    f"  y range (PDF): {min(l[1] for l in thin_lines):.1f} – {max(l[3] for l in thin_lines):.1f}"
)
print(
    f"  = display y:   {page_h - max(l[3] for l in thin_lines):.1f} – {page_h - min(l[1] for l in thin_lines):.1f}"
)
print()

pdfium_page = doc[PAGE_IDX]
with pdfium_guard():
    chars_data = get_page_chars(pdfium_page)

pdftext_spans_raw = get_spans(chars_data["chars"])
pdftext_lines_list = get_lines(pdftext_spans_raw)

print(
    f"pdftext spans extracted: {sum(len(l.get('spans',[])) for l in pdftext_lines_list)}"
)
# Print spans in the y range where strikethrough lines exist
struck = tag_struck_spans(pdftext_lines_list, thin_lines, page_h)

print(f"\nSpans matched to drawn strikethrough lines: {len(struck)}")
for s in struck:
    print(f"  ~~{s['text']}~~")

doc.close()
