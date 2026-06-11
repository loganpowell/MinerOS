"""Apply the strikethrough fix to pipeline_middle_json_mkcontent.py and verify."""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
file_path = ROOT / "mineru/backend/pipeline/pipeline_middle_json_mkcontent.py"

src = file_path.read_text(encoding="utf-8")

# ── Verify tilde fix in markdown_utils.py ─────────────────────────────────────
utils_path = ROOT / "mineru/backend/utils/markdown_utils.py"
utils_src = utils_path.read_text(encoding="utf-8")
if '"~"' in utils_src or "'~'" in utils_src:
    print("⚠  ~ still present in CONSERVATIVE_MARKDOWN_SPECIAL_CHARS — fixing…")
    utils_src = utils_src.replace('("*", "_", "`", "~", "$")', '("*", "_", "`", "$")')
    utils_path.write_text(utils_src, encoding="utf-8")
    print("✓  tilde removed from escape chars")
else:
    print("✓  tilde already removed from escape chars")

# ── Apply _apply_span_style + updated _render_span ────────────────────────────
if "_apply_span_style" in src:
    print("✓  _apply_span_style already present")
else:
    MARKER = "def _render_span(span, escape_markdown=True):"
    if MARKER not in src:
        print("✗  Could not find _render_span — aborting")
        sys.exit(1)

    HELPER = '''\
def _apply_span_style(content: str, style: list) -> str:
    """Apply bold/italic/strikethrough Markdown wrappers to a rendered text span."""
    if not style or not content:
        return content
    if 'bold' in style and 'italic' in style:
        content = f'***{content}***'
    elif 'bold' in style:
        content = f'**{content}**'
    elif 'italic' in style:
        content = f'*{content}*'
    if 'strikethrough' in style:
        content = f'~~{content}~~'
    return content


'''

    src = src.replace(MARKER, HELPER + MARKER, 1)
    print("✓  _apply_span_style injected")

    # Now patch the return site inside _render_span
    OLD_RETURN = "    return span_type, content\n\n\ndef _join_rendered_span"
    NEW_RETURN = """\
    # Apply inline text styles (bold, italic, strikethrough) after stripping.
    if span_type == ContentType.TEXT:
        style = span.get('style', [])
        if style:
            content = _apply_span_style(content, style)

    return span_type, content


def _join_rendered_span"""
    if OLD_RETURN in src:
        src = src.replace(OLD_RETURN, NEW_RETURN, 1)
        print("✓  style application injected in _render_span return site")
    else:
        print("⚠  Could not find exact return site — checking nearby…")
        # Fallback: find `return span_type, content` inside _render_span
        idx = src.find("def _render_span")
        chunk = src[idx : idx + 1200]
        print(repr(chunk[-200:]))

    file_path.write_text(src, encoding="utf-8")

print("\nDone. Run: python scripts/run_test.py")
