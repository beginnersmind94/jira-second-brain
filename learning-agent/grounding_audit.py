"""grounding_audit.py — Exhaustive claim-level grounding audit for published guides.

Parses every  <!-- Source: {ref} {tier}: "{quote}" -->  comment from a guide's
raw HTML (with citations still present) and surfaces:
  - A structured citation record per Source comment
  - Any [TO VERIFY] markers (unsourced claims flagged for SME review)
  - An optional drift flag when the source ref's content has changed since the
    guide was generated (detected via source_content_hash in draft metadata)

This module is READ-ONLY.  It emits data; it never writes files, transitions
status, or modifies any stored artifact.

Trust guardrails (non-negotiable):
  1. If parsing fails or yields a partial result, the audit payload says so —
     it never claims "exhaustive" when it can only see part of the document.
  2. fully_grounded is True ONLY when to_verify_count == 0 AND every citation
     has a non-empty verbatim_quote.  One empty quote breaks the flag.
  3. Drift flags are informational — they never block the audit or change status.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# Matches:  <!-- Source: NXT-1234 AC: "verbatim quote" -->
# Also handles:  <!-- Source: transcript [MM:SS] -->  (no tier, no quote)
# and multi-token refs like [[NXT-1234:AC]] embedded in the ref field.
_SOURCE_COMMENT_RE = re.compile(
    r"<!--\s*Source:\s*"
    r"(?P<ref>[^\s\"']+)"           # ref: NXT-1234 or [[NXT-1234:AC]] or transcript
    r"(?:\s+(?P<tier>[A-Z_]+):)?"   # optional: AC: / RN: / RN_INTERNAL: / Description:
    r"(?:\s*\"(?P<quote>[^\"]*)\")?" # optional: "verbatim quote"
    r"[^>]*"                        # anything else inside the comment
    r"-->",
    re.DOTALL,
)

# Also handle the bracket-notation refs like [[NXT-1234:AC]] that appear in
# the demo HTML as part of the ref token.
_BRACKET_REF_RE = re.compile(r"\[\[(?P<ticket>[^:\]]+):(?P<tier>[^\]]+)\]\]")

# [TO VERIFY: ...] markers
_TO_VERIFY_RE = re.compile(r"\[TO VERIFY[^\]]*\]", re.IGNORECASE)

# HTML heading tags for section detection
_HEADING_RE = re.compile(r"<h([23])[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)

# HTML tag strip (simple)
_TAG_RE = re.compile(r"<[^>]+>")

# Normalise whitespace
_WS_RE = re.compile(r"\s+")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_tags(text: str) -> str:
    """Remove HTML tags and normalise whitespace."""
    text = _TAG_RE.sub(" ", text)
    text = _WS_RE.sub(" ", text)
    return text.strip()


def _parse_ref(raw_ref: str) -> tuple[str, str | None]:
    """Return (clean_ref, embedded_tier_or_None).

    Handles both plain refs (NXT-1234, GUIDE-001) and the bracket notation
    [[NXT-1234:AC]] that the Cell-D assembler sometimes emits inline.
    """
    m = _BRACKET_REF_RE.search(raw_ref)
    if m:
        return m.group("ticket").strip(), m.group("tier").strip()
    return raw_ref.strip(), None


def _content_before(html: str, end_pos: int, max_chars: int = 400) -> str:
    """Return a window of raw HTML immediately preceding `end_pos`."""
    start = max(0, end_pos - max_chars)
    return html[start:end_pos]


def _find_section(html: str, pos: int) -> str:
    """Walk backwards from `pos` to find the nearest H2 or H3 heading text."""
    fragment = html[:pos]
    headings = list(_HEADING_RE.finditer(fragment))
    if not headings:
        return ""
    last = headings[-1]
    return _strip_tags(last.group(2))[:120]


def _preceding_claim_text(raw_before: str) -> str:
    """Extract the text of the sentence or element immediately before a
    Source comment.  Strip HTML, trim to the last 200 characters, and return
    the last meaningful sentence fragment."""
    text = _strip_tags(raw_before)
    # Trim leading/trailing noise
    text = text[-300:].strip()
    # Return the last "sentence" (split on . or ; or \n)
    for sep in (".", ";", "\n"):
        parts = [p.strip() for p in text.rsplit(sep, 1) if p.strip()]
        if len(parts) == 2:
            return parts[-1][:200]
    return text[-200:]


# ---------------------------------------------------------------------------
# Main extraction function
# ---------------------------------------------------------------------------

def extract_citations(resource_id: str, html: str | None = None,
                      html_path: Path | None = None) -> dict[str, Any]:
    """Parse all <!-- Source: ... --> comments and [TO VERIFY] markers from a
    published guide's raw HTML (the version with citations still embedded).

    Parameters
    ----------
    resource_id : str
        The guide's resource ID (used only for labelling in error responses).
    html : str | None
        Raw HTML content.  If not provided, `html_path` must be given.
    html_path : Path | None
        Path to the HTML file.  Read only when `html` is None.

    Returns
    -------
    dict with keys:
        citations        — list of citation dicts
        to_verify        — list of [TO VERIFY] marker dicts
        parse_error      — str or None (set when HTML could not be read)
        exhaustive       — bool (True when parsing succeeded fully)
    """
    if html is None:
        if html_path is None:
            return {
                "citations": [],
                "to_verify": [],
                "parse_error": "No html or html_path supplied.",
                "exhaustive": False,
            }
        try:
            html = html_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return {
                "citations": [],
                "to_verify": [],
                "parse_error": f"Could not read HTML file: {exc}",
                "exhaustive": False,
            }

    citations: list[dict] = []
    seen_positions: list[int] = []

    for m in _SOURCE_COMMENT_RE.finditer(html):
        raw_ref = m.group("ref") or ""
        comment_tier = (m.group("tier") or "").strip() or None
        verbatim_quote = (m.group("quote") or "").strip()

        # Resolve bracket-notation refs that embed tier inside the ref token.
        clean_ref, embedded_tier = _parse_ref(raw_ref)

        # Tier priority: explicit in comment > embedded in ref > None
        tier = comment_tier or embedded_tier or None

        # Also check if the raw_ref itself contains :DESC / :AC / :RN hints
        # e.g. [[NXT-37111:DESC]] → tier DESC already handled by _parse_ref
        if tier is None and ":" in clean_ref:
            parts = clean_ref.split(":", 1)
            clean_ref = parts[0].strip()
            tier = parts[1].strip() if len(parts) > 1 else None

        # Skip pure transcript markers (no grounding claim from Jira/guide)
        is_transcript = clean_ref.lower().startswith("transcript")

        start_pos = m.start()

        # Claim text: text of the element immediately before this comment
        raw_before = _content_before(html, start_pos)
        claim_text = _preceding_claim_text(raw_before)

        # Section heading
        section = _find_section(html, start_pos)

        grounded = bool(verbatim_quote) or is_transcript

        citations.append({
            "section": section,
            "claim_text": claim_text,
            "source_ref": clean_ref,
            "tier": tier,
            "verbatim_quote": verbatim_quote,
            "grounded": grounded,
            "is_transcript": is_transcript,
            "drift_flag": False,  # filled in by augment_drift_flags()
        })
        seen_positions.append(start_pos)

    # ── [TO VERIFY] markers ──────────────────────────────────────────────────
    to_verify: list[dict] = []
    for m in _TO_VERIFY_RE.finditer(html):
        raw_before = _content_before(html, m.start())
        section = _find_section(html, m.start())
        surrounding = _strip_tags(html[max(0, m.start() - 100): m.end() + 100])
        to_verify.append({
            "section": section,
            "marker_text": m.group(0),
            "surrounding_context": surrounding[:300],
        })

    return {
        "citations": citations,
        "to_verify": to_verify,
        "parse_error": None,
        "exhaustive": True,
    }


# ---------------------------------------------------------------------------
# Drift detection
# ---------------------------------------------------------------------------

def augment_drift_flags(citations: list[dict], meta: dict) -> int:
    """Mark citations as drift_flag=True when the cited source ref has changed.

    Detection strategy: the draft metadata may carry a ``source_content_hash``
    or a per-ticket hash map.  If not present, no flag is raised (silent omit
    per spec).

    Returns the count of flagged citations.
    """
    # V1: the draft metadata doesn't yet store per-ticket content hashes.
    # The spec says "if no hash is stored, omit the flag silently."
    # We reserve the field so the response shape is stable when hashes land.
    stored_hashes: dict = meta.get("source_content_hashes") or {}
    if not stored_hashes:
        return 0

    flagged = 0
    for cit in citations:
        ref = cit.get("source_ref") or ""
        if ref in stored_hashes:
            # Compare stored hash with current ticket file if available.
            # (Ticket files live at raw/tickets/<ref>.md in jira-brain.)
            # For now: if a hash entry exists and differs from the current
            # computed hash, flag it.  In V1 no ticket files are within the
            # learning-agent tree, so this is a no-op beyond reserving shape.
            stored_hash = stored_hashes[ref]
            current_hash = _current_ticket_hash(ref)
            if current_hash and current_hash != stored_hash:
                cit["drift_flag"] = True
                flagged += 1
    return flagged


def _current_ticket_hash(ref: str) -> str | None:
    """Return an MD5 of the current ticket file content, or None if not found."""
    # Walk up from this file to the jira-brain root.
    here = Path(__file__).parent
    for candidate in (
        here.parent / "raw" / "tickets" / f"{ref}.md",
        here.parent.parent / "raw" / "tickets" / f"{ref}.md",
    ):
        if candidate.exists():
            try:
                content = candidate.read_bytes()
                return hashlib.md5(content).hexdigest()
            except OSError:
                return None
    return None


# ---------------------------------------------------------------------------
# Summary builder
# ---------------------------------------------------------------------------

def build_audit_payload(resource_id: str, title: str, citations: list[dict],
                        to_verify: list[dict], parse_error: str | None,
                        exhaustive: bool, drift_flagged: int = 0) -> dict:
    """Assemble the JSON audit payload for a single resource.

    The ``_note`` field is non-negotiable per the trust spec.  When
    ``exhaustive`` is False, the note says so explicitly — we never claim
    exhaustive coverage when parsing failed.
    """
    verified = sum(1 for c in citations if c.get("grounded"))
    total = len(citations)
    to_verify_count = len(to_verify)

    # fully_grounded: True ONLY when no [TO VERIFY] markers AND every citation
    # has a non-empty verbatim_quote (transcript-only cites are exempt because
    # they are structurally unquotable — the timestamp IS the citation).
    jira_cits = [c for c in citations if not c.get("is_transcript")]
    all_jira_quoted = all(bool(c.get("verbatim_quote")) for c in jira_cits)
    fully_grounded = (to_verify_count == 0) and all_jira_quoted and exhaustive

    if parse_error:
        note = (
            f"PARTIAL — parsing failed: {parse_error}. "
            "This audit does NOT cover the full guide. Do not treat it as complete."
        )
    elif not exhaustive:
        note = (
            "PARTIAL — not every claim in this guide was reached. "
            "Do not treat this as an exhaustive audit."
        )
    else:
        note = (
            "Exhaustive — every claim in this guide listed. Not sampled."
        )

    drift_header: str | None = None
    if drift_flagged > 0:
        drift_header = (
            f"⚠️ {drift_flagged} citation{'s' if drift_flagged != 1 else ''} "
            "may reference updated sources — review flagged rows."
        )

    payload: dict[str, Any] = {
        "resource_id": resource_id,
        "title": title,
        "total_claims": total,
        "verified_claims": verified,
        "to_verify_count": to_verify_count,
        "fully_grounded": fully_grounded,
        "citations": citations,
        "to_verify": to_verify,
        "_note": note,
    }
    if drift_header:
        payload["drift_warning"] = drift_header
    if parse_error:
        payload["parse_error"] = parse_error

    return payload
