import re
from mineru.utils.strikethrough_utils import _substitute_struck_phrases

toc_sample = (
    "# ~~TABLE OF CONTENTS~~\n\n# ~~GENERAL~~\n\n"
    "1. ETHICS COMPLIANCE 3   \n"
    "2. DEFINITIONS 3\n\n"
    "# ~~BID SUBMISSION~~\n\n"
    "3. INTERNATIONAL BIDDING 5   \n"
    "7. BID CONTENTS 5   \n"
    "8. EXTRANEOUS TERMS 5   \n"
    "9. CONFIDENTIAL/TRADE SECRET MATERIALS 6   \n"
    "~~10. PREVAILING WAGE RATES - PUBLIC WORKS AND~~ BUILDING SERVICES CONTRACTS 6   \n"
    "11. TAXES 7   \n"
    "12. EXPENSES PRIOR TO CONTRACT EXECUTION 7   \n"
    "13. CONTRACT PUBLICITY 87   \n"
    "14. PRODUCT REFERENCES 8   \n"
    "15. RESERVED 8   \n"
    "~~16. PRODUCTS MANUFACTURED IN PUBLIC~~ INSTITUTIONS 8   \n"
    "17. PRICING 8"
)

test_phrases = [
    "1. ETHICS COMPLIANCE",
    "2. DEFINITIONS",
    "3. INTERNATIONAL BIDDING",
    "7. BID CONTENTS",
    "8. EXTRANEOUS TERMS",
    "11. TAXES",
    "13. CONTRACT PUBLICITY",
    "14. PRODUCT REFERENCES",
    "17. PRICING",
]

print("=== Individual phrase regex test ===")
for phrase in test_phrases:
    parts = re.split(r"([\s_]+)", phrase)
    regex_parts = []
    for part in parts:
        if re.match(r"[\s_]+", part):
            regex_parts.append(r"[\s_]*")
        else:
            regex_parts.append(r"[\s_]*".join(re.escape(c) for c in part))
    pattern = "".join(regex_parts)
    m = re.search(r"(?<!~)" + pattern + r"(?!~)", toc_sample)
    status = f"MATCH={repr(m.group(0))}" if m else "NO MATCH"
    print(f"  {repr(phrase)}: {status}")

print("\n=== After _substitute_struck_phrases ===")
result = _substitute_struck_phrases(toc_sample, test_phrases)
for line in result.splitlines():
    print(f"  {line}")
