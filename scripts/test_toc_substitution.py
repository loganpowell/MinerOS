"""Test substitution against actual VLM TOC output."""

import sys

sys.path.insert(0, "/Users/logan.powell/Documents/projects/ctd/MinerU")
import re
from mineru.utils.strikethrough_utils import _substitute_struck_phrases

# Phrases from page 2 (top-20 after fixes)
page2_phrases = [
    "30. ESTIMATED / SPECIFIC QUANTITY CONTRACTS __ 11",
    "62. INDEMNIFICATION RELATING TO INFRINGEMENT2120",
    "63. LIMITATION OF LIABILITY FOR LOT 1 - SOFTWARE",
    "68. OWNERSHIP/TITLE TO PROJECT DELIVERABLES 2927",
    "28. MODIFICATION OF CONTRACT TERMS / ADDITIONAL",
    "72. NO HARDSTOP/PASSIVE LICENSE MONITORING 3129",
    "41. REPAIRED OR REPLACED PARTS / COMPONENTS_13",
    "63B. LIMITATION OF LIABILITY FOR LOT 3 - CLOUD",
    "10. PREVAILING WAGE RATES - PUBLIC WORKS AND",
    "71. CHANGES TO PRODUCT OR SERVICE OFFERINGS",
    "27. PARTICIPATION IN CENTRALIZED CONTRACTS",
    "OR ALTERNATIVE TERMS AND CONDITIONS IN AN",
    "12. EXPENSES PRIOR TO CONTRACT EXECUTION",
    "63A. LIMITATION OF LIABILITY FOR LOT 4 -",
    "35. SHIPPING/RECEIPT OF PHYSICAL PRODUCT",
    "42. EMPLOYEES, SUBCONTRACTORS & AGENTS",
    "9. CONFIDENTIAL/TRADE SECRET MATERIALS",
    "26A. OFFICIAL USE ONLY/NO PERSONAL USE",
    "16. PRODUCTS MANUFACTURED IN PUBLIC",
    "67. AUDIT OF LICENSED PRODUCT USAGE",
]

# Simulate what VLM might output for the TOC (from the existing .md)
# Read from the existing output
md_path = "/Users/logan.powell/Documents/projects/ctd/MinerU/output/22802bid03_appendixbtracked_0/vlm/22802bid03_appendixbtracked_0.md"
with open(md_path) as f:
    existing_md = f.read()

# Extract page 2 section (TABLE OF CONTENTS area)
lines = existing_md.split("\n")
toc_lines = []
in_toc = False
for line in lines:
    if "TABLE OF CONTENTS" in line:
        in_toc = True
    if in_toc:
        toc_lines.append(line)
    if in_toc and len(toc_lines) > 60:
        break

toc_text = "\n".join(toc_lines[:60])
print("=== Current TOC excerpt ===")
for l in toc_lines[:30]:
    print(f"  {l}")

print("\n=== After re-substitution ===")
result = _substitute_struck_phrases(toc_text, page2_phrases)
for l in result.split("\n")[:30]:
    print(f"  {l}")

# Check page 5, item t.
page5_phrases = ["Licensed Software"]
test_item_t = (
    'The term "Product" includes Licensed Software all offerings under this contract.'
)
result_t = _substitute_struck_phrases(test_item_t, page5_phrases)
print(f"\n=== Page 5, item t. ===")
print(f"  Before: {test_item_t}")
print(f"  After:  {result_t}")
