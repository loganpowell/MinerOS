"""
Strikethrough fix test script.

Usage:
  # Test the markdown rendering layer with synthetic data (no ML required):
  python test_strikethrough.py

  # Inspect a PDF for StrikeOut annotations:
  python test_strikethrough.py --inspect path/to/file.pdf

  # Process a PDF through the txt-mode text pipeline and show markdown output:
  python test_strikethrough.py --pdf path/to/file.pdf
"""

import argparse
import sys
from pathlib import Path

# ── Synthetic rendering tests ──────────────────────────────────────────────────


def test_rendering():
    """Test the markdown rendering layer directly with synthetic para_blocks."""
    from mineru.backend.pipeline.pipeline_middle_json_mkcontent import (
        merge_para_with_text,
    )
    from mineru.utils.enum_class import ContentType, BlockType

    def make_text_span(content, styles=None):
        span = {"type": ContentType.TEXT, "content": content}
        if styles:
            span["style"] = styles
        return span

    def make_para_block(spans):
        return {
            "type": BlockType.TEXT,
            "lines": [{"spans": spans}],
        }

    print("=" * 60)
    print("Synthetic rendering tests")
    print("=" * 60)

    test_cases = [
        ("Plain text", [make_text_span("Hello world")], None),
        ("Tilde in text", [make_text_span("~approximation~ of ~50%")], None),
        ("Bold span", [make_text_span("Important", styles=["bold"])], None),
        (
            "Strikethrough span",
            [make_text_span("deleted text", styles=["strikethrough"])],
            None,
        ),
        (
            "Bold + strikethrough",
            [make_text_span("deleted bold", styles=["bold", "strikethrough"])],
            None,
        ),
        (
            "Mixed: normal + strikethrough",
            [
                make_text_span("Keep this "),
                make_text_span("remove this", styles=["strikethrough"]),
                make_text_span(" keep this too"),
            ],
            None,
        ),
    ]

    for label, spans, _ in test_cases:
        block = make_para_block(spans)
        result = merge_para_with_text(block, make_mode="markdown", img_buket_path="")
        print(f"\n  [{label}]")
        print(f"    → {repr(result)}")

    print()


# ── PDF annotation inspector ───────────────────────────────────────────────────


def inspect_pdf(pdf_path: str):
    """List all annotations in a PDF, flagging StrikeOut ones."""
    import pypdfium2 as pdfium
    import pypdfium2.raw as pdfium_c

    ANNOT_SUBTYPE_NAMES = {
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
        14: "Caret",
        15: "Ink",
        16: "Popup",
        17: "FileAttachment",
        18: "Sound",
        19: "Movie",
        20: "Widget",
        21: "Screen",
        22: "PrinterMark",
        23: "TrapNet",
        24: "Watermark",
        25: "3D",
        26: "Redact",
    }
    # FPDF_ANNOT_STRIKEOUT = 12 per PDFium source
    STRIKEOUT_SUBTYPE = 12

    print("=" * 60)
    print(f"Inspecting: {pdf_path}")
    print("=" * 60)

    doc = pdfium.PdfDocument(pdf_path)
    total_strikeout = 0

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        page_h = page.get_height()
        annot_count = pdfium_c.FPDFPage_GetAnnotCount(page.raw)

        page_strikeouts = []
        for i in range(annot_count):
            annot = pdfium_c.FPDFPage_GetAnnot(page.raw, i)
            subtype = pdfium_c.FPDFAnnot_GetSubtype(annot)
            name = ANNOT_SUBTYPE_NAMES.get(subtype, f"Unknown({subtype})")

            if subtype == STRIKEOUT_SUBTYPE:
                # Get quad points (each quad = 4 corners = 8 floats)
                quad_count = pdfium_c.FPDFAnnot_CountAttachmentPoints(annot)
                quads = []
                for q in range(quad_count):
                    quad = pdfium_c.FS_QUADPOINTSF()
                    pdfium_c.FPDFAnnot_GetAttachmentPoints(annot, q, quad)
                    # Convert from PDF coords (bottom-left origin) to page coords
                    # Points: x1,y1 (top-left), x2,y2 (top-right), x3,y3 (bottom-left), x4,y4 (bottom-right)
                    x1, y1 = quad.x1, page_h - quad.y1
                    x2, y2 = quad.x2, page_h - quad.y2
                    x3, y3 = quad.x3, page_h - quad.y3
                    x4, y4 = quad.x4, page_h - quad.y4
                    bbox = (
                        min(x1, x2, x3, x4),
                        min(y1, y2, y3, y4),
                        max(x1, x2, x3, x4),
                        max(y1, y2, y3, y4),
                    )
                    quads.append(bbox)
                page_strikeouts.append(quads)
                total_strikeout += 1

            pdfium_c.FPDFPage_CloseAnnot(annot)

        if page_strikeouts:
            print(
                f"\n  Page {page_idx + 1}: {len(page_strikeouts)} StrikeOut annotation(s)"
            )
            for i, quads in enumerate(page_strikeouts):
                for bbox in quads:
                    print(
                        f"    #{i+1} bbox: x0={bbox[0]:.1f} y0={bbox[1]:.1f} x1={bbox[2]:.1f} y1={bbox[3]:.1f}"
                    )
        elif annot_count > 0:
            print(
                f"\n  Page {page_idx + 1}: {annot_count} annotation(s), none are StrikeOut"
            )

    print(f"\nTotal StrikeOut annotations found: {total_strikeout}")
    if total_strikeout == 0:
        print("  ⚠  No StrikeOut annotations detected.")
        print(
            "     Strikethrough may be drawn as path objects (lines) rather than annotations."
        )
        print(
            "     Try a PDF exported from Word or LibreOffice Writer with track-changes strikethrough."
        )
    doc.close()


# ── PDF text extraction test ───────────────────────────────────────────────────


def process_pdf(pdf_path: str, output_dir: str = "/tmp/mineru-strikethrough-test"):
    """
    Run a PDF through the txt-mode text extraction pipeline and print the
    resulting markdown. This exercises the full rendering path without ML.
    """
    import os
    import json
    from mineru.utils.pdf_text_tool import get_page
    from mineru.backend.pipeline.pipeline_middle_json_mkcontent import (
        merge_para_with_text,
    )
    from mineru.utils.enum_class import ContentType, BlockType
    import pypdfium2 as pdfium
    import pypdfium2.raw as pdfium_c
    from mineru.utils.pdfium_guard import pdfium_guard

    STRIKEOUT_SUBTYPE = 12

    print("=" * 60)
    print(f"Processing PDF: {pdf_path}")
    print("=" * 60)

    doc = pdfium.PdfDocument(pdf_path)

    for page_idx in range(min(len(doc), 5)):  # limit to first 5 pages
        page = doc[page_idx]
        page_h = page.get_height()

        # --- Collect StrikeOut annotation bboxes ---
        strikeout_regions = []
        with pdfium_guard():
            annot_count = pdfium_c.FPDFPage_GetAnnotCount(page.raw)
            for i in range(annot_count):
                annot = pdfium_c.FPDFPage_GetAnnot(page.raw, i)
                subtype = pdfium_c.FPDFAnnot_GetSubtype(annot)
                if subtype == STRIKEOUT_SUBTYPE:
                    quad_count = pdfium_c.FPDFAnnot_CountAttachmentPoints(annot)
                    for q in range(quad_count):
                        quad = pdfium_c.FS_QUADPOINTSF()
                        pdfium_c.FPDFAnnot_GetAttachmentPoints(annot, q, quad)
                        x1, y1 = quad.x1, page_h - quad.y1
                        x2, y2 = quad.x2, page_h - quad.y2
                        x3, y3 = quad.x3, page_h - quad.y3
                        x4, y4 = quad.x4, page_h - quad.y4
                        strikeout_regions.append(
                            (
                                min(x1, x2, x3, x4),
                                min(y1, y2, y3, y4),
                                max(x1, x2, x3, x4),
                                max(y1, y2, y3, y4),
                            )
                        )
                pdfium_c.FPDFPage_CloseAnnot(annot)

        print(f"\nPage {page_idx + 1}: {len(strikeout_regions)} StrikeOut region(s)")

        # --- Extract text spans ---
        with pdfium_guard():
            page_data = get_page(page)

        for block in page_data.get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    span_bbox = span.get("bbox")
                    text = span.get("text", "")
                    if not text or not text.strip():
                        continue
                    if span_bbox:
                        # Check overlap with any strikeout region
                        sx0, sy0, sx1, sy1 = span_bbox
                        for rx0, ry0, rx1, ry1 in strikeout_regions:
                            overlap_x = max(0, min(sx1, rx1) - max(sx0, rx0))
                            overlap_w = sx1 - sx0
                            if overlap_w > 0 and overlap_x / overlap_w > 0.3:
                                print(f"  ✓ Strikethrough span: {repr(text)}")
                                break
    doc.close()


# ── Main ───────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Strikethrough fix test utilities")
    parser.add_argument(
        "--inspect", metavar="PDF", help="Inspect PDF for StrikeOut annotations"
    )
    parser.add_argument(
        "--pdf", metavar="PDF", help="Process PDF and show markdown output"
    )
    args = parser.parse_args()

    if args.inspect:
        inspect_pdf(args.inspect)
    elif args.pdf:
        process_pdf(args.pdf)
    else:
        test_rendering()


if __name__ == "__main__":
    main()
