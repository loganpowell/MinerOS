"""Test VLM strikethrough substitution on the existing middle JSON + sample PDF."""

import json
import copy
from mineros.utils.strikethrough_utils import (
    _parse_thin_horizontal_lines,
    _get_struck_phrases_from_page,
    substitute_strikethrough_in_vlm_pdf_info,
)
import pypdf
import pypdfium2 as pdfium
import io
from mineros.utils.pdfium_guard import pdfium_guard

pdf_bytes = open("demo/pdfs/strikethrough.pdf", "rb").read()
pypdf_reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
with pdfium_guard():
    pdfium_doc = pdfium.PdfDocument(io.BytesIO(pdf_bytes))

try:
    page_height = 792.0
    pypdf_page = pypdf_reader.pages[3]
    with pdfium_guard():
        pdfium_page = pdfium_doc[3]

    thin_lines = _parse_thin_horizontal_lines(pypdf_page)
    print(f"Thin lines on page 4: {len(thin_lines)}")

    phrases = _get_struck_phrases_from_page(pdfium_page, thin_lines, page_height)
    print(f"\nStruck phrases ({len(phrases)}):")
    for p in phrases:
        print(f"  {p!r}")

    # Test substitution on a known VLM output string
    test_content = (
        "3. Three and one-half Four percent of funds may be allocated to NVTC"
    )
    from mineros.utils.strikethrough_utils import _substitute_struck_phrases

    result = _substitute_struck_phrases(test_content, phrases)
    print(f"\nSubstitution test:")
    print(f"  IN:  {test_content!r}")
    print(f"  OUT: {result!r}")
    assert (
        "~~Three and one-half~~" in result
    ), f"Expected ~~Three and one-half~~ in {result!r}"
    assert "~~Three and one-half~~" not in result.replace(
        "~~Three and one-half~~", ""
    ), False
    print("  OK")

    # Test on the actual saved middle JSON
    with open("output/strikethrough/vlm/strikethrough_middle.json") as f:
        mj = json.load(f)
    mj_copy = copy.deepcopy(mj)

    substitute_strikethrough_in_vlm_pdf_info(mj_copy["pdf_info"], pdf_bytes)

    # Find the "Three and one-half" span
    found = False
    for page_info in mj_copy["pdf_info"]:
        outer_blocks = page_info.get("para_blocks", [])
        for outer in outer_blocks:
            for inner in outer.get("blocks", []):
                for line in inner.get("lines", []):
                    for span in line.get("spans", []):
                        c = span.get("content", "")
                        if "Three" in c:
                            print(f"\nSpan with 'Three':")
                            print(f"  {c[:120]!r}")
                            if "~~Three and one-half~~" in c:
                                found = True
    if found:
        print("\nVLM substitution: OK — ~~Three and one-half~~ found in output")
    else:
        print("\nVLM substitution: MISS — strikethrough not found in span content")
finally:
    with pdfium_guard():
        pdfium_doc.close()
