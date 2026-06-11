"""Look at raw PDF page content stream to find strikethrough encoding."""

from pathlib import Path
import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c

pdf_path = Path(__file__).parent.parent / "demo/pdfs/strikethrough.pdf"
doc = pdfium.PdfDocument(str(pdf_path))

# Page 4 has 191 path objects - likely has strikethrough content
page_idx = 3
page = doc[page_idx]
page_h = page.get_height()
page_w = page.get_width()

print(f"Page {page_idx+1}: {page_w:.0f} x {page_h:.0f}")
print()

# Iterate through ALL objects, grab path bounds via raw API
path_bounds = []
for obj in page.get_objects():
    t = pdfium_c.FPDFPageObj_GetType(obj.raw)
    if t == 2:  # PATH
        # Try get_bounds via raw API
        left = pdfium_c.c_float(0)
        bottom = pdfium_c.c_float(0)
        right = pdfium_c.c_float(0)
        top = pdfium_c.c_float(0)
        ok = pdfium_c.FPDFPageObj_GetBounds(
            obj.raw,
            pdfium_c.byref(left),
            pdfium_c.byref(bottom),
            pdfium_c.byref(right),
            pdfium_c.byref(top),
        )
        if ok:
            l, b, r, t2 = left.value, bottom.value, right.value, top.value
            # Convert to display coords
            path_bounds.append(
                {
                    "x0": l,
                    "y0": page_h - t2,
                    "x1": r,
                    "y1": page_h - b,
                    "w": r - l,
                    "h": t2 - b,
                }
            )

print(f"Total paths with valid bounds: {len(path_bounds)}")

# Show thin horizontal ones (strikethrough lines)
thin = [p for p in path_bounds if 0 < p["h"] < 3 and p["w"] > 5]
normal = [p for p in path_bounds if p["w"] > 0 or p["h"] > 0]
zero = [p for p in path_bounds if p["w"] == 0 and p["h"] == 0]

print(f"  Thin horizontal (<3pt tall, >5pt wide): {len(thin)}")
print(f"  Any non-zero bounds: {len(normal)}")
print(f"  Zero-size bounds: {len(zero)}")

if thin:
    print()
    print("Thin paths (likely strikethrough/underline lines):")
    for p in thin[:20]:
        print(
            f"  x0={p['x0']:.1f}  y0={p['y0']:.1f}  x1={p['x1']:.1f}  y1={p['y1']:.1f}  w={p['w']:.1f}  h={p['h']:.2f}"
        )

if normal and not thin:
    print()
    print("Non-zero paths (sample):")
    for p in normal[:10]:
        print(
            f"  x0={p['x0']:.1f}  y0={p['y0']:.1f}  x1={p['x1']:.1f}  y1={p['y1']:.1f}  w={p['w']:.1f}  h={p['h']:.2f}"
        )

doc.close()
