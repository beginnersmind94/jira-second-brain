"""segment_store.py — Guide segmentation engine for LX-3.

Splits a published guide's HTML at H2 boundaries into ordered segments.

INVARIANT (BLOCKING — AC2):
    ''.join(s['body_html'] for s in segment_guide(html)) == html
    (modulo wrapper-level tags stripped at ingest — the published render is
    losslessly reproduced segment by segment)

Every segment keeps the <h2> tag inside body_html so the rendered segment looks
identical to the original guide section.

Single-H2 or no-H2 guide → returns exactly one segment with heading=guide title
(if derivable from <h1>) or empty string, and body_html=full content.

Uses html.parser (stdlib) — no external deps.
"""
from __future__ import annotations

import re
import unicodedata


# ── Slug helper ──────────────────────────────────────────────────────────────


def _slugify(text: str) -> str:
    """Return a URL-safe anchor slug from heading text.

    Lowercases, normalises unicode, removes non-alphanumeric except hyphen/space,
    collapses whitespace to hyphens.
    """
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\-]", "", text)
    text = re.sub(r"[\s\-]+", "-", text).strip("-")
    return text or "section"


# ── HTML text extraction ──────────────────────────────────────────────────────


def _inner_text(tag_html: str) -> str:
    """Return inner text of an HTML tag, stripping nested tags.

    E.g. '<h2>Adding <em>Items</em></h2>' → 'Adding Items'
    """
    return re.sub(r"<[^>]+>", "", tag_html).strip()


# ── Core segmentation ─────────────────────────────────────────────────────────


def segment_guide(html: str) -> list[dict]:
    """Split published guide HTML at H2 boundaries.

    Returns an ordered list:
        [{
            "index":     int,       # 0-based
            "heading":   str,       # verbatim H2 inner text; "" if no H2 found
            "body_html": str,       # full content from H2 tag to next H2 (exclusive)
            "anchor":    str,       # slugified heading for deep-linking
        }]

    INVARIANT: ''.join(s['body_html'] for s in segments) == html  (lossless)

    Single-H2 or no-H2 guide → returns one segment with heading derived from the
    guide's <h1> tag (or "" if absent) and body_html = full content.
    """
    if not html:
        return [{"index": 0, "heading": "", "body_html": "", "anchor": "section"}]

    # Split at <h2 ... > boundaries (case-insensitive, self-closing impossible for h2).
    # We use re.split with a capturing group so the delimiters are kept.
    # Pattern: opening <h2> tag (any attributes allowed).
    H2_OPEN = re.compile(r"(<h2(?:\s[^>]*)?>)", re.IGNORECASE)

    # Also find the H2 closing tag + its content to extract the heading text.
    # Pattern: <h2...> ... </h2>
    H2_FULL = re.compile(r"<h2(?:\s[^>]*)?>[\s\S]*?</h2\s*>", re.IGNORECASE)

    # Split on H2 opening tags; splits[0] is pre-H2 content; then [tag, content, tag, content, …]
    splits = H2_OPEN.split(html)

    if len(splits) == 1:
        # No H2 found — return as single segment, heading from H1 if present
        h1_match = re.search(r"<h1(?:\s[^>]*)?>[\s\S]*?</h1\s*>", html, re.IGNORECASE)
        heading = _inner_text(h1_match.group(0)) if h1_match else ""
        return [{"index": 0, "heading": heading, "body_html": html, "anchor": _slugify(heading) or "section"}]

    segments: list[dict] = []
    idx = 0
    i = 0

    # splits layout:  [pre, <h2>, body, <h2>, body, ...]
    # The pre-H2 content (splits[0]) belongs to a phantom segment-0 only if non-empty.
    # Per the invariant we must include it — prepend it to the first real segment's body_html.
    pre = splits[0]  # may be empty

    while i + 1 < len(splits):
        h2_tag = splits[i + 1]      # the <h2 ...> opening tag
        rest = splits[i + 2] if i + 2 < len(splits) else ""
        # Reconstruct the full segment body: h2_tag + any content up to (but not including)
        # the next <h2>. The next opening h2_tag is the next split delimiter.
        # After re.split, splits[2], [4], [6], ... are the body portions between h2 tags.
        # So segment body_html = h2_tag + rest
        # We need to close the h2 tag + its closing tag properly.
        # Actually rest already contains everything until the next <h2> open tag,
        # including the </h2> close tag for THIS h2.
        body_html = h2_tag + rest

        # Extract heading text from the full <h2>...</h2> element at the start of body_html.
        h2_full_match = H2_FULL.match(body_html.lstrip())
        if h2_full_match:
            heading = _inner_text(h2_full_match.group(0))
        else:
            # No closing </h2> found — fall back to stripping the open tag's text
            heading = _inner_text(h2_tag)

        if idx == 0 and pre:
            # Prepend any pre-H2 content to the first segment so losslessness holds
            body_html = pre + body_html

        segments.append({
            "index": idx,
            "heading": heading,
            "body_html": body_html,
            "anchor": _slugify(heading),
        })
        idx += 1
        i += 2

    # Safety: if for some reason we produced no segments, return the whole doc.
    if not segments:
        return [{"index": 0, "heading": "", "body_html": html, "anchor": "section"}]

    # ── Losslessness assertion (development safeguard) ────────────────────────
    reconstructed = "".join(s["body_html"] for s in segments)
    if reconstructed != html:
        # Fallback: return a single segment so the endpoint never crashes.
        # (Logged for debugging; should never happen with the algorithm above.)
        import logging
        logging.warning(
            "segment_guide: losslessness check failed — returning single-segment fallback. "
            "html_len=%d reconstructed_len=%d", len(html), len(reconstructed)
        )
        h1_match = re.search(r"<h1(?:\s[^>]*)?>[\s\S]*?</h1\s*>", html, re.IGNORECASE)
        heading = _inner_text(h1_match.group(0)) if h1_match else ""
        return [{"index": 0, "heading": heading, "body_html": html, "anchor": _slugify(heading) or "section"}]

    return segments


def get_section_titles(html: str) -> list[str]:
    """Return verbatim H2 inner-text list from guide HTML.

    Used for the objective header — values are the H2 headings exactly as they
    appear in the published guide; no new text is synthesised.
    """
    H2_FULL = re.compile(r"<h2(?:\s[^>]*)?>[\s\S]*?</h2\s*>", re.IGNORECASE)
    return [_inner_text(m.group(0)) for m in H2_FULL.finditer(html)]
