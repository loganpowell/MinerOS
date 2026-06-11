"""Verify position-aware substitution prevents false positives."""

from mineru.utils.strikethrough_utils import _substitute_struck_phrases

# Simulated span content from b1. SOLICITATION body text
body_content = (
    "including but not limited to, Appendix A (Standard Clauses for NYS Contracts), "
    "Appendix B, (General Specifications) and identified attachments."
)

# Phrase as now returned by _get_struck_phrases_from_page:
# ('Appendix B', y_min_disp=61.6, y_max_disp=70.6)
# The body span bbox (display coords): [x0, y0, x1, y1] ~ [36, 430, 585, 530]
# Margin is 8 pts, so sy0=422, sy1=538 — no overlap with y range 61-71.

span_bbox = [36.0, 430.0, 585.0, 530.0]
_Y_MARGIN = 8.0
sy0 = span_bbox[1] - _Y_MARGIN  # 422
sy1 = span_bbox[3] + _Y_MARGIN  # 538

all_page_phrases = [
    ("Appendix B", 61.6, 70.6),  # struck in header, NOT in body
    ("Licensed Software", 521.8, 531.8),  # struck near this span y-range
]

# Filter as done in substitute_strikethrough_in_vlm_pdf_info
span_phrases = [p for p, py0, py1 in all_page_phrases if py0 <= sy1 and py1 >= sy0]
print(f"Span y-range (with margin): [{sy0:.0f}, {sy1:.0f}]")
print(f"Phrase y-ranges: Appendix B=[61,71], Licensed Software=[522,532]")
print(f"Filtered span_phrases: {span_phrases}")

result = _substitute_struck_phrases(body_content, span_phrases)
print(f"\nInput:  {body_content}")
print(f"Result: {result}")
print()
if "Appendix B" not in result.replace("~~Appendix B~~", ""):
    if "~~Appendix B~~" not in result:
        print("✓ 'Appendix B' correctly NOT struck in body paragraph")
    else:
        print("✗ FALSE POSITIVE: 'Appendix B' was struck in body paragraph")
else:
    print("✓ 'Appendix B' not struck (text absent)")
