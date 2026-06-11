"""Quick validation of the two fixes."""

import pypdf, io
import pypdfium2 as pdfium
from mineru.utils.strikethrough_utils import (
    _parse_thin_horizontal_lines,
    _get_struck_phrases_from_page,
    _substitute_struck_phrases,
)
from mineru.utils.pdfium_guard import pdfium_guard

pdf_path = "demo/pdfs/22802bid03_appendixbtracked_0.pdf"
with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
with pdfium_guard():
    doc = pdfium.PdfDocument(io.BytesIO(pdf_bytes))

for pg_idx, label in [(1, "TOC (page 2)"), (4, "Definitions (page 5)")]:
    page = reader.pages[pg_idx]
    mbox = page.mediabox
    page_height = float(mbox.height)
    thin_lines = _parse_thin_horizontal_lines(page)

    with pdfium_guard():
        pdfium_page = doc[pg_idx]

    phrases = _get_struck_phrases_from_page(pdfium_page, thin_lines, page_height)
    print(f"\n=== {label}: {len(phrases)} struck phrases ===")
    for p in phrases[:20]:
        print(f"  {repr(p)}")

# Test fix 2: flexible whitespace matching
print("\n=== Fix 2: whitespace normalization test ===")
test_phrase = "Licensed Softwareall offerings under this contract."
test_content = (
    'The term "Product" includes Licensed Software all offerings under this contract.'
)
result = _substitute_struck_phrases(test_content, [test_phrase])
print(f"  Input:  {repr(test_content)}")
print(f"  Phrase: {repr(test_phrase)}")
print(f"  Result: {repr(result)}")
print(f"  ✓ strikethrough applied" if "~~" in result else "  ✗ NO match")

with pdfium_guard():
    doc.close()
