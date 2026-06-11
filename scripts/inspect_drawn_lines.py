"""
Parse page content stream to extract drawn line coordinates, then cross-reference
with text spans to identify which spans are struck through.
"""

from pathlib import Path
import re
import pypdf
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTChar, LTAnno, LTTextBox, LTTextLine

pdf_path = Path(__file__).parent.parent / "demo/pdfs/strikethrough.pdf"
reader = pypdf.PdfReader(str(pdf_path))


def get_page_content(page):
    """Return decoded content stream bytes for a page."""
    content_obj = page.get_contents()
    if content_obj is None:
        return b""
    if isinstance(content_obj, (list, tuple)):
        return b"".join(c.get_data() for c in content_obj)
    return content_obj.get_data()


def parse_drawn_lines(content_bytes, page_height):
    """
    Parse PDF content stream for moveto/lineto/stroke sequences.
    Returns list of (x0, y0, x1, y1) in display coords (y=0 at top).
    """
    lines = []
    # Tokenize the stream
    stream = content_bytes.decode("latin-1", errors="replace")
    tokens = stream.split()

    stack = []
    i = 0
    current_path_start = None  # (x, y) of last 'm'
    last_move = None

    while i < len(tokens):
        tok = tokens[i]

        # Push numbers onto stack
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
            # Record as a path segment
            # We'll finalize when we hit S/s/f/etc.
            # Store for now
            current_path_start = last_move
            current_path_end = (x, y)
            # Convert from PDF coords (y=0 bottom) to display (y=0 top)
            x0, y0 = current_path_start
            x1, y1 = current_path_end
            lines.append(
                (
                    min(x0, x1),
                    page_height - max(y0, y1),
                    max(x0, x1),
                    page_height - min(y0, y1),
                )
            )
            stack.clear()

        elif tok in ("S", "s", "F", "f", "B", "b", "f*", "B*", "b*"):
            stack.clear()

        elif tok == "re" and len(stack) >= 4:
            # Rectangle: x y w h re
            h = stack.pop()
            w = stack.pop()
            y = stack.pop()
            x = stack.pop()
            lines.append((x, page_height - (y + h), x + w, page_height - y))
            stack.clear()

        else:
            stack.clear()

        i += 1

    return lines


def is_strikethrough_line(x0, y0, x1, y1, text_spans):
    """
    Return spans whose horizontal midpoint overlaps this line and whose
    vertical midpoint is close to the line.
    """
    line_y_mid = (y0 + y1) / 2
    line_h = abs(y1 - y0)
    line_w = abs(x1 - x0)

    if line_w < 5:  # too short
        return []

    matched = []
    for span in text_spans:
        sx0, sy0, sx1, sy1 = span["bbox"]
        span_y_mid = (sy0 + sy1) / 2
        span_h = sy1 - sy0

        # Vertical check: line passes through ~30-70% height of span (middle third)
        vert_ok = abs(line_y_mid - span_y_mid) < (span_h * 0.5)
        if not vert_ok:
            continue

        # Horizontal overlap check: >30% of span width covered by the line
        horiz_overlap = max(0, min(x1, sx1) - max(x0, sx0))
        if span_h > 0 and horiz_overlap / max(sx1 - sx0, 1) > 0.3:
            matched.append(span)

    return matched


# ── Scan page 4 (index 3) which has the most path objects ─────────────────────

PAGE_INDICES = [3, 4, 7, 14]  # pages with many paths

for page_idx in PAGE_INDICES:
    page_pdf = reader.pages[page_idx]
    page_h = float(page_pdf.mediabox.height)
    page_w = float(page_pdf.mediabox.width)

    raw = get_page_content(page_pdf)
    drawn_lines = parse_drawn_lines(raw, page_h)

    # Filter to thin horizontal lines (likely strikethrough/underline)
    thin_lines = [
        (x0, y0, x1, y1)
        for x0, y0, x1, y1 in drawn_lines
        if abs(y1 - y0) < 3 and abs(x1 - x0) > 5
    ]

    print(f"\n=== Page {page_idx + 1} ({page_w:.0f}x{page_h:.0f}) ===")
    print(f"  Total drawn segments: {len(drawn_lines)}")
    print(f"  Thin horizontal lines: {len(thin_lines)}")

    if not thin_lines:
        print("  (No thin horizontal lines found on this page)")
        continue

    # Extract text spans via pdfminer for this page only
    text_spans = []
    page_layout_gen = extract_pages(str(pdf_path), page_numbers=[page_idx])
    for page_layout in page_layout_gen:
        for element in page_layout:
            if not isinstance(element, LTTextBox):
                continue
            for line in element:
                if not isinstance(line, LTTextLine):
                    continue
                span_text = ""
                span_x0 = None
                span_chars = []
                for char in line:
                    if isinstance(char, LTChar):
                        if span_x0 is None:
                            span_x0 = char.x0
                        span_chars.append(char)
                        span_text += char.get_text()
                    elif isinstance(char, LTAnno):
                        span_text += char.get_text()
                if span_text.strip() and span_chars:
                    all_x0 = [c.x0 for c in span_chars]
                    all_x1 = [c.x1 for c in span_chars]
                    all_y0 = [c.y0 for c in span_chars]
                    all_y1 = [c.y1 for c in span_chars]
                    text_spans.append(
                        {
                            "text": span_text.strip(),
                            "bbox": (
                                min(all_x0),
                                page_h - max(all_y1),  # display y
                                max(all_x1),
                                page_h - min(all_y0),
                            ),
                        }
                    )

    # Match lines to spans
    struck_texts = set()
    for x0, y0, x1, y1 in thin_lines:
        matched = is_strikethrough_line(x0, y0, x1, y1, text_spans)
        for span in matched:
            struck_texts.add(span["text"])

    print(f"  Text spans matched to drawn lines ({len(struck_texts)}):")
    for t in sorted(struck_texts):
        print(f"    ~~{t}~~")
