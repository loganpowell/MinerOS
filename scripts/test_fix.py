"""Run after-fix verification and PDF annotation inspection."""

import sys
from pathlib import Path

# ── Rendering tests ────────────────────────────────────────────────────────────
from mineru.backend.pipeline.pipeline_middle_json_mkcontent import (
    merge_para_with_text,
    escape_special_markdown_char,
)
from mineru.utils.enum_class import ContentType, BlockType


def blk(spans):
    return {"type": BlockType.TEXT, "lines": [{"spans": spans}]}


def span(text, style=None):
    s = {"type": ContentType.TEXT, "content": text}
    if style:
        s["style"] = style
    return s


print("=== Rendering layer (no ML required) ===\n")
print("Tilde in plain text:", repr(escape_special_markdown_char("~approx~ or ~50%")))
print()

cases = [
    ("plain text", [span("Hello world")]),
    ("strikethrough", [span("deleted text", ["strikethrough"])]),
    ("bold", [span("important", ["bold"])]),
    ("italic", [span("emphasis", ["italic"])]),
    (
        "bold+italic+strikethrough",
        [span("all three", ["bold", "italic", "strikethrough"])],
    ),
    (
        "mixed inline",
        [span("Keep "), span("remove this", ["strikethrough"]), span(" keep")],
    ),
]

for label, spans in cases:
    result = merge_para_with_text(blk(spans))
    print(f"  {label:32s} -> {repr(result)}")

# ── PDF annotation inspection ──────────────────────────────────────────────────
pdf_path = Path(__file__).parent.parent / "demo/pdfs/strikethrough.pdf"
if not pdf_path.exists():
    print(f"\nPDF not found at {pdf_path}")
    sys.exit(0)

print(f"\n=== StrikeOut annotations in {pdf_path.name} ===\n")

import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c

# FPDF_ANNOT_STRIKEOUT = 12  (per pdfium/fpdf_annot.h)
STRIKEOUT = 12
SUBTYPE_NAMES = {
    9: "Highlight",
    10: "Underline",
    11: "Squiggly",
    12: "StrikeOut",
    1: "Text",
    2: "Link",
}

doc = pdfium.PdfDocument(str(pdf_path))
total = 0

for page_idx in range(len(doc)):
    page = doc[page_idx]
    page_h = page.get_height()
    count = pdfium_c.FPDFPage_GetAnnotCount(page.raw)
    if count == 0:
        continue

    page_hits = []
    for i in range(count):
        annot = pdfium_c.FPDFPage_GetAnnot(page.raw, i)
        subtype = pdfium_c.FPDFAnnot_GetSubtype(annot)
        name = SUBTYPE_NAMES.get(subtype, f"type{subtype}")

        if subtype == STRIKEOUT:
            qcount = pdfium_c.FPDFAnnot_CountAttachmentPoints(annot)
            bboxes = []
            for q in range(qcount):
                quad = pdfium_c.FS_QUADPOINTSF()
                pdfium_c.FPDFAnnot_GetAttachmentPoints(annot, q, quad)
                xs = [quad.x1, quad.x2, quad.x3, quad.x4]
                ys = [
                    page_h - quad.y1,
                    page_h - quad.y2,
                    page_h - quad.y3,
                    page_h - quad.y4,
                ]
                bboxes.append((min(xs), min(ys), max(xs), max(ys)))
            page_hits.append(bboxes)
            total += 1
        pdfium_c.FPDFPage_CloseAnnot(annot)

    if page_hits:
        print(f"  Page {page_idx + 1}: {len(page_hits)} StrikeOut annotation(s)")
        for i, bboxes in enumerate(page_hits):
            for bbox in bboxes:
                print(
                    f"    #{i+1}  x0={bbox[0]:.1f} y0={bbox[1]:.1f}"
                    f"  x1={bbox[2]:.1f} y1={bbox[3]:.1f}"
                )

doc.close()
print(f"\nTotal StrikeOut annotations: {total}")
if total == 0:
    print("  No StrikeOut annotations found.")
    print(
        "  The strikethrough may be rendered as drawn lines rather than PDF annotations."
    )
    print("  (This is common in PDFs created outside Word/LibreOffice.)")
