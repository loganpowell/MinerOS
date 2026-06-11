"""Read raw content stream of page 4 to see PDF operators for strikethrough."""

from pathlib import Path
import pypdf

pdf_path = Path(__file__).parent.parent / "demo/pdfs/strikethrough.pdf"
reader = pypdf.PdfReader(str(pdf_path))

# Page 4 (index 3) has 191 path objects
page = reader.pages[3]
content = page.get_contents()

if hasattr(content, "get_data"):
    data = content.get_data().decode("latin-1", errors="replace")
elif isinstance(content, (list, tuple)):
    data = b"".join(c.get_data() for c in content).decode("latin-1", errors="replace")
else:
    data = str(content)

# Show a snippet that likely contains strikethrough lines (look for 'l' or 're' operators near 'm')
lines = data.split("\n")
print(f"Page 4 content stream: {len(lines)} lines, {len(data)} bytes")
print()

# Find lines with drawing operators
draw_ops = ["m", "l", "re", "h", "f", "F", "S", "s", "B", "b", "W", "c", "v", "y"]
sample_lines = []
for i, line in enumerate(lines):
    parts = line.strip().split()
    if parts and parts[-1] in draw_ops[:6]:  # path-drawing operators
        sample_lines.append((i, line.strip()))

print(f"Path drawing operators found: {len(sample_lines)}")
print()
print("Sample of path operations (first 40):")
# Show in context of 2 lines before
shown = set()
for i, (lineno, line) in enumerate(sample_lines[:40]):
    ctx_start = max(0, lineno - 2)
    ctx = "\n".join(
        f"  {lines[j]}" for j in range(ctx_start, min(lineno + 3, len(lines)))
    )
    print(f"\n--- near line {lineno} ---")
    print(ctx)
    if i >= 20:
        break
