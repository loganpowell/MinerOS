"""VLM-based table extraction for inline DOCX images.

When a DOCX contains a table pasted as a screenshot (or exported as an image),
the normal DOCX XML parser produces a plain IMAGE block with no structure.
This module optionally promotes such IMAGE blocks to TABLE blocks by running
the VLM's table-recognition prompt against the image.

The VLM is only called when ``MINEROS_VL_SERVER`` is set or a local model
is configured; if neither is available the page blocks are returned unchanged.

Aspect-ratio guard
------------------
Only images wider than they are tall (landscape-ish, ratio >= 1.0) are
candidates for table extraction. Portrait images (logos, photos, charts)
are left as IMAGE blocks.
"""
import base64
import os
from io import BytesIO

from loguru import logger

# Minimum width-to-height ratio for an image to be considered a table candidate.
_MIN_TABLE_ASPECT_RATIO = 1.0


def _get_vlm_predictor():
    """Return a MinerUClient predictor if the VLM is reachable, else None."""
    server_url = os.getenv("MINERU_VL_SERVER") or os.getenv("MINEROS_VL_SERVER")
    if not server_url:
        return None
    try:
        from mineru_vl_utils import MinerUClient

        return MinerUClient(
            backend="http-client",
            server_url=server_url,
            model_name=os.getenv("MINERU_VL_MODEL_NAME", ""),
            api_key=os.getenv("MINERU_VL_API_KEY", ""),
            enable_table_formula_eq_wrap=True,
            image_analysis=False,
        )
    except Exception as exc:
        logger.debug(f"Could not initialise VLM predictor for DOCX image analysis: {exc}")
        return None


def _b64_to_pil(b64_str: str):
    """Decode a base64 image string to a PIL Image."""
    from PIL import Image

    # strip optional data-URI prefix
    if "," in b64_str:
        b64_str = b64_str.split(",", 1)[1]
    return Image.open(BytesIO(base64.b64decode(b64_str)))


def _is_table_candidate(pil_image) -> bool:
    w, h = pil_image.size
    if h == 0:
        return False
    return (w / h) >= _MIN_TABLE_ASPECT_RATIO


def _extract_table_html(predictor, pil_image) -> str | None:
    """Ask the VLM to extract table HTML from a PIL image.

    Returns the HTML string on success, or None if the VLM produces no
    useful output or raises an exception.
    """
    try:
        result = predictor.content_extract(pil_image, type="table")
        if result is None:
            return None
        html = str(result).strip()
        # Require at minimum a <table> tag to consider this a real table.
        if "<table" not in html.lower():
            return None
        return html
    except Exception as exc:
        logger.debug(f"VLM table extraction failed for DOCX image: {exc}")
        return None


def promote_image_blocks_to_tables(page_blocks: list[dict]) -> list[dict]:
    """Walk page_blocks and upgrade landscape IMAGE blocks to TABLE blocks via VLM.

    This is a no-op if the VLM is not configured.  Returns the (possibly
    modified) page_blocks list.
    """
    predictor = _get_vlm_predictor()
    if predictor is None:
        return page_blocks

    promoted = 0
    for block in page_blocks:
        if block.get("type") != "image":
            continue
        b64 = block.get("content", "")
        if not b64:
            continue
        try:
            pil_image = _b64_to_pil(b64)
        except Exception:
            continue
        if not _is_table_candidate(pil_image):
            continue

        html = _extract_table_html(predictor, pil_image)
        if html:
            block["type"] = "table"
            block["content"] = html
            promoted += 1
            logger.debug(f"Promoted DOCX image block to table ({pil_image.size})")

    if promoted:
        logger.info(f"Promoted {promoted} DOCX image block(s) to TABLE via VLM")
    return page_blocks
