"""Version B ONLY — the Anthropic Citations API as the grounding authority.

Imported LAZILY (inside the writer branch) so Version A never needs the `anthropic` package or an
API key. The Citations API returns, for each generated span, a guaranteed-verbatim `cited_text`
from the source document it used — that structural guarantee is why Version B trusts it over
regex extraction.

Docs contract honored (verified against platform.claude.com + the claude-api reference):
  - document blocks use source.type='text' (field text as plain text).
  - citations.enabled=true per document; enabling is all-or-none per request.
  - each response text block carries a .citations list; each citation exposes .cited_text
    (verbatim) and .document_title (we set it to 'KEY:TIER').
  - incompatible with structured outputs -> we parse .citations ourselves.
  - works with prompt caching (cache_control) and the Batch API.
  - NO temperature/top_p: rejected with 400 on Opus 4.8/4.7/Fable 5, so CITATIONS_MODEL is free.
  - cache_control on the LAST document only: the API caps cache breakpoints at 4/request, and a
    well-sourced section can cite more than 4 (ticket, tier) documents.
"""
from __future__ import annotations
import os

import demo

CITATIONS_SECTION_SYSTEM_PROMPT = (
    "You are writing ONE section of a learning guide for the `{module}` module. You have "
    "NO tools. Write clean HTML: a single <h2> heading followed by <p> and <ul>/<li> "
    "content. Ground EVERY factual statement in the provided source documents — state "
    "nothing the sources do not support. Quote or closely paraphrase the sources so each "
    "claim can be attached to its source span. Do NOT write a Sources list (it is added "
    "automatically). Do NOT invent labels, values, menu paths, or error strings that are "
    "not present in the sources."
)

_TIER_ORDER = ["AC", "RN", "RNINT", "DESC"]


def _record(key: str) -> dict:
    return (demo._FIX.get("tickets", {}).get(key)
            or demo._FIX.get("epics", {}).get(key) or {})


def build_ticket_documents(ticket_keys: list[str]) -> list[dict]:
    """One Anthropic document block per (ticket, tier) with non-empty field text.
    Deterministic order: sorted ticket key, then tier rank (AC, RN, RNINT, DESC).
    Exactly ONE cache_control breakpoint (on the last doc) — the API caps breakpoints at 4."""
    docs: list[dict] = []
    for key in sorted(set(ticket_keys)):
        rec = _record(key)
        for tier in _TIER_ORDER:
            field = demo._FIELD_BY_TIER[tier]
            text = (rec.get(field) or "").strip()
            if not text:
                continue
            docs.append({
                "type": "document",
                "source": {"type": "text", "media_type": "text/plain", "data": text},
                "title": f"{key}:{tier}",
                "citations": {"enabled": True},
            })
    if docs:
        docs[-1]["cache_control"] = {"type": "ephemeral"}
    return docs


def parse_citation_response(content) -> dict:
    """Pure parser (unit-tested without a live call). `content` is the list of response content
    blocks (real SDK objects, or any objects exposing .type/.text/.citations)."""
    segments: list[dict] = []
    prose_parts: list[str] = []
    for block in content:
        if getattr(block, "type", None) != "text":
            continue
        text = getattr(block, "text", "") or ""
        prose_parts.append(text)
        cites = []
        for c in (getattr(block, "citations", None) or []):
            title = getattr(c, "document_title", "") or ""
            span = getattr(c, "cited_text", "") or ""
            if ":" in title and span:
                key, tier = title.rsplit(":", 1)
                cites.append({"span": span, "key": key, "tier": tier})
        segments.append({"text": text, "cites": cites})
    return {"segments": segments, "prose": "".join(prose_parts)}


def cite_id(key: str, tier: str, sid: str, n: int) -> str:
    """A registry id namespaced by the SECTION id `sid`, so two sections that cite the same
    (key, tier) never collide in the shared registry."""
    return f"{key}:{tier}:{sid}:C{n:03d}"


def segments_to_html(segments: list[dict], sid: str) -> tuple[str, dict]:
    """Pure: turn parsed citation segments into (html_fragment_with_[CITE:id], {cid: entry}).
    The span is stored RAW (never sanitized) so demo.validate_citations' `_norm(quote) in
    _norm(field)` substring check passes — sanitizing would change bytes on one side only."""
    parts: list[str] = []
    entries: dict[str, dict] = {}
    n = 0
    for seg in segments:
        parts.append(seg["text"])
        for c in seg["cites"]:
            cid = cite_id(c["key"], c["tier"], sid, n)
            n += 1
            entries[cid] = {"issue": c["key"], "tier": c["tier"], "span": c["span"]}
            parts.append(f"[CITE:{cid}]")
    return "".join(parts).strip(), entries


def write_section_citations(section: dict, docs: list[dict], module: str, directive: str = "") -> dict:
    """Raw Messages API call with citations enabled. Requires ANTHROPIC_API_KEY.
    No temperature/top_p (400 on Opus 4.8/4.7/Fable 5)."""
    from anthropic import Anthropic

    client = Anthropic()  # reads ANTHROPIC_API_KEY from the environment
    title = section.get("title", "Section")
    scope = section.get("scope", "")
    directive_line = (
        f"\nAUTHORING DIRECTIVE (tone/audience/emphasis ONLY — never invent facts): "
        f"{directive.strip()}\n" if directive and directive.strip() else ""
    )
    instruction = (
        f"Section: {title}\nScope: {scope}\n{directive_line}\n"
        f"Write the <h2>{title}</h2> section now, grounded ONLY in the documents above."
    )
    content = list(docs) + [{"type": "text", "text": instruction}]
    resp = client.messages.create(
        model=os.getenv("CITATIONS_MODEL", "claude-sonnet-4-6"),
        max_tokens=4096,
        system=CITATIONS_SECTION_SYSTEM_PROMPT.format(module=module),
        messages=[{"role": "user", "content": content}],
    )
    parsed = parse_citation_response(resp.content)
    usage = None
    u = getattr(resp, "usage", None)
    if u is not None:
        usage = {
            "input_tokens": getattr(u, "input_tokens", 0),
            "output_tokens": getattr(u, "output_tokens", 0),
            "cache_read_input_tokens": getattr(u, "cache_read_input_tokens", 0),
            "cache_creation_input_tokens": getattr(u, "cache_creation_input_tokens", 0),
        }
    return {"title": title, "segments": parsed["segments"], "prose": parsed["prose"], "usage": usage}
