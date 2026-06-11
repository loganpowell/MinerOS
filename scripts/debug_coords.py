"""
Debug coordinate alignment between drawn lines and text spans on page 4.
"""

from pathlib import Path
import pypdf
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTChar, LTAnno, LTTextBox, LTTextLine

pdf_path = Path(__file__).parent.parent / "demo/pdfs/strikethrough.pdf"
reader = pypdf.PdfReader(str(pdf_path))


def get_page_content(page):
    content_obj = page.get_contents()
    if content_obj is None:
        return b""
    if isinstance(content_obj, (list, tuple)):
        return b"".join(c.get_data() for c in content_obj)
    return content_obj.get_data()


def parse_drawn_lines(content_bytes, page_height):
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
        elif tok == "l" and len(stack) >= 2 and last_move is not None:
            y, x = stack.pop(), stack.pop()
            x0, y0_pdf = last_move
            x1, y1_pdf = x, y
            lines.append(
                (
                    min(x0, x1),
                    min(y0_pdf, y1_pdf),
                    max(x0, x1),
                    max(y0_pdf, y1_pdf),
                )
            )
            stack.clear()
        elif tok == "re" and len(stack) >= 4:
            h = stack.pop()
            w = stack.pop()
            y = stack.pop()
            x = stack.pop()
            lines.append((x, y, x + w, y + h))
            stack.clear()
        else:
            stack.clear()
        i += 1
    return lines  # in PDF coords (y=0 at bottom)


PAGE_IDX = 3
page_pdf = reader.pages[PAGE_IDX]
page_h = float(page_pdf.mediabox.height)

raw = get_page_content(page_pdf)
all_lines = parse_drawn_lines(raw, page_h)
thin_lines = [
    (x0, y0, x1, y1)
    for x0, y0, x1, y1 in all_lines
    if abs(y1 - y0) < 3 and abs(x1 - x0) > 5
]

print(
    f"Page {PAGE_IDX+1}: {len(thin_lines)} thin horizontal lines (PDF coords, y=0 bottom)"
)
print("Sample (first 20):")
for x0, y0, x1, y1 in sorted(thin_lines, key=lambda l: -l[1])[:20]:
    print(f"  x0={x0:.1f}  y={y0:.2f}-{y1:.2f}  x1={x1:.1f}  width={x1-x0:.1f}")

print()

# Now list pdfminer text lines and their y coords (also PDF "y=0 bottom")
print("pdfminer text lines (PDF coords, y=0 bottom):")
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
            # pdfminer y coords are already PDF (bottom=0)
            print(
                f"  y0={line.y0:.1f}  y1={line.y1:.1f}  mid={((line.y0+line.y1)/2):.1f}  x0={line.x0:.1f}  x1={line.x1:.1f}  text={repr(text[:50])}"
            )
