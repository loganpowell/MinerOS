"""Use pdfminer to extract text with color/font info to identify strikethrough regions."""

from pathlib import Path
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTChar, LTAnno, LTTextBox, LTTextLine
from pdfminer.pdfcolor import PDFColorSpace

pdf_path = Path(__file__).parent.parent / "demo/pdfs/strikethrough.pdf"

print(f"Scanning {pdf_path.name} for text color variations...\n")

color_samples = {}  # color -> list of (page, text_snippet)

for page_num, page_layout in enumerate(extract_pages(str(pdf_path))):
    if page_num >= 4:  # limit scan to first 4 pages
        break

    page_colors = {}
    for element in page_layout:
        if not isinstance(element, LTTextBox):
            continue
        for line in element:
            if not isinstance(line, LTTextLine):
                continue
            line_text = ""
            line_color = None
            for char in line:
                if isinstance(char, LTChar):
                    gs = char.graphicstate
                    # text fill color
                    ncs = getattr(gs, "ncs", None)  # non-stroke colorspace
                    scs = getattr(gs, "scs", None)  # stroke colorspace
                    fc = getattr(gs, "ncolor", None)  # fill color
                    sc = getattr(gs, "scolor", None)  # stroke color
                    color = str(fc)
                    if line_color is None:
                        line_color = color
                    elif color != line_color:
                        line_color = "MIXED"
                    line_text += char.get_text()
                elif isinstance(char, LTAnno):
                    line_text += char.get_text()

            line_text = line_text.strip()
            if line_text and line_color and line_color != "MIXED":
                if line_color not in color_samples:
                    color_samples[line_color] = []
                color_samples[line_color].append((page_num + 1, line_text[:60]))

print("Distinct text colors found:")
for color, samples in sorted(color_samples.items()):
    print(f"\n  Color {color}  ({len(samples)} lines)")
    for page, text in samples[:3]:
        print(f"    page {page}: {repr(text)}")
