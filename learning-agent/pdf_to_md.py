"""Quick PDF -> Markdown conversion for the producer's upload step.

Goal: Word-export-fast (<30s) conversion of an uploaded PDF into clean markdown that the
generation pipeline can consume, while being wary of the common PDF extraction pitfalls.

We REUSE the repo's proven cleanup pipeline (jira-brain/scripts/guide_text_cleanup.py),
which already handles:
  - header/footer + page-number + boilerplate stripping
  - the Symbol-font bullet glyph (U+F0B7) that pypdf surfaces raw, plus other bullets
  - de-hyphenation of column wraps and line reflow (wrap-column heuristic)
  - heading + numbered/lettered step recovery
  - a multi-column-layout WARNING (the orphaned-icon / two-column failure mode)

On top of that, this module adds the things a *live upload* path needs and the guide
batch pipeline didn't:
  - scanned / image-only PDF detection (no embedded text) -> clear, actionable error
    (we do NOT silently emit an empty doc; OCR is out of scope for the <30s budget)
  - password-protected PDF detection
  - a page cap + soft wall-clock guard so a 400-page upload can't blow the budget

Pure pypdf + the shared cleaner. No network, no SDK.
"""
import io
import sys
import time
from pathlib import Path

# Reuse the battle-tested cleaner that produced the 86 guide extractions.
_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from guide_text_cleanup import clean as _clean  # noqa: E402

from pypdf import PdfReader  # noqa: E402

MAX_PAGES = 80           # budget guard; real guides are far smaller
TIME_BUDGET_S = 25.0     # soft stop, leaves headroom under the 30s ceiling
MIN_CHARS_PER_PAGE = 12  # below this average => almost certainly scanned images


class PdfConversionError(Exception):
    """Expected, user-facing conversion failure (bad/scanned/encrypted PDF)."""


# Common pypdf text pitfalls: ligature glyphs come out as single codepoints, soft hyphens
# and non-breaking spaces sneak in from justified text. Fix them before cleanup so the
# heading/step heuristics (and the eventual reader) see normal characters.
_LIGATURES = {"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl"}


def _normalize(s: str) -> str:
    for k, v in _LIGATURES.items():
        s = s.replace(k, v)
    s = s.replace("­", "")    # soft hyphen (invisible line-break hint)
    s = s.replace(" ", " ")   # non-breaking space
    s = s.replace("﻿", "")    # stray BOM
    return s


def convert(data: bytes, title: str = "", max_pages: int = MAX_PAGES) -> dict:
    """Convert PDF bytes to markdown.

    Returns {markdown, warnings[], pages, pages_used, truncated, elapsed_s, doc_meta}.
    Raises PdfConversionError with a human-readable message on unreadable / scanned /
    encrypted PDFs so the caller can surface it instead of producing junk.
    """
    t0 = time.monotonic()
    try:
        reader = PdfReader(io.BytesIO(data))
    except Exception as e:
        raise PdfConversionError(f"Could not open this PDF ({e}). Is the file complete?")

    if getattr(reader, "is_encrypted", False):
        try:
            reader.decrypt("")  # many "encrypted" PDFs just have an empty owner password
        except Exception:
            raise PdfConversionError(
                "This PDF is password-protected. Remove the password and re-upload, "
                "or paste the text as .md/.txt.")

    n_pages = len(reader.pages)
    if n_pages == 0:
        raise PdfConversionError("This PDF has no pages.")

    truncated = n_pages > max_pages
    pages_txt = []
    for page in reader.pages[:max_pages]:
        try:
            pages_txt.append(_normalize(page.extract_text() or ""))
        except Exception:
            pages_txt.append("")  # one bad page shouldn't abort the whole doc
        if time.monotonic() - t0 > TIME_BUDGET_S:
            truncated = True
            break

    used = len(pages_txt)
    total_chars = sum(len(p.strip()) for p in pages_txt)
    if total_chars < MIN_CHARS_PER_PAGE * max(used, 1):
        # No meaningful selectable text -> scanned/image PDF. Fail loudly; do not emit
        # an empty "successful" markdown (that would silently produce an empty guide).
        raise PdfConversionError(
            "This PDF appears to be scanned images (no selectable text), so a quick "
            "conversion can't read it. Upload a text-based PDF or a Word/PDF export, "
            "or paste the transcript as .md/.txt.")

    markdown, meta = _clean(pages_txt, frontmatter_title=title)
    warnings = list(meta.get("extraction_warnings") or [])
    if truncated:
        warnings.append(f"truncated_to_{used}_of_{n_pages}_pages")

    return {
        "markdown": markdown,
        "warnings": warnings,
        "pages": n_pages,
        "pages_used": used,
        "truncated": truncated,
        "elapsed_s": round(time.monotonic() - t0, 2),
        "doc_meta": {k: v for k, v in meta.items() if k != "extraction_warnings"},
    }


if __name__ == "__main__":  # tiny manual smoke test: python pdf_to_md.py some.pdf
    import json
    if len(sys.argv) < 2:
        print("usage: python pdf_to_md.py <file.pdf>")
        raise SystemExit(2)
    blob = Path(sys.argv[1]).read_bytes()
    try:
        out = convert(blob, title=Path(sys.argv[1]).stem)
        print(json.dumps({k: v for k, v in out.items() if k != "markdown"}, indent=2))
        print("\n----- markdown (first 1200 chars) -----\n" + out["markdown"][:1200])
    except PdfConversionError as e:
        print("PdfConversionError:", e)
