"""Cleanup pipeline for Cybersoft guide PDF text extraction.

Pure functions, no I/O. The extractor passes raw per-page text in and gets
a structured markdown body + extracted document metadata back.

Pipeline order matters: boilerplate stripping happens per-page so cross-page
boundaries are preserved, then text-level cleanup is applied to the joined
document, then heading/list structure is recovered.
"""

import hashlib
import re
from typing import Dict, List, Tuple

# Cybersoft Quick Guides emit bullets as U+F0B7 (Symbol-font private-use
# codepoint that pypdf surfaces raw). Quick Cards use U+2022. Add others as
# the corpus expands; unknown glyphs trigger an extraction warning.
BULLET_GLYPHS = ("", "•", "▪", "●")
BULLET_GLYPH_RE = re.compile("(?:" + "|".join(re.escape(g) for g in BULLET_GLYPHS) + r")\s*")

FOOTER_LABELS = (
    "Category",
    "Document Type",
    "Author",
    "Software Version",
    "Updated",
)
FOOTER_LABEL_PATTERN = re.compile(
    r"\s*(" + "|".join(re.escape(label) for label in FOOTER_LABELS) + r")\s*:\s*",
    re.IGNORECASE,
)

BOILERPLATE_PATTERNS = [
    re.compile(r"^PROPRIETARY AND CONFIDENTIAL.*$", re.IGNORECASE),
    re.compile(r"^©\s*Cybersoft.*$", re.IGNORECASE),
    re.compile(r"^Page\s+\d+\s+of\s+\d+\s*$", re.IGNORECASE),
]

STEP_RE = re.compile(r"^\d+\.\s+\S")
SUB_STEP_RE = re.compile(r"^[a-z]\.\s+\S")
BULLET_RE = re.compile(r"^- ")
SUB_BULLET_RE = re.compile(r"^  - ")
HEADING_RE = re.compile(r"^#{1,6}\s")
SENTENCE_END_RE = re.compile(r"[.!?:](?:[\"')\]]+)?\s*$")

# Narrow wrap-tail signals. Articles and prepositions are excluded because
# step content commonly ends with "...the <noun>" or "...to <verb>", which
# would otherwise swallow the next observation or step.
#   - Conjunction (and/or/but/nor) at end of line, optionally followed by
#     one more word. This catches both "...BALANCED AND" and "...and Payment".
#   - Modal verb (will/may/can/...) followed by another word.
#   - Trailing comma or semicolon.
_MID_PHRASE_TAIL_RE = re.compile(
    r"(?:[,;]"
    r"|\b(?:and|or|but|nor)(?:\s+\S+)?"
    r"|\b(?:will|may|can|must|shall|should|could|would)\s+\S+"
    r")\s*$",
    re.IGNORECASE,
)

# Hard wrap-column heuristic: PDF source columns wrap around 75-80 chars, so
# any prev line at this length without a sentence end is overwhelmingly a wrap.
_WRAP_COLUMN_MIN = 70

# Lines starting with one of these are intro phrases, not section headings.
HEADING_BLOCKLIST_STARTS = {
    "with", "on", "in", "at", "by", "from", "after", "before", "when",
    "while", "since", "during", "between", "once", "if", "to",
}

SHORT_CONNECTORS = {
    "a", "an", "the", "of", "for", "to", "and", "or", "in", "on", "at", "by",
    "with", "as",
}


def text_hash(text: str) -> str:
    """Stable short hash of meaningful content.

    Whitespace is normalized so trivial reformatting does not register as drift.
    16 hex chars is enough to make accidental collisions implausible across
    the ~100 guides in this corpus.
    """
    normalized = re.sub(r"\s+", " ", text).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def clean(pages: List[str], frontmatter_title: str = "") -> Tuple[str, Dict]:
    """Clean per-page raw text into a structured markdown body.

    Returns (markdown_body, metadata) where metadata may contain:
      - software_version, source_updated, document_type, author (from footer)
      - extraction_warnings: list of warning codes
    """
    pages = [_strip_known_boilerplate(p) for p in pages]
    pages = [_strip_page_number_lines(p) for p in pages]

    text = "\n\n".join(p.strip() for p in pages if p.strip())
    text, doc_meta = _extract_doc_footer(text)

    text = _normalize_bullets(text)
    text = _dehyphenate_wraps(text)
    text = _drop_redundant_title(text, frontmatter_title)
    text = _promote_headings(text)
    text = _reflow_lines(text)
    text = _nest_step_observations(text)
    text = _collapse_blank_runs(text)

    warnings = _detect_warnings(text)
    return text.strip() + "\n", {**doc_meta, "extraction_warnings": warnings}


def _strip_known_boilerplate(page: str) -> str:
    out = []
    for line in page.split("\n"):
        if any(pat.match(line.strip()) for pat in BOILERPLATE_PATTERNS):
            continue
        out.append(line)
    return "\n".join(out)


def _strip_page_number_lines(page: str) -> str:
    out = []
    for line in page.split("\n"):
        s = line.strip()
        if re.fullmatch(r"\d+", s):
            continue
        if re.fullmatch(r"Page\s+\d+\s+of\s+\d+", s, re.IGNORECASE):
            continue
        out.append(line)
    return "\n".join(out)


def _extract_doc_footer(text: str) -> Tuple[str, Dict]:
    """Find and remove a Category/Document Type/Author/... block.

    Cybersoft Quick Cards put the footer at the end of page 1 rather than
    the document end, so a bottom-up scan misses it. Instead we find a
    cluster of >= 3 footer-label lines within a 3-line window of each other
    (label, value, label, value, ... is the typical shape) and excise that
    span. Footers can sit in the middle of the document.
    """
    lines = text.split("\n")
    label_re = re.compile(r"^(" + "|".join(FOOTER_LABELS) + r")\s*:", re.IGNORECASE)

    label_indices = [i for i, line in enumerate(lines) if label_re.match(line.strip())]
    if len(label_indices) < 3:
        return text, {}

    # Group label indices into clusters where consecutive labels are no more
    # than 3 lines apart (allows one value line between labels).
    clusters: List[List[int]] = []
    current: List[int] = [label_indices[0]]
    for idx in label_indices[1:]:
        if idx - current[-1] <= 3:
            current.append(idx)
        else:
            if len(current) >= 3:
                clusters.append(current)
            current = [idx]
    if len(current) >= 3:
        clusters.append(current)

    if not clusters:
        return text, {}

    best = max(clusters, key=len)
    start = best[0]
    end = min(best[-1] + 2, len(lines) - 1)
    footer_block = "\n".join(lines[start:end + 1])
    body = "\n".join(lines[:start] + lines[end + 1:]).strip()
    return body, _parse_footer_block(footer_block)


def _parse_footer_block(block: str) -> Dict:
    """Parse footer where labels may have inline or next-line values."""
    marked = FOOTER_LABEL_PATTERN.sub(
        lambda m: f"\x1e{m.group(1).strip()}\x1f", block
    )
    out: Dict[str, str] = {}
    for chunk in marked.split("\x1e"):
        if "\x1f" not in chunk:
            continue
        label, _, value = chunk.partition("\x1f")
        value = " ".join(line.strip() for line in value.splitlines() if line.strip())
        if not value:
            continue
        key = label.strip().lower().replace(" ", "_")
        if key == "updated":
            key = "source_updated"
        out[key] = value
    return out


def _normalize_bullets(text: str) -> str:
    text = BULLET_GLYPH_RE.sub("- ", text)
    text = re.sub(r"^o\s+([A-Z])", r"  - \1", text, flags=re.MULTILINE)
    return text


def _dehyphenate_wraps(text: str) -> str:
    """Join 'word-\\nword' into 'word-word'.

    The hyphen is preserved because in this corpus the documented compounds
    (over-claiming, re-enroll, sign-off) are real hyphenated words rather than
    typesetter line-wraps of single words.
    """
    return re.sub(r"(\w)-\n(\w)", r"\1-\2", text)


def _drop_redundant_title(text: str, frontmatter_title: str) -> str:
    """If the first content line restates the doc title, drop it."""
    if not frontmatter_title:
        return text
    lines = text.split("\n")
    for i, line in enumerate(lines):
        s = line.strip()
        if not s:
            continue
        if _titles_match(s, frontmatter_title):
            return "\n".join(lines[i + 1:]).lstrip("\n")
        return text
    return text


def _titles_match(line: str, title: str) -> bool:
    """Treat a line as redundant title only when its words are a subset of
    the frontmatter title (modulo "quick/guide/card" filler).

    Single-word titles like "Reconciliation" need this — strict overlap-only
    rules either reject them or trigger on any sentence that happens to use
    the title word.
    """
    def norm(s):
        return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()
    line_words = set(norm(line).split())
    title_words = set(norm(title).split())
    for ignored in ("quick", "guide", "card"):
        title_words.discard(ignored)
        line_words.discard(ignored)
    if not title_words or not line_words:
        return False
    return line_words.issubset(title_words) and bool(line_words & title_words)


def _promote_headings(text: str) -> str:
    """Promote heading-candidate lines to '## '.

    Promotion fires when:
      - The line passes _is_heading_candidate (short, Title Case, no trailing
        sentence punctuation, doesn't start with a preposition).
      - A step/bullet/heading appears within a few lines after it (modulo
        intro prose, handled by _next_is_structural).
      - The previous content line "terminates": ends with sentence
        punctuation, is itself a heading, is a step/bullet, or is short
        prose (< wrap column). Long unterminated prose is almost always a
        visual wrap whose continuation must not be mistaken for a heading.
      - The previous content line does NOT end with a conjunction (and/or/
        but/nor). Trailing conjunctions are the strongest wrap signal we
        have, and the next line is almost always a wrap continuation rather
        than a section heading.
    A blank line is inserted before each promoted heading.
    """
    lines = text.split("\n")
    out: List[str] = []
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or HEADING_RE.match(s) or _is_list_or_step(line):
            out.append(line)
            continue
        prev_nonblank = _last_nonblank(out)
        prev_blank_sep = not out or not out[-1].strip()
        prev_left = prev_nonblank.lstrip() if prev_nonblank else ""
        prev_is_structural = bool(prev_left and _is_list_or_step(prev_nonblank))
        prev_terminates = bool(
            prev_nonblank
            and (
                SENTENCE_END_RE.search(prev_nonblank)
                or HEADING_RE.match(prev_left)
                or prev_is_structural
                or len(prev_nonblank.rstrip()) < _WRAP_COLUMN_MIN
            )
        )
        if not (prev_blank_sep or prev_terminates):
            out.append(line)
            continue
        if prev_nonblank and _CONJUNCTION_TAIL_RE.search(prev_nonblank):
            out.append(line)
            continue
        if _is_heading_candidate(s) and _next_is_structural(lines, i + 1):
            if out and out[-1].strip():
                out.append("")
            out.append(f"## {s}")
            continue
        out.append(line)
    return "\n".join(out)


_CONJUNCTION_TAIL_RE = re.compile(r"\b(?:and|or|but|nor)\s*$", re.IGNORECASE)


def _last_nonblank(lines: List[str]) -> str:
    for line in reversed(lines):
        if line.strip():
            return line
    return ""


def _is_list_or_step(line: str) -> bool:
    stripped_left = line.lstrip()
    return bool(
        STEP_RE.match(stripped_left)
        or BULLET_RE.match(stripped_left)
        or SUB_BULLET_RE.match(line)
        or SUB_STEP_RE.match(stripped_left)
    )


def _is_heading_candidate(line: str) -> bool:
    if len(line) > 80:
        return False
    if SENTENCE_END_RE.search(line):
        return False
    if line.endswith(","):
        return False
    words = line.split()
    # 2-word minimum filters out single-token wrap fragments like
    # "Date/Time/Balance" that happen to look heading-shaped.
    if not (2 <= len(words) <= 10):
        return False
    if words[0].lower() in HEADING_BLOCKLIST_STARTS:
        return False
    cap = 0
    countable = 0
    for w in words:
        if not w[0].isalpha():
            cap += 1
            countable += 1
            continue
        countable += 1
        if w[0].isupper() or w.lower() in SHORT_CONNECTORS:
            cap += 1
    if countable == 0:
        return False
    return cap / countable >= 0.7


def _next_is_structural(lines: List[str], start: int) -> bool:
    """True if a step/bullet/heading appears within ~8 lines.

    Up to 3 intermediate non-structural lines (intro/observation prose) are
    skipped over. Cybersoft sections come in three intro styles:
      - No intro: heading immediately followed by step
      - Phrase intro: "With the transaction selected and the X open"
      - Sentence intro: "The user may force close an OPENED Session."
    We accept all three by allowing prose with or without trailing punctuation.
    False-positive risk is bounded by the heading-candidate filter itself,
    which requires Title Case + short + no trailing punctuation on the
    heading line.
    """
    intros_allowed = 3
    for j in range(start, min(start + 8, len(lines))):
        s = lines[j].strip()
        if not s:
            continue
        if _is_list_or_step(lines[j]):
            return True
        if _is_heading_candidate(s):
            return True
        if intros_allowed > 0:
            intros_allowed -= 1
            continue
        return False
    return False


def _reflow_lines(text: str) -> str:
    """Join lines split by visual line wrap; keep observation lines separate.

    Joining rules, in order:
      1. Skip if the current line starts a structural element (heading,
         bullet, step) or the previous line is a heading.
      2. Skip if the previous line ends with sentence-ending punctuation.
      3. Join if the current line starts with a lowercase letter (real
         English sentences rarely start lowercase; strong wrap signal).
      4. Join if the previous line ends with a mid-phrase token (conjunction,
         article, preposition, modal verb, comma) — catches wraps with
         capital-start continuations like "and Change\\nReturned".
      5. Otherwise, new line. Observations after a step stay separate so
         _nest_step_observations can indent them as continuations.
    """
    lines = text.split("\n")
    out: List[str] = []
    for line in lines:
        s = line.rstrip()
        if not s:
            if out and out[-1] != "":
                out.append("")
            continue
        if not out or not out[-1].strip():
            out.append(s)
            continue
        prev = out[-1]
        s_left = s.lstrip()
        if HEADING_RE.match(s_left) or _is_list_or_step(s):
            out.append(s)
            continue
        if HEADING_RE.match(prev.lstrip()):
            out.append(s)
            continue
        if SENTENCE_END_RE.search(prev):
            out.append(s)
            continue
        if _is_wrap_continuation(prev, s_left):
            out[-1] = f"{prev.rstrip()} {s_left}"
        else:
            out.append(s)
    return "\n".join(out)


def _is_wrap_continuation(prev: str, curr_lstripped: str) -> bool:
    """Decide whether curr should be merged onto prev.

    Three independent join signals:
      - curr begins with a lowercase letter (real English almost never does
        outside of mid-sentence wrap continuation).
      - prev ends with a narrow set of mid-phrase tokens (comma, semicolon,
        conjunction-plus-word, or modal-verb-plus-word).
      - prev is a prose line (not a numbered step or bullet) at or past the
        PDF wrap column (~70 chars). Length on a structural line usually
        reflects multi-clause content, not visual wrap; applying the length
        signal there would swallow legitimate observation lines that follow.
    """
    if curr_lstripped and curr_lstripped[0].islower():
        return True
    if _MID_PHRASE_TAIL_RE.search(prev):
        return True
    # Length-based wrap signal applies to prose AND bullets (both wrap
    # visually in the PDF). Numbered steps are exempt because steps that
    # legitimately span multiple clauses can exceed the wrap column.
    prev_left = prev.lstrip()
    is_prev_step = bool(STEP_RE.match(prev_left) or SUB_STEP_RE.match(prev_left))
    if not is_prev_step and len(prev.rstrip()) >= _WRAP_COLUMN_MIN:
        return True
    return False


def _nest_step_observations(text: str) -> str:
    """Indent unstructured prose lines that follow a numbered step.

    In Cybersoft guides, a step is often followed by an observation
    ('The Summary Sale page displays.') that belongs to the step. Indenting
    it 3 spaces makes markdown renderers treat it as a continuation of the
    list item rather than a list-breaking paragraph.
    """
    lines = text.split("\n")
    out: List[str] = []
    in_step = False
    step_indent = ""
    for line in lines:
        s = line.rstrip()
        stripped_left = s.lstrip()
        if not s:
            out.append("")
            in_step = False
            continue
        if HEADING_RE.match(s):
            in_step = False
            out.append(s)
            continue
        m = re.match(r"^(\s*)(\d+)\.\s", s)
        if m:
            in_step = True
            step_indent = m.group(1) + "   "
            out.append(s)
            continue
        if BULLET_RE.match(stripped_left) or SUB_BULLET_RE.match(s):
            in_step = False
            out.append(s)
            continue
        if in_step:
            out.append(step_indent + stripped_left)
            continue
        out.append(s)
    return "\n".join(out)


def _collapse_blank_runs(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text)


def _detect_warnings(text: str) -> List[str]:
    warnings: List[str] = []
    stripped = re.sub(r"\s+", " ", text).strip()
    if not stripped:
        warnings.append("no_extractable_text")
        return warnings
    if len(stripped) < 200:
        warnings.append("very_little_text")
    if any(g in text for g in BULLET_GLYPHS):
        warnings.append("unhandled_pdf_bullets")
    if "�" in text:
        warnings.append("replacement_chars_present")
    consecutive = 0
    for line in text.split("\n"):
        if re.match(r"^This (button|feature|icon|option)", line.strip()):
            consecutive += 1
            if consecutive >= 3:
                warnings.append("possible_multi_column_layout")
                break
        elif line.strip():
            consecutive = 0
    return warnings
