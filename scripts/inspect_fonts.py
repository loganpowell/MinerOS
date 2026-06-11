"""Inspect all font names in the PDF to find strikethrough-related fonts."""

import collections
from pathlib import Path
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTChar, LTAnno, LTTextBox, LTTextLine

pdf_path = Path(__file__).parent.parent / "demo/pdfs/strikethrough.pdf"
fonts_seen = collections.Counter()
char_samples = collections.defaultdict(list)

for page_num, page_layout in enumerate(extract_pages(str(pdf_path))):
    for element in page_layout:
        if not isinstance(element, LTTextBox):
            continue
        for line in element:
            if not isinstance(line, LTTextLine):
                continue
            for char in line:
                if isinstance(char, LTChar):
                    fname = char.fontname
                    fonts_seen[fname] += 1
                    if len(char_samples[fname]) < 6:
                        char_samples[fname].append(char.get_text())

print("Distinct fonts and sample chars:")
for fname, count in fonts_seen.most_common():
    chars = "".join(char_samples[fname])
    print(f"  {fname:58s}  n={count:5d}  sample={repr(chars)}")
