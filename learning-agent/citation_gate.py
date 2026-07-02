"""Unified grounding gate for both versions.

Layer 1 (ALWAYS): the deterministic substring check (demo.validate_citations) — the existing
hard floor. Its dict is returned UNCHANGED under result["substring"], so every caller that binds
`integ = run_gate(...)["substring"]` keeps working byte-for-byte.

Layer 2 (when gate_mode() in {citations, both}): a COVERAGE check — every claim-bearing <p>/<li>
block before the Sources section must carry a <!-- Source: ... --> citation. An uncited claim
block = overreach, the one failure Layer 1 ignores (Layer 1 only validates the citations that are
present). Deterministic; needs no API key.

PASS = substring clean AND (coverage layer off OR coverage clean).
"""
from __future__ import annotations
import re

import demo
from config import gate_mode

_SRC_RE = re.compile(r"<!--\s*Source:", re.I)
_BLOCK_RE = re.compile(r"<(p|li)\b[^>]*>(.*?)</\1>", re.I | re.S)
_TAG_RE = re.compile(r"<[^>]+>")
_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
_SOURCES_SPLIT_RE = re.compile(r"<h2[^>]*>\s*Sources\s*</h2>", re.I)


def _uncited_claim_blocks(html: str) -> tuple[int, int]:
    """(total_claim_blocks, uncited_claim_blocks) among <p>/<li> before Sources."""
    head = _SOURCES_SPLIT_RE.split(html, maxsplit=1)[0]
    total = uncited = 0
    for m in _BLOCK_RE.finditer(head):
        inner = m.group(2)
        visible = _TAG_RE.sub("", _COMMENT_RE.sub("", inner)).strip()
        if not visible:
            continue
        total += 1
        if not _SRC_RE.search(inner):
            uncited += 1
    return total, uncited


def run_gate(html: str, module: str = "", *, transcript_text: str = "") -> dict:
    sub = demo.validate_citations(html, transcript_text=transcript_text)
    invalid = html.count("INVALID_CITE_ID")
    substring_clean = (sub["tier_lie"] == 0 and sub["quote_not_found"] == 0 and invalid == 0)
    result = {
        "passed": substring_clean,
        "mode": gate_mode(),
        "substring": sub,
        "citations": None,
        "violations": [],
    }
    if not substring_clean:
        result["violations"].append(
            f"substring tier_lie={sub['tier_lie']} "
            f"quote_not_found={sub['quote_not_found']} invalid_cite_id={invalid}"
        )
    if gate_mode() in {"citations", "both"}:
        total, uncited = _uncited_claim_blocks(html)
        result["citations"] = {"claims": total, "uncited_claims": uncited,
                               "nonverbatim": sub["quote_not_found"]}
        citations_clean = (uncited == 0 and sub["quote_not_found"] == 0)
        result["passed"] = substring_clean and citations_clean
        if uncited:
            result["violations"].append(f"citations uncited_claims={uncited}")
    return result
