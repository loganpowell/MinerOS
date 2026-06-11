"""Quick test for strikethrough_utils.py logic."""

import pypdf
import io
from mineru.utils.strikethrough_utils import (
    _parse_thin_horizontal_lines,
    _tag_strikethrough_in_para_blocks,
    tag_strikethrough_in_pdf_info,
)

pdf_bytes = open("demo/pdfs/strikethrough.pdf", "rb").read()
reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
page = reader.pages[3]  # page 4 (0-indexed)
lines = _parse_thin_horizontal_lines(page)
print(f"Page 4 thin lines found: {len(lines)}")
print(f"Sample lines (PDF coords, y=0 bottom): {lines[:3]}")

# Test tagging with synthetic spans.
# Line (86.84, 625.19, 143.56, 625.19) at y_pdf = 625.19
# For page_height = 792: display center = 792 - 625.19 = 166.81
# Span at display [80, 159, 150, 175] has midpoint 167 → should match
# Span at display [250, 159, 350, 175] is far right → should NOT match
page_height = 792.0
para_blocks = [
    {
        "lines": [
            {
                "spans": [
                    {
                        "bbox": [80, 159, 150, 175],
                        "type": "text",
                        "content": "Twenty-four",
                    },
                    {
                        "bbox": [250, 159, 350, 175],
                        "type": "text",
                        "content": "no strike",
                    },
                ]
            }
        ]
    }
]
_tag_strikethrough_in_para_blocks(para_blocks, lines, page_height)
for span in para_blocks[0]["lines"][0]["spans"]:
    print(repr(span["content"]), "->", span.get("style", []))

# Also test the public API with a real PDF
pdf_info = [
    {
        "page_idx": 3,
        "page_size": [612, 792],
        "para_blocks": para_blocks,
    }
]
# Reset spans
for span in para_blocks[0]["lines"][0]["spans"]:
    span.pop("style", None)

tag_strikethrough_in_pdf_info(pdf_info, pdf_bytes)
print("\nAfter tag_strikethrough_in_pdf_info:")
for span in para_blocks[0]["lines"][0]["spans"]:
    print(repr(span["content"]), "->", span.get("style", []))

print("\nAll tests passed!")
