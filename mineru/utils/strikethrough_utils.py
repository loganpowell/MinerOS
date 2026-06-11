"""
Utilities for detecting strikethrough text in PDFs using drawn path objects.

PDFs commonly encode strikethrough with either:
1. Annotation objects (type StrikeOut=12) — handled elsewhere
2. Drawn horizontal line paths in the page content stream — handled here

The content-stream approach parses moveto (m) / lineto (l) / rectangle (re)
operators to find near-zero-height horizontal segments that spatially overlap
text spans, then tags those spans with style: ['strikethrough'].
"""

from __future__ import annotations

import io
import logging

logger = logging.getLogger(__name__)

# Strikethroughs must fall within the *middle zone* of a span or character's
# vertical extent.  The zone is defined as:
#
#   [y_bottom + MARGIN * height,  y_top - MARGIN * height]
#
# A MARGIN of 0.25 means the central 50% of the glyph.  Strikethroughs pass
# through the x-height region (~30–70% from the bottom) so they always land
# inside this zone.  Underlines sit at the baseline (~0–10% from the bottom)
# and overlines at the top (~90–100%), both outside the zone — regardless of
# font size, making this test scale-invariant with no document-specific tuning.
_VERT_ZONE_MARGIN = 0.25

# Minimum horizontal overlap fraction (relative to span width) required for a
# drawn line to be considered a strikethrough for that span.
_HORIZ_OVERLAP_MIN_FRACTION = 0.25

# A drawn segment is considered "thin" (potential strikethrough) if its height
# is at most this many PDF user-space units.
_MAX_LINE_HEIGHT = 3.0

# Minimum width a drawn line must have to be considered (filters out dots)
_MIN_LINE_WIDTH = 5.0


# ---------------------------------------------------------------------------
# Content-stream parser
# ---------------------------------------------------------------------------


def _get_page_content_bytes(page) -> bytes:
    """Return raw content-stream bytes for a pypdf Page."""
    contents = page.get_contents()
    if contents is None:
        return b""
    if isinstance(contents, (list, tuple)):
        return b"".join(obj.get_data() for obj in contents)
    return contents.get_data()


def _parse_thin_horizontal_lines(page) -> list:
    """Return thin horizontal line segments from a pypdf Page's content stream.

    Returns a list of ``(x0, y_mid, x1, y_mid)`` tuples in PDF user-space
    coordinates (y=0 at bottom of page).
    """
    raw = _get_page_content_bytes(page)
    if not raw:
        return []

    tokens = raw.decode("latin-1", errors="replace").split()
    lines = []
    stack = []
    last_move = None

    i = 0
    while i < len(tokens):
        tok = tokens[i]
        i += 1
        try:
            stack.append(float(tok))
            continue
        except ValueError:
            pass

        if tok == "m" and len(stack) >= 2:
            # PDF syntax: x y m  (top of stack is y)
            y, x = stack.pop(), stack.pop()
            last_move = (x, y)
            stack.clear()

        elif tok == "l" and len(stack) >= 2 and last_move is not None:
            # PDF syntax: x y l
            y, x = stack.pop(), stack.pop()
            x0, y0 = last_move
            x1, y1 = x, y
            h = abs(y1 - y0)
            w = abs(x1 - x0)
            if h <= _MAX_LINE_HEIGHT and w >= _MIN_LINE_WIDTH:
                lx0, lx1 = min(x0, x1), max(x0, x1)
                ly = (y0 + y1) / 2
                lines.append((lx0, ly, lx1, ly))
            last_move = (x, y)  # support multi-segment lineto paths
            stack.clear()

        elif tok == "re" and len(stack) >= 4:
            # PDF syntax: x y width height re
            h, w, y, x = stack.pop(), stack.pop(), stack.pop(), stack.pop()
            if abs(h) <= _MAX_LINE_HEIGHT and abs(w) >= _MIN_LINE_WIDTH:
                lx0, lx1 = min(x, x + w), max(x, x + w)
                ly = y + h / 2
                lines.append((lx0, ly, lx1, ly))
            stack.clear()

        else:
            stack.clear()

    return lines


# ---------------------------------------------------------------------------
# Span tagging
# ---------------------------------------------------------------------------


def _tag_strikethrough_in_para_blocks(para_blocks, thin_lines_pdf, page_height):
    """Mutate spans in *para_blocks*, adding ``'strikethrough'`` to their
    ``style`` list when a drawn line overlaps with the span's bounding box.

    Args:
        para_blocks: The ``para_blocks`` list from a page's middle-JSON dict.
        thin_lines_pdf: Thin horizontal segments in PDF coords (y=0 at bottom).
        page_height: Page height in PDF user-space units (points).
    """
    if not thin_lines_pdf or not para_blocks:
        return

    for block in para_blocks:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                bbox = span.get("bbox")
                if not bbox or len(bbox) < 4:
                    continue
                sx0, sy0_disp, sx1, sy1_disp = bbox[:4]
                span_w = sx1 - sx0
                if span_w <= 0:
                    continue

                # Convert display (y=0 top) → PDF (y=0 bottom)
                sy0_pdf = page_height - sy1_disp
                sy1_pdf = page_height - sy0_disp
                span_h = sy1_pdf - sy0_pdf
                if span_h <= 0:
                    continue

                for lx0, ly, lx1, _ in thin_lines_pdf:
                    # Vertical match: line must fall within the middle zone of
                    # the span.  This naturally excludes underlines (at the
                    # bottom of the bbox) and overlines (at the top).
                    zone_lo = sy0_pdf + span_h * _VERT_ZONE_MARGIN
                    zone_hi = sy1_pdf - span_h * _VERT_ZONE_MARGIN
                    if not (zone_lo <= ly <= zone_hi):
                        continue
                    # Horizontal overlap
                    overlap = max(0.0, min(lx1, sx1) - max(lx0, sx0))
                    if overlap / span_w < _HORIZ_OVERLAP_MIN_FRACTION:
                        continue
                    # Tag the span
                    style = span.setdefault("style", [])
                    if "strikethrough" not in style:
                        style.append("strikethrough")
                    break  # one matching line is enough


# ---------------------------------------------------------------------------
# VLM mode: phrase-level extraction + content-string substitution
# ---------------------------------------------------------------------------


def _get_struck_phrases_from_page(pypdfium_page, thin_lines_pdf, page_height):
    """Return a list of struck-through text phrases on a page with their y-extents.

    Extracts character-level bboxes via pdftext, tags each character against
    the drawn strikethrough lines, then groups consecutive struck characters
    into whitespace-normalised phrases suitable for string substitution.

    Args:
        pypdfium_page: A pypdfium2 PdfPage object.
        thin_lines_pdf: Output of ``_parse_thin_horizontal_lines`` for this page.
        page_height: Page height in PDF user-space units.

    Returns:
        List of ``(phrase, y_min_disp, y_max_disp)`` tuples, where y values are
        in display coordinates (y=0 at top).  Sorted longest-phrase-first to
        avoid partial replacements when a short phrase is a substring of a longer.
    """
    try:
        from pdftext.pdf.chars import deduplicate_chars, get_chars
        from mineru.utils.pdfium_guard import pdfium_guard
    except ImportError:
        return []

    try:
        with pdfium_guard():
            textpage = pypdfium_page.get_textpage()
            page_bbox = pypdfium_page.get_bbox()
        chars = deduplicate_chars(get_chars(textpage, page_bbox, 0, True))
    except Exception as exc:
        logger.debug("get_chars failed: %s", exc)
        return []

    if not chars:
        return []

    # Tag each character as struck or not, keeping (x0, x1, y0_disp, y1_disp, char_text)
    # Use a stricter overlap threshold than the span-level check: at the
    # character level a 25% clip is proportionally large, so require 50%.
    _CHAR_OVERLAP_FRACTION = 0.5
    struck = []  # (x0, x1, y0_disp, y1_disp, char_text)
    for char in chars:
        bbox_obj = char.get("bbox")
        if bbox_obj is None:
            continue
        bb = bbox_obj.bbox if hasattr(bbox_obj, "bbox") else list(bbox_obj)
        x0, y0_disp, x1, y1_disp = bb
        char_text = char.get("char", "")
        if not char_text:
            continue

        # Convert display → PDF coords
        y0_pdf = page_height - y1_disp
        y1_pdf = page_height - y0_disp
        char_h = y1_pdf - y0_pdf
        if char_h <= 0:
            continue
        char_w = x1 - x0

        for lx0, ly, lx1, _ in thin_lines_pdf:
            # Same middle-zone test as the span-level check.
            zone_lo = y0_pdf + char_h * _VERT_ZONE_MARGIN
            zone_hi = y1_pdf - char_h * _VERT_ZONE_MARGIN
            if not (zone_lo <= ly <= zone_hi):
                continue
            # Use overlap-fraction rather than a point-in-range check with
            # manual padding.  This mirrors the span-level logic in
            # _tag_strikethrough_in_para_blocks and is scale-invariant: it
            # works for any font size or line extent without needing
            # document-specific tolerance constants.
            if char_w <= 0:
                continue
            overlap = max(0.0, min(lx1, x1) - max(lx0, x0))
            if overlap / char_w < _CHAR_OVERLAP_FRACTION:
                continue
            struck.append((x0, x1, y0_disp, y1_disp, char_text))
            break

    if not struck:
        return []

    # Sort into reading order: top-to-bottom, left-to-right
    struck.sort(key=lambda c: (round(c[2] / 3), c[0]))

    # Group into phrases.
    #   gap < _CHAR_KERN_GAP   → adjacent letters, concatenate directly
    #   _CHAR_KERN_GAP ≤ gap < _PHRASE_BREAK_GAP → word space, insert " "
    #   gap ≥ _PHRASE_BREAK_GAP or y change       → new phrase
    _CHAR_KERN_GAP = 1.5  # PDF points
    _PHRASE_BREAK_GAP = 20.0  # PDF points

    # Each entry: (text, y0_disp_min, y1_disp_max) — track y extents for
    # position-aware substitution (avoids matching unstruck occurrences on
    # other lines/pages).
    phrase_entries = []  # list of [text, y0_min, y1_max]
    current = ""
    cur_y0_min = None
    cur_y1_max = None
    prev_x1 = None
    prev_y = None

    def _flush():
        nonlocal current, cur_y0_min, cur_y1_max
        if current.strip():
            phrase_entries.append([current.strip(), cur_y0_min, cur_y1_max])
        current = ""
        cur_y0_min = None
        cur_y1_max = None

    for x0, x1, y0_disp, y1_disp, ch in struck:
        if prev_y is not None and abs(y0_disp - prev_y) > 4.0:
            _flush()
            current = ch
            cur_y0_min = y0_disp
            cur_y1_max = y1_disp
        elif prev_x1 is not None:
            gap = x0 - prev_x1
            if gap >= _PHRASE_BREAK_GAP or gap < -2.0:
                # Large forward gap → word break between phrases.
                # Negative gap → backwards x-jump meaning a new text object
                # (e.g., bold run rendered after body text in content stream).
                _flush()
                current = ch
                cur_y0_min = y0_disp
                cur_y1_max = y1_disp
            elif gap >= _CHAR_KERN_GAP:
                current += " " + ch
                cur_y0_min = min(cur_y0_min, y0_disp)
                cur_y1_max = max(cur_y1_max, y1_disp)
            else:
                current += ch
                cur_y0_min = min(cur_y0_min, y0_disp)
                cur_y1_max = max(cur_y1_max, y1_disp)
        else:
            current = ch
            cur_y0_min = y0_disp
            cur_y1_max = y1_disp
        prev_x1 = x1
        prev_y = y0_disp

    _flush()

    # Post-process: TOC rows often contain long runs of leader characters
    # ("______..." or ".. .. ..") and may merge two columns into one phrase.
    # Split each raw phrase on runs of 3+ underscores, keeping y-range.
    import re as _re

    def _split_leaders(raw: str, y0_min: float, y1_max: float) -> list:
        parts = _re.split(r"_{3,}", raw)
        out = []
        for part in parts:
            cleaned = part.strip()
            letter_count = sum(1 for c in cleaned if c.isalpha())
            if letter_count >= 3:
                out.append((cleaned, y0_min, y1_max))
        return out

    expanded: list = []
    for text, y0_min, y1_max in phrase_entries:
        expanded.extend(_split_leaders(text, y0_min, y1_max))

    # Deduplicate by phrase text, keeping first occurrence, then sort longest-first
    seen: set = set()
    deduped: list = []
    for entry in expanded:
        if entry[0] not in seen:
            seen.add(entry[0])
            deduped.append(entry)
    deduped.sort(key=lambda e: len(e[0]), reverse=True)
    return deduped  # list of (phrase_str, y_min_disp, y_max_disp)


def _substitute_struck_phrases(content, phrases):
    """Replace each phrase in *content* with ``~~phrase~~``, avoiding double-wrapping.

    *phrases* is a list of plain strings (already filtered to those relevant for
    this span).  Uses a flexible regex that allows optional whitespace between
    every pair of adjacent non-space characters within each word-segment,
    handling merged-word artefacts from pdftext (e.g. ``"Softwareall"`` matching
    ``"Software all"`` in the VLM output).
    """
    import re

    for phrase in phrases:
        # Skip if already wrapped
        if f"~~{phrase}~~" in content:
            continue

        # Build a flexible regex:
        #   - Between whitespace-separated segments: require \s+
        #   - Within each non-whitespace segment: allow \s* between every pair
        #     of adjacent characters (handles merged-word artefacts)
        #   - Treat underscore characters in the phrase as optional whitespace
        #     (\s*) because leader-dot underscores are invisible in VLM output
        parts = re.split(r"([\s_]+)", phrase)
        regex_parts = []
        for part in parts:
            if re.match(r"[\s_]+", part):
                regex_parts.append(r"[\s_]*")
            else:
                # Allow optional whitespace between every adjacent character pair
                regex_parts.append(r"\s*".join(re.escape(c) for c in part))
        pattern = "".join(regex_parts)

        # Find the actual matched text so we can wrap it verbatim (preserving
        # the spacing that is already in the VLM output).
        m = re.search(r"(?<!~)" + pattern + r"(?!~)", content)
        if m:
            matched = m.group(0)
            content = content[: m.start()] + f"~~{matched}~~" + content[m.end() :]
    return content


def _iter_vlm_spans(para_blocks):
    """Yield all span dicts from a VLM para_blocks structure.

    VLM blocks may have either a direct ``lines`` list (pipeline-style) or an
    inner ``blocks`` list containing sub-blocks with their own ``lines``.
    """
    for block in para_blocks:
        # Top-level block may wrap inner blocks (VLM list/group style)
        for inner in block.get("blocks", []):
            for line in inner.get("lines", []):
                yield from line.get("spans", [])
        # Also handle pipeline-style direct lines
        for line in block.get("lines", []):
            yield from line.get("spans", [])


def substitute_strikethrough_in_vlm_pdf_info(pdf_info, pdf_bytes):
    """Post-process VLM *pdf_info* to insert ``~~...~~`` around struck-through text.

    Unlike the pipeline path (which tags word-level spans), VLM spans contain
    full paragraphs.  This function uses pdftext character-level bboxes to
    identify exactly which text strings are struck, then performs string
    substitution directly on ``span['content']``.

    Args:
        pdf_info: List of page dicts from ``middle_json["pdf_info"]``.
        pdf_bytes: Raw bytes of the original PDF file.
    """
    try:
        import pypdf
        import pypdfium2 as pdfium
    except ImportError as exc:
        logger.warning("Missing dependency for VLM strikethrough detection: %s", exc)
        return

    from mineru.utils.pdfium_guard import pdfium_guard

    try:
        pypdf_reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    except Exception as exc:
        logger.debug("Could not open PDF for VLM strikethrough: %s", exc)
        return

    with pdfium_guard():
        pdfium_doc = pdfium.PdfDocument(io.BytesIO(pdf_bytes))

    try:
        for page_info in pdf_info:
            page_idx = page_info.get("page_idx", 0)
            para_blocks = page_info.get("para_blocks")
            if not para_blocks:
                continue

            page_size = page_info.get("page_size", [0, 0])
            page_height = float(page_size[1]) if page_size else 0.0
            if page_height <= 0:
                continue

            try:
                pypdf_page = pypdf_reader.pages[page_idx]
                with pdfium_guard():
                    pdfium_page = pdfium_doc[page_idx]
            except (IndexError, Exception):
                continue

            thin_lines = _parse_thin_horizontal_lines(pypdf_page)
            if not thin_lines:
                continue

            phrases = _get_struck_phrases_from_page(
                pdfium_page, thin_lines, page_height
            )
            if not phrases:
                continue

            logger.debug(
                "Page %d: %d struck phrases to substitute: %s",
                page_idx,
                len(phrases),
                phrases,
            )

            for span in _iter_vlm_spans(para_blocks):
                content = span.get("content")
                if not isinstance(content, str) or not content:
                    continue

                # Filter phrases to those whose y-range overlaps this span's bbox.
                # This prevents false substitution of a struck phrase (e.g.
                # "Appendix B" from a page header) into body paragraphs that
                # happen to contain the same words unstruck.
                span_bbox = span.get("bbox")
                if span_bbox and len(span_bbox) >= 4:
                    # bbox is [x0, y0_disp, x1, y1_disp] in display coords
                    # Add a generous vertical margin (half a typical line height)
                    # so phrases near the span edge still match.
                    _Y_MARGIN = 8.0  # points
                    sy0 = span_bbox[1] - _Y_MARGIN
                    sy1 = span_bbox[3] + _Y_MARGIN
                    span_phrases = [
                        p for p, py0, py1 in phrases if py0 <= sy1 and py1 >= sy0
                    ]
                else:
                    # No bbox available — fall back to using all phrases
                    span_phrases = [p for p, *_ in phrases]

                if not span_phrases:
                    continue

                new_content = _substitute_struck_phrases(content, span_phrases)
                if new_content != content:
                    span["content"] = new_content
    finally:
        with pdfium_guard():
            pdfium_doc.close()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def tag_strikethrough_in_pdf_info(pdf_info, pdf_bytes):
    """Post-process *pdf_info* (the ``pdf_info`` list from the middle JSON) to
    tag text spans that are visually struck through by drawn lines in the PDF.

    This function mutates the spans in-place by adding ``'strikethrough'`` to
    each span's ``style`` list.  The downstream Markdown renderer
    (``_apply_span_style``) already handles this style.

    Args:
        pdf_info: List of page dicts from ``middle_json["pdf_info"]``.
        pdf_bytes: Raw bytes of the original PDF file.
    """
    try:
        import pypdf
    except ImportError:
        logger.warning("pypdf not installed; skipping strikethrough detection.")
        return

    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    except Exception as exc:
        logger.debug("Could not open PDF for strikethrough detection: %s", exc)
        return

    for page_info in pdf_info:
        page_idx = page_info.get("page_idx", 0)
        para_blocks = page_info.get("para_blocks")
        if not para_blocks:
            continue

        page_size = page_info.get("page_size", [0, 0])
        page_height = float(page_size[1]) if page_size else 0.0
        if page_height <= 0:
            continue

        try:
            pdf_page = reader.pages[page_idx]
        except IndexError:
            continue

        thin_lines = _parse_thin_horizontal_lines(pdf_page)
        if not thin_lines:
            continue

        logger.debug(
            "Page %d: found %d thin lines, tagging spans", page_idx, len(thin_lines)
        )
        _tag_strikethrough_in_para_blocks(para_blocks, thin_lines, page_height)
