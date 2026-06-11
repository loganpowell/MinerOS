"""Inspect the strikethrough PDF more deeply — find path objects over text."""

import sys
from pathlib import Path

import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c

pdf_path = Path(__file__).parent.parent / "demo/pdfs/strikethrough.pdf"
doc = pdfium.PdfDocument(str(pdf_path))

print(f"Pages: {len(doc)}\n")

for page_idx in range(len(doc)):
    page = doc[page_idx]
    page_h = page.get_height()
    page_w = page.get_width()

    print(f"=== Page {page_idx + 1} ({page_w:.0f} x {page_h:.0f}) ===")

    # Enumerate ALL page object types
    type_counts = {}
    path_objects = []
    text_objects = []

    for obj in page.get_objects():
        t = pdfium_c.FPDFPageObj_GetType(obj.raw)
        type_name = {1: "TEXT", 2: "PATH", 3: "IMAGE", 4: "SHADING", 5: "FORM"}.get(
            t, f"?{t}"
        )
        type_counts[type_name] = type_counts.get(type_name, 0) + 1

        if t == 2:  # PATH
            left, bottom, right, top = 0.0, 0.0, 0.0, 0.0
            try:
                bounds = obj.get_bounds()
                left, bottom, right, top = bounds
            except Exception:
                pass
            # Convert from PDF coords (y=0 at bottom) to display coords (y=0 at top)
            path_objects.append(
                {
                    "x0": left,
                    "y0": page_h - top,
                    "x1": right,
                    "y1": page_h - bottom,
                    "height": top - bottom,
                    "width": right - left,
                }
            )

    print(f"  Object types: {type_counts}")

    # Show thin horizontal paths (likely strikethrough lines)
    thin_lines = [p for p in path_objects if 0 < p["height"] < 3 and p["width"] > 5]
    if thin_lines:
        print(
            f"  Thin horizontal paths (likely strikethrough/underline): {len(thin_lines)}"
        )
        for p in thin_lines[:10]:
            print(
                f"    x0={p['x0']:.1f}  y0={p['y0']:.1f}  x1={p['x1']:.1f}  y1={p['y1']:.1f}"
                f"  w={p['width']:.1f}  h={p['height']:.2f}"
            )
    else:
        print(f"  No thin horizontal paths found (total paths: {len(path_objects)})")
        if path_objects:
            print("  Sample paths:")
            for p in path_objects[:5]:
                print(
                    f"    x0={p['x0']:.1f}  y0={p['y0']:.1f}  x1={p['x1']:.1f}  y1={p['y1']:.1f}"
                    f"  w={p['width']:.1f}  h={p['height']:.2f}"
                )

    # Show all annotations (any type)
    annot_count = pdfium_c.FPDFPage_GetAnnotCount(page.raw)
    SUBTYPE_NAMES = {
        1: "Text",
        2: "Link",
        3: "FreeText",
        4: "Line",
        5: "Square",
        6: "Circle",
        7: "Polygon",
        8: "PolyLine",
        9: "Highlight",
        10: "Underline",
        11: "Squiggly",
        12: "StrikeOut",
        13: "Stamp",
        20: "Widget",
    }
    if annot_count:
        print(f"  Annotations ({annot_count}):")
        for i in range(annot_count):
            annot = pdfium_c.FPDFPage_GetAnnot(page.raw, i)
            subtype = pdfium_c.FPDFAnnot_GetSubtype(annot)
            name = SUBTYPE_NAMES.get(subtype, f"type{subtype}")
            print(f"    #{i+1} subtype={name}({subtype})")
            pdfium_c.FPDFPage_CloseAnnot(annot)

    # Extract text spans with their bboxes using pdftext
    from mineru.utils.pdf_text_tool import get_page_chars
    from mineru.utils.pdfium_guard import pdfium_guard
    from pdftext.pdf.pages import assign_scripts, get_blocks, get_lines, get_spans

    with pdfium_guard():
        chars_data = get_page_chars(page)

    spans_raw = get_spans(chars_data["chars"])
    lines_raw = get_lines(spans_raw)

    print(f"  Text spans extracted: {sum(len(l.get('spans', [])) for l in lines_raw)}")
    for line in lines_raw[:5]:
        for sp in line.get("spans", [])[:3]:
            text = sp.get("text", "").strip()
            bbox = sp.get("bbox")
            if text and bbox:
                print(
                    f"    text={repr(text[:40]):42s} bbox={[round(x,1) for x in bbox.bbox]}"
                )

    print()

doc.close()
