"""
End-to-end test: synthetic middle JSON + strikethrough detection + markdown rendering.

Doesn't require ML models — exercises the full rendering pipeline.
"""

import io
import sys
import pypdf

# Build synthetic middle JSON with known struck spans
from mineru.utils.strikethrough_utils import tag_strikethrough_in_pdf_info
from mineru.backend.pipeline.pipeline_middle_json_mkcontent import union_make
from mineru.utils.enum_class import MakeMode

# Test A: Rendering — does _apply_span_style render strikethrough correctly?
print("=== Test A: _apply_span_style rendering ===")
from mineru.backend.pipeline.pipeline_middle_json_mkcontent import _apply_span_style

cases = [
    (["strikethrough"], "hello", "~~hello~~"),
    (["bold", "strikethrough"], "hi", "~~**hi**~~"),
    (["italic", "strikethrough"], "yo", "~~*yo*~~"),
    (["bold", "italic", "strikethrough"], "all", "~~***all***~~"),
    ([], "plain", "plain"),
]
for style, text, expected in cases:
    result = _apply_span_style(text, style)
    status = "OK" if result == expected else f"FAIL (got {result!r})"
    print(f"  style={style} input={text!r} -> {result!r}  {status}")

# Test B: Full pipeline — synthetic para_blocks go through union_make
print("\n=== Test B: union_make with strikethrough spans ===")
synthetic_pdf_info = [
    {
        "page_idx": 0,
        "page_size": [612, 792],
        "para_blocks": [
            {
                "type": "text",
                "lines": [
                    {
                        "spans": [
                            {
                                "type": "text",
                                "content": "Keep this",
                                "bbox": [72, 100, 200, 115],
                                "style": [],
                            },
                            {
                                "type": "text",
                                "content": "delete this",
                                "bbox": [205, 100, 350, 115],
                                "style": ["strikethrough"],
                            },
                            {
                                "type": "text",
                                "content": "keep too",
                                "bbox": [355, 100, 450, 115],
                                "style": [],
                            },
                        ]
                    }
                ],
            }
        ],
    }
]

md = union_make(synthetic_pdf_info, MakeMode.MM_MD, "")
md_str = "".join(md) if isinstance(md, list) else str(md)
print("Output markdown:", repr(md_str))
has_strikethrough = "~~delete this~~" in md_str
print("Contains ~~delete this~~:", has_strikethrough)

# Test C: Detection on real PDF
print("\n=== Test C: Detection on demo/pdfs/strikethrough.pdf page 4 ===")
pdf_bytes = open("demo/pdfs/strikethrough.pdf", "rb").read()
test_page_info = {
    "page_idx": 3,
    "page_size": [612, 792],
    "para_blocks": [
        {
            "type": "text",
            "lines": [
                {
                    "spans": [
                        # "Twenty-four" area on page 4 ~ x:[86,144], display_y:[166,180]
                        {
                            "type": "text",
                            "content": "Twenty-four",
                            "bbox": [86, 166, 144, 180],
                        },
                        # Something in unstyled area
                        {
                            "type": "text",
                            "content": "normal text",
                            "bbox": [300, 400, 480, 415],
                        },
                    ]
                }
            ],
        }
    ],
}
tag_strikethrough_in_pdf_info([test_page_info], pdf_bytes)
for span in test_page_info["para_blocks"][0]["lines"][0]["spans"]:
    print(f"  {span['content']!r} -> style={span.get('style', [])}")

print("\nAll end-to-end tests done!")
