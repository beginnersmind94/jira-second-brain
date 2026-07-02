# Citations-API Migration — Execution Runbook v2 (Windows)

**Audience:** the executor subagents that run on the Windows laptop.
**Rule:** every task is decision-free. Copy the code exactly, run the exact command, check
the exact pass/fail. **If any anchor precheck fails, or anything is ambiguous, STOP and
report — do not improvise, do not "find the closest match."**

**Shell:** Windows PowerShell. Python is `python` (if that fails, `py -3`). All commands run
from `learning-agent\` unless stated.

> **This v2 supersedes the earlier draft runbook.** §1.1 lists every change from that draft
> and why — each is a grounded correctness fix, not a preference. If you were handed the
> earlier draft, use THIS file instead.

---

## 0. What this migration does (read once, then execute)

We add Anthropic's **Citations API** to the pipeline that actually ships content (the
**Cell-D** pipeline: plan → registry of verbatim spans → parallel section writers →
deterministic `assemble` → grounding gate → human approval). We deliver **two versions from
one codebase**, selected by a `GATE_MODE` environment variable:

| | **Version A** (subscription / enterprise) | **Version B** (paid API) |
|---|---|---|
| `GATE_MODE` | `substring` (or unset) | `both` |
| `ANTHROPIC_API_KEY` | unset | set |
| Section writer | existing SDK writer (unchanged) | **Citations API** produces the grounded spans |
| Grounding gate | substring check only (today's behavior) | substring check **+** citation-coverage check |
| Runs on the user's machine today? | **Yes** (subscription OAuth) | No — needs a paid key |

**Why this is the right shape.** Version A's existing design is *grounding-by-construction*:
the section writer has no channel to type a quote or a tier — it emits only `[CITE:id]`, and a
deterministic assembler renders the verbatim span + tier from a registry built straight from
the Jira fixture. Wrong-tier and non-verbatim are therefore *impossible*. Version B keeps that
gate but swaps the writer for the **Citations API**, whose structural guarantee is that every
returned `cited_text` is a verbatim substring of the source document it cited. That buys two
things Version A can't get for free: (1) the model writes *natural prose* and the API attaches
the spans, and (2) a new **coverage** dimension — every claim block must carry a citation, which
catches *over-claiming* (a sentence with no source), the one failure the registry approach
ignores (it only validates the citations that are present).

Neither version is strictly "better." They guard different failure modes. Version A is the
strongest structural guarantee and the one the user runs today; Version B adds coverage + more
natural prose when a paid key is available.

**Two independent switches (this split is deliberate — see §1):**

- **`gate_mode()`** — a *policy*. When `citations`/`both`, the gate additionally enforces that
  every claim block carries a citation. **Deterministic; needs no key.**
- **`citations_enabled()`** — `gate_mode() ∈ {citations,both}` **AND** a key is present. Only
  this switches the *writer* to the Citations API. **Needs a key.**

Consequence: the whole gate + eval layer is testable **without a key**. Only live Version B
*generation* needs a key. On a machine with no key, everything in Waves 0–4 runs green except
the two clearly-marked live checks (they print `SKIP`).

---

## 1. Design refinements (why this is simple and correct)

Grounding the plan against the real code (`demo.py`, `demo_d.py`, `demo_app.py`) surfaced these
honest simplifications. They are already baked into the tasks below; this section explains them.

1. **`gate_mode()` vs `citations_enabled()` split.** The coverage gate is deterministic (no
   key); only the *writer* needs the API. Splitting them makes Version B's gate fully
   unit-testable offline and keeps keys scoped to generation. Changes no Version A behavior.
2. **`run_gate(html, module="")` — `module` is optional and unused by the gate.**
   `demo.validate_citations` reads the process-global fixture (`demo._FIX`, set by
   `_ensure_fixture`), and the coverage check reads only the HTML. No call site has to thread a
   `module` value it doesn't have.
3. **Enforcement is narrowed to the two live gates that already re-validate:**
   `publish_pending` and `approve_resource`. Every other `validate_citations` call becomes a
   pure rename (`integ = run_gate(...)["substring"]`) with **byte-identical** behavior. Two
   enforcement points, minimal blast radius.
4. **Version B stores the RAW `cited_text` span (never sanitized).** `demo.validate_citations`
   verifies a quote by `_norm(quote) in _norm(field)` — a substring test against the *whole*
   field, with the *same* `_norm` on both sides. A Citations `cited_text` is always a verbatim
   substring of the field document we send, so it passes unchanged. Sanitizing it (smart-quote
   or `-->` rewriting) would change the bytes on only one side and *break* the verbatim check —
   so we deliberately don't. This matches how the Jira registry already stores raw spans.
5. **Batch API is an optional appendix (§8), not a pass/fail gate.** It can't be verified
   without a key and isn't core to the two-version story. Prompt caching (the cheap, free win)
   is kept.

### 1.1 What changed from the earlier draft runbook (and why)

Each item below is a bug or drift the earlier draft would have hit on the *real* code. All are
fixed in this v2.

| # | Problem in the earlier draft | Fix in v2 | Why it matters |
|---|---|---|---|
| A | **Stale line numbers.** The draft cited `demo_app.py` lines 285/4803/4943/5216/5297/5469/5578/7418. The real file has drifted ~10–25 lines (actual: 295/4813/4953/5243/5318/5490/5600/7439). | Every Wave-2 edit is **anchor-based** with an **occurrence-count precheck** (§5.0). Line numbers are hints only. | A subagent sent to a wrong line sees different text and either edits the wrong place or stalls. Anchors + a count check make it deterministic: match exactly, or STOP. |
| B | **Cite-id collision across sections (Version B).** The draft's per-section counter reset to `0`, so two sections citing the same `KEY:TIER` both emitted `KEY:TIER:C000` and collided in the shared registry — last writer wins, one section silently renders the **wrong span**. The deterministic gate can't catch it (both spans are verbatim + correct tier). | Cite-ids are namespaced by the section id: `KEY:TIER:<sid>:Cnnn`. Reassembly is extracted to a pure `segments_to_html()` and **unit-tested keyless** (T1.2). | A wrong-span citation defeats Version B's whole grounding promise while passing every gate. |
| C | **`cache_control` on every document → 400.** The API allows **max 4 cache breakpoints per request**. A well-sourced long-form section cites 3–8 tickets × up to 4 tiers = far more than 4 documents; putting a breakpoint on each 400s the request, failing essentially every real Version B section. | Put **one** breakpoint on the last document only. | Without this, Version B generation fails on real content, not edge cases. |
| D | **`temperature=0.0` in the writer + smoke.** Valid on Sonnet 4.6, but **rejected with a 400 on Opus 4.8 / 4.7 / Fable 5** — which the draft explicitly allowed via `CITATIONS_MODEL`. | Remove `temperature` entirely. (Determinism isn't guaranteed by `temperature=0` anyway; grounding comes from the API, not sampling.) | Makes the `CITATIONS_MODEL` override actually safe, per current Anthropic model rules. |
| E | **Version B silently broke transcript-only guides.** The draft routed to the Citations writer whenever `citations_enabled()`, but built documents only from Jira `ticket_keys`. A transcript-only section (which carries `span_ids`, not `ticket_keys`) would get **zero documents** and lose all citations. | Route to the Citations writer **only when the section has `ticket_keys`**; transcript-only and structural sections fall through to the existing SDK writer (identical to Version A for those sections). | Keeps transcript-only mode working under Version B instead of silently degrading it. |
| F | **Model id guidance was misleading.** The draft implied you might need a "dated model id." | Bare ids are authoritative (`claude-sonnet-4-6`, `claude-opus-4-8`); **never** append a date suffix. `.env.example` says so. | A dated id 404s on the first-party API. |
| G | **Parity eval only tested synthetic drafts.** | Keep the synthetic parity test (T3.2) **and** add a keyless, fixture-free `coverage_report.py` (T3.3) that prints how the coverage layer would score **real** drafts. | Lets the team *see* whether coverage would false-positive on real content before Version B relies on it — informational, never a hard fail. |

---

## 2. Prerequisites & baseline

```powershell
# from learning-agent\
python --version                     # expect 3.10+  (if 'python' missing, use: py -3 --version)
python -m pip install -r requirements.txt
python -m pip install pytest         # if not already present
```

Confirm the code imports cleanly and record the baseline BEFORE changing anything:

```powershell
python -c "import demo, demo_d, demo_app; print('baseline import OK')"
python -m eval.regression            # RECORD the summary line — you compare against it after Wave 2
```

**PASS gate for §2:** `baseline import OK` prints, and `eval.regression` runs to completion.
Write down its summary line — it is your Wave-2 comparison baseline.

---

## 3. Wave 0 — config + dependency + live smoke (1 agent, sequential)

### T0.1 — Create `config.py`

Create `learning-agent\config.py` with **exactly**:

```python
"""Two-version switches. GATE_MODE selects the gate policy; a key selects the writer.

  GATE_MODE=substring (default) -> Version A: existing behavior, no key needed.
  GATE_MODE=both      + a key   -> Version B: Citations writer + coverage gate.
  GATE_MODE=citations           -> coverage gate ON but writer falls back to SDK
                                    unless a key is also present (gate-only strict mode).
"""
from __future__ import annotations
import os

_VALID = {"substring", "citations", "both"}


def gate_mode() -> str:
    m = os.getenv("GATE_MODE", "substring").strip().lower()
    return m if m in _VALID else "substring"


def citations_enabled() -> bool:
    """True iff the WRITER should call the Citations API (needs an API key)."""
    return gate_mode() in {"citations", "both"} and bool(os.getenv("ANTHROPIC_API_KEY"))
```

**PASS:**
```powershell
python -c "import config; assert config.gate_mode()=='substring'; assert config.citations_enabled() is False; print('T0.1 PASS')"
```
Expect `T0.1 PASS`, exit code 0 (with no `GATE_MODE` and no key set).

### T0.2 — Add the `anthropic` dependency + live smoke script

**Edit `requirements.txt`** — anchor precheck first:
```powershell
Select-String -Path requirements.txt -Pattern "^claude-agent-sdk>=0.2.0$" -SimpleMatch:$false
```
Expect exactly **one** match. If zero or more than one, STOP and report.

Then insert these two lines **immediately after** the `claude-agent-sdk>=0.2.0` line:
```
# Version B ONLY — raw Messages API for the Citations grounding writer.
anthropic>=0.40.0
```

Install and pin:
```powershell
python -m pip install "anthropic>=0.40.0"
python -c "import anthropic; print('anthropic', anthropic.__version__)"
```
If the printed version is higher than `0.40.0`, replace `0.40.0` in `requirements.txt` with the
printed version.

Create `learning-agent\scripts\smoke_citations.py` with **exactly**:

```python
"""Live smoke test for the Anthropic Citations API (Version B only).

Prints SKIP and exits 0 when ANTHROPIC_API_KEY is unset, so it never breaks
Version A or CI. With a key, it sends one citation-enabled document and asserts
the response carries a verbatim cited_text tagged with our document title.

No temperature/top_p: those are rejected with a 400 on Opus 4.8/4.7/Fable 5, so
omitting them keeps CITATIONS_MODEL free to point at any current model.
"""
import os
import sys


def main() -> int:
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("SKIP: no ANTHROPIC_API_KEY")
        return 0
    from anthropic import Anthropic

    client = Anthropic()
    model = os.getenv("CITATIONS_MODEL", "claude-sonnet-4-6")
    resp = client.messages.create(
        model=model,
        max_tokens=512,
        messages=[{"role": "user", "content": [
            {"type": "document",
             "source": {"type": "text", "media_type": "text/plain",
                        "data": "The cashier must confirm the student PIN before serving a meal."},
             "title": "NXT-TEST:AC",
             "citations": {"enabled": True}},
            {"type": "text",
             "text": "In one sentence, state what the cashier must do, and cite the source."},
        ]}],
    )
    cited = []
    for block in resp.content:
        if getattr(block, "type", None) == "text":
            for c in (getattr(block, "citations", None) or []):
                cited.append((getattr(c, "document_title", ""), getattr(c, "cited_text", "")))
    print("citations:", cited)
    ok = any(t == "NXT-TEST:AC" and (s or "").strip() for t, s in cited)
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
```

**PASS (no key — subscription-only machine):**
```powershell
python scripts\smoke_citations.py     # expect: "SKIP: no ANTHROPIC_API_KEY", exit 0
```
**PASS (with a key — later, on a Version B machine):** last line is `PASS`, and the printed
`citations:` list contains a `('NXT-TEST:AC', <non-empty>)` tuple.

---

## 4. Wave 1 — core modules (2 agents, parallel)

Both files are independent and fully testable without a key.

### T1.1 — Create `citation_gate.py`

Create `learning-agent\citation_gate.py` with **exactly**:

```python
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
```

Create `learning-agent\tests\test_run_gate.py` with **exactly**:

```python
import os
import demo
from citation_gate import run_gate

CLEAN = '<h1>T</h1>\n<p>Alpha claim.<!-- Source: [[NXT-1001:AC]] "Alpha." --></p>'
# tier_lie: the span "Alpha." lives in AC, but this comment claims DESC.
DIRTY = '<h1>T</h1>\n<p>Bad.<!-- Source: [[NXT-1001:DESC]] "Alpha." --></p>'


def _fix():
    demo._FIX = {"tickets": {"NXT-1001": {"ac": "Alpha.", "rn": "", "rn_internal": "", "desc": "Delta."}},
                 "epics": {}}


def test_substring_mode_is_byte_identical():
    _fix(); os.environ.pop("GATE_MODE", None)
    g = run_gate(CLEAN)
    assert g["citations"] is None
    assert g["substring"] == demo.validate_citations(CLEAN)
    assert g["passed"] is True


def test_tier_lie_fails():
    _fix(); os.environ.pop("GATE_MODE", None)
    g = run_gate(DIRTY)
    assert g["passed"] is False
    assert g["substring"]["tier_lie"] == 1


def test_both_mode_coverage_flags_uncited_claim():
    _fix(); os.environ["GATE_MODE"] = "both"
    try:
        html = CLEAN + "\n<p>An uncited overreaching claim with no source.</p>"
        g = run_gate(html)
        assert g["citations"]["uncited_claims"] == 1
        assert g["passed"] is False
    finally:
        os.environ.pop("GATE_MODE", None)
```

**PASS:**
```powershell
python -m pytest tests\test_run_gate.py -q     # expect all passed, exit 0
```

### T1.2 — Create `citations_client.py`

Create `learning-agent\citations_client.py` with **exactly**:

```python
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
```

Create `learning-agent\tests\test_citations_client.py` with **exactly**:

```python
from types import SimpleNamespace
import demo
import citations_client as cc


def test_build_ticket_documents_one_block_per_nonempty_tier():
    demo._FIX = {"tickets": {"NXT-1001": {"ac": "Alpha.", "rn": "Bravo.",
                                          "rn_internal": "", "desc": "Delta."}},
                 "epics": {}}
    docs = cc.build_ticket_documents(["NXT-1001"])
    assert [d["title"] for d in docs] == ["NXT-1001:AC", "NXT-1001:RN", "NXT-1001:DESC"]
    for d in docs:
        assert d["type"] == "document"
        assert d["source"]["type"] == "text"
        assert d["citations"]["enabled"] is True
    # exactly ONE cache breakpoint (API caps breakpoints at 4/request; a section can cite >4 docs)
    assert sum("cache_control" in d for d in docs) == 1
    assert docs[-1]["cache_control"]["type"] == "ephemeral"


def test_parse_citation_response_extracts_span_and_tier():
    cit = SimpleNamespace(type="text", cited_text="Alpha.", document_title="NXT-1001:AC")
    blocks = [
        SimpleNamespace(type="text", text="<h2>Rules</h2><p>Cashier confirms PIN.", citations=[cit]),
        SimpleNamespace(type="text", text="</p>", citations=[]),
    ]
    out = cc.parse_citation_response(blocks)
    assert out["segments"][0]["cites"] == [{"span": "Alpha.", "key": "NXT-1001", "tier": "AC"}]
    assert "Cashier confirms PIN" in out["prose"]


def test_segments_to_html_namespaces_cite_ids_by_section():
    segs = [{"text": "A.", "cites": [{"span": "Alpha.", "key": "NXT-1001", "tier": "AC"}]}]
    h1, e1 = cc.segments_to_html(segs, "s1")
    h2, e2 = cc.segments_to_html(segs, "s2")
    # same content, different section -> disjoint cite-ids (no registry collision)
    assert set(e1).isdisjoint(set(e2))
    assert "[CITE:NXT-1001:AC:s1:C000]" in h1
    assert "[CITE:NXT-1001:AC:s2:C000]" in h2
    assert e1["NXT-1001:AC:s1:C000"] == {"issue": "NXT-1001", "tier": "AC", "span": "Alpha."}
```

**PASS:**
```powershell
python -m pytest tests\test_citations_client.py -q     # expect all passed, exit 0
```

---

## 5. Wave 2 — wiring (1 agent, sequential; do AFTER Wave 1 passes)

### 5.0 — The anchor precheck (do this for EVERY edit in this wave)

Line numbers in the notes below are **hints only** — the file has drifted before and will again.
For each edit, first confirm the FIND anchor appears the **expected number of times**, then edit.
Standard precheck (adapt the pattern + count per task):

```powershell
# Count exact occurrences of the anchor. Must equal the "expected" count stated in the task.
(Select-String -Path <file> -Pattern '<anchor text>' -SimpleMatch).Count
```

**If the count does not match, STOP and report — do not edit.** Do not "search nearby."

### T2.1a — Imports

**`demo_app.py`** — anchor (expected count **1**):
```
from demo import build_demo_options, build_derive_options, build_derive_prompt, validate_citations
```
Replace that single line with:
```python
from demo import build_demo_options, build_derive_options, build_derive_prompt, validate_citations
from citation_gate import run_gate
from config import gate_mode
```

**`demo_d.py`** — anchor (expected count **1**):
```
from demo import ALLOWED_TOOLS as DEMO_ALLOWED_TOOLS
```
Add, immediately after that line:
```python
from citation_gate import run_gate
from config import citations_enabled
```

### T2.1b — Rename the reporting call-sites (behavior identical)

At each site the ONLY change is `validate_citations(X)` → `run_gate(X)["substring"]`. `integ` keeps
the exact same dict shape, so all downstream `integ[...]` reads are untouched.

**`demo_app.py`** — the following anchor appears **exactly twice** (near the old lines 4813 and
5318); replace **both** occurrences (replace-all is safe — both become the same text):
```
    integ = validate_citations(html)
```
→
```python
    integ = run_gate(html)["substring"]
```

**`demo_app.py`** — anchor (expected count **1**, near old line 295):
```
    integ = validate_citations(draft_html, transcript_text=transcript_text)
```
→
```python
    integ = run_gate(draft_html, transcript_text=transcript_text)["substring"]
```

**`demo_app.py`** — anchor (expected count **1**, near old line 4953):
```
    integ = validate_citations(html, transcript_text=transcript_text)
```
→
```python
    integ = run_gate(html, transcript_text=transcript_text)["substring"]
```

**`demo_app.py`** — anchor (expected count **1**, near old line 5490):
```
    integ = validate_citations(new_html, transcript_text=t_text)
```
→
```python
    integ = run_gate(new_html, transcript_text=t_text)["substring"]
```

**`demo_app.py`** — anchor (expected count **1**, near old line 7439):
```
    integ = validate_citations(draft_html)
```
→
```python
    integ = run_gate(draft_html)["substring"]
```

**`demo_d.py`** — anchor (expected count **1**, near old line 601):
```
    integ = validate_citations(html)
```
→
```python
    integ = run_gate(html)["substring"]
```

> After T2.1b (before the enforcement edits), the ONLY remaining `validate_citations(` calls in
> `demo_app.py` are the two ENFORCEMENT sites edited next (T2.1c inside `publish_pending`, T2.1d
> inside `approve_resource`). Confirm at this checkpoint:
> `(Select-String -Path demo_app.py -Pattern 'validate_citations(' -SimpleMatch).Count` should be
> **2**. If not, STOP. (Note: `demo_d.py` line ~111 has a `validate_citations(` mention inside a
> *comment* — that is not a call and is left untouched; that is why the final gate below matches
> the assignment `integ = validate_citations(`, which excludes comments.)

### T2.1c — Enforcement site: `publish_pending` (adds the coverage layer in Version B)

**`demo_app.py`** — anchor block (expected count **1**). FIND exactly:
```python
    ci = meta.get("citation_integrity")
    if not ci:  # older/non-Cell-D draft — compute grounding now
        if meta.get("module"):
            _ensure_fixture(meta["module"])
        integ = validate_citations(html_path.read_text(encoding="utf-8"),
                                   transcript_text=_transcript_text_for(meta))
        ci = {"tier_lie": integ["tier_lie"], "not_found": integ["quote_not_found"],
              "invalid_cite_id": 0}
    violations = (ci.get("tier_lie", 0) or 0) + (ci.get("not_found", 0) or 0) + (ci.get("invalid_cite_id", 0) or 0)
    if violations > 0:
```
REPLACE with:
```python
    ci = meta.get("citation_integrity")
    _gate = None
    # Version B (or a missing stored result) re-validates live so the coverage layer
    # applies. Version A with a stored clean result keeps its existing fast path.
    if gate_mode() in {"citations", "both"} or not ci:
        if meta.get("module"):
            _ensure_fixture(meta["module"])
        _gate = run_gate(html_path.read_text(encoding="utf-8"),
                         transcript_text=_transcript_text_for(meta))
        _sub = _gate["substring"]
        ci = {"tier_lie": _sub["tier_lie"], "not_found": _sub["quote_not_found"],
              "invalid_cite_id": 0, "citations": _gate["citations"]}
    violations = (ci.get("tier_lie", 0) or 0) + (ci.get("not_found", 0) or 0) + (ci.get("invalid_cite_id", 0) or 0)
    blocked = (not _gate["passed"]) if _gate is not None else (violations > 0)
    if blocked:
```
(Leave the `raise HTTPException(409, detail={...})` body that follows unchanged.)

### T2.1d — Enforcement site: `approve_resource` (the human floor into the Library)

**`demo_app.py`** — anchor block (expected count **1**). FIND exactly:
```python
    raw_html = html_path.read_text(encoding="utf-8")
    integ = validate_citations(raw_html, transcript_text=_transcript_text_for(meta))
    invalid = raw_html.count("INVALID_CITE_ID")
    ci = {"verified": integ["ok"], "tier_lie": integ["tier_lie"],
          "not_found": integ["quote_not_found"], "invalid_cite_id": invalid}
    violations = ci["tier_lie"] + ci["not_found"] + ci["invalid_cite_id"]
    if violations > 0:
```
REPLACE with:
```python
    raw_html = html_path.read_text(encoding="utf-8")
    _gate = run_gate(raw_html, transcript_text=_transcript_text_for(meta))
    integ = _gate["substring"]
    invalid = raw_html.count("INVALID_CITE_ID")
    ci = {"verified": integ["ok"], "tier_lie": integ["tier_lie"],
          "not_found": integ["quote_not_found"], "invalid_cite_id": invalid,
          "citations": _gate["citations"]}
    if not _gate["passed"]:
```
(Leave the `_log_review_decision({...})` call and the `raise HTTPException(409, ...)` body that
follow unchanged.)

### T2.2 — Writer seam (Version B generation)

**`demo_d.py`** — insert a NEW function immediately BEFORE the `async def write_section(` line.
Anchor (expected count **1**):
```
async def write_section(sec: dict, registry: dict, by_ticket: dict, module: str,
```
Insert, on the lines just above it:
```python
async def _write_section_via_citations(sec: dict, registry: dict, module: str,
                                       sem: asyncio.Semaphore, directive: str = "") -> dict:
    """Version B writer: the Citations API produces the grounded spans. Returns the SAME
    section shape as write_section ({title, html-with-[CITE:id], ...}) and merges synthetic,
    section-namespaced registry entries so the existing assemble() renders them verbatim."""
    import time as _time
    import citations_client  # lazy: Version A never imports anthropic

    t0 = _time.monotonic()
    title = sec.get("title", "Section")
    sid = sec.get("id") or _slug(title)  # section id namespaces cite-ids (no cross-section collision)
    docs = citations_client.build_ticket_documents(sec.get("ticket_keys") or [])
    async with sem:
        res = await asyncio.to_thread(
            citations_client.write_section_citations, sec, docs, module, directive)
    # segments_to_html is pure + unit-tested; entries are globally unique via `sid`.
    html, entries = citations_client.segments_to_html(res["segments"], sid)
    registry.update(entries)  # safe under asyncio: runs on the event-loop thread after the await
    if not html.lower().startswith("<h2"):
        html = f"<h2>{title}</h2>\n{html}"
    return {"title": title, "html": html, "stop_reason": "citations",
            "secs": round(_time.monotonic() - t0, 1), "errored": False,
            "attempts": 1, "usage": res.get("usage")}


```

**`demo_d.py`** — then branch inside `write_section`. Anchor block (expected count **1**). FIND:
```python
                        section_tmpl: str = SECTION_SYSTEM_PROMPT) -> dict:
    title = sec.get("title", "Section")
```
REPLACE with:
```python
                        section_tmpl: str = SECTION_SYSTEM_PROMPT) -> dict:
    # Version B: only Jira-grounded sections (with ticket_keys) go through the Citations API.
    # Transcript-only sections (span_ids) and structural sections (no keys) fall through to the
    # existing SDK writer — identical to Version A for those sections.
    if citations_enabled() and sec.get("ticket_keys"):
        return await _write_section_via_citations(sec, registry, module, sem, directive=directive)
    title = sec.get("title", "Section")
```

No orchestrator edits are needed: `write_section` and `assemble` share the same `registry`
object, so the section-namespaced synthetic entries merged above are visible to `assemble`.

### Wave 2 PASS gate (proves Version A unchanged)

```powershell
# 1) imports still clean
python -c "import demo, demo_d, demo_app; print('imports OK')"
# 2) no raw grounding CALL remains — every `integ = validate_citations(` is now run_gate.
#    (Match the assignment, not a bare 'validate_citations(', so the demo_d.py comment on line
#    ~111 does not count. Both enforcement sites were rewritten to `_gate = run_gate(...)`.)
(Select-String -Path demo_app.py -Pattern 'integ = validate_citations(' -SimpleMatch).Count   # expect 0
(Select-String -Path demo_d.py  -Pattern 'integ = validate_citations(' -SimpleMatch).Count    # expect 0
# 3) the gate wrapper is byte-identical to the old check in substring mode
python -m pytest tests\test_run_gate.py tests\test_citations_client.py -q
# 4) full regression + the existing suites — compare to your §2 baseline
python -m eval.regression
python -m pytest eval\test_builder_beats.py tests\test_evaluator_task5.py -q
```
**PASS:** `imports OK` prints; the two `Select-String` counts are exactly `2` and `0`;
`test_run_gate` + `test_citations_client` green; `eval.regression` matches the §2 baseline (no
new failures); `test_builder_beats` and `test_evaluator_task5` green.

---

## 6. Wave 3 — evals (parallel; after Wave 2)

### T3.1 — Create `eval/test_overreach.py`

Create `learning-agent\eval\test_overreach.py` with **exactly**:

```python
"""Proves the capability Version B adds over Version A: catching an over-claim (a substantive
sentence with NO citation). Runs without an API key."""
import os
import demo
from citation_gate import run_gate


def _fix():
    demo._FIX = {"tickets": {"NXT-1001": {"ac": "Alpha.", "rn": "", "rn_internal": "", "desc": ""}},
                 "epics": {}}


# One properly-cited claim + one invented, uncited claim.
OVERREACH = (
    "<h1>Guide</h1>\n"
    '<p>Alpha is required.<!-- Source: [[NXT-1001:AC]] "Alpha." --></p>\n'
    "<p>The system also emails the district superintendent automatically.</p>"
)


def test_version_b_catches_overreach():
    _fix(); os.environ["GATE_MODE"] = "both"
    try:
        g = run_gate(OVERREACH)
        assert g["passed"] is False
        assert g["citations"]["uncited_claims"] >= 1
    finally:
        os.environ.pop("GATE_MODE", None)


def test_version_a_passes_overreach_through():
    _fix(); os.environ.pop("GATE_MODE", None)   # substring / Version A
    g = run_gate(OVERREACH)
    assert g["citations"] is None
    assert g["passed"] is True   # substring only checks present citations
```

**PASS:**
```powershell
python -m pytest eval\test_overreach.py -q     # expect all passed, exit 0
```

### T3.2 — Create `eval/parity.py`

Create `learning-agent\eval\parity.py` with **exactly**:

```python
"""Gate-parity report: on KNOWN-clean drafts (every claim block cited), Version B's coverage
layer must not fail anything the substring layer passes. PASS when divergences == 0.
Run: python -m eval.parity"""
import os
import sys
import demo
from citation_gate import run_gate

CLEAN_DRAFTS = [
    ('<h1>A</h1>\n<p>Alpha.<!-- Source: [[NXT-1001:AC]] "Alpha." --></p>\n\n'
     "<h2>Sources</h2>\n<ul>\n<li><code>NXT-1001</code> — x</li>\n</ul>"),
    ('<h1>B</h1>\n<p>Bravo.<!-- Source: [[NXT-1001:RN]] "Bravo." --></p>\n'
     '<ul>\n<li>Point.<!-- Source: [[NXT-1001:AC]] "Alpha." --></li>\n</ul>'),
]


def main() -> int:
    demo._FIX = {"tickets": {"NXT-1001": {"ac": "Alpha.", "rn": "Bravo.",
                                          "rn_internal": "", "desc": ""}},
                 "epics": {}}
    os.environ["GATE_MODE"] = "both"
    divergences = 0
    try:
        for i, html in enumerate(CLEAN_DRAFTS):
            g = run_gate(html)
            sub_ok = (g["substring"]["tier_lie"] == 0 and g["substring"]["quote_not_found"] == 0)
            if sub_ok and not g["passed"]:
                divergences += 1
                print(f"  draft {i}: substring PASS but gate FAIL -> {g['citations']}")
    finally:
        os.environ.pop("GATE_MODE", None)
    print(f"divergences: {divergences}")
    return 0 if divergences == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
```

**PASS:**
```powershell
python -m eval.parity     # expect final line "divergences: 0", exit 0
```

### T3.3 — Create `eval/coverage_report.py` (informational, keyless)

Create `learning-agent\eval\coverage_report.py` with **exactly**:

```python
"""INFORMATIONAL (never fails): show how the coverage layer would score REAL drafts, so the team
can see whether GATE_MODE=both would false-positive on legitimately-structured content BEFORE
Version B relies on it. Fixture-free — it calls only the coverage layer.
Run: python -m eval.coverage_report [file1.html file2.html ...]  (defaults to drafts\\*.html)"""
import glob
import os
import sys
from citation_gate import _uncited_claim_blocks


def main() -> int:
    files = sys.argv[1:] or sorted(glob.glob(os.path.join("drafts", "*.html")))
    if not files:
        print("no draft html found (looked in drafts\\*.html)")
        return 0
    for f in files:
        try:
            html = open(f, encoding="utf-8").read()
        except OSError as e:
            print(f"  skip {f}: {e}")
            continue
        total, uncited = _uncited_claim_blocks(html)
        print(f"{uncited:>3} uncited / {total:>3} claim blocks   {os.path.basename(f)}")
    print("\n(informational only — nonzero 'uncited' shows where GATE_MODE=both would flag a draft)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**PASS:**
```powershell
python -m eval.coverage_report     # exit 0; prints one line per draft. Never fails by design.
```
> Read the output. If real Version-A drafts show many `uncited` claim blocks, that is expected
> (Version A never runs coverage). It tells you the Version B *writer* prompt must cite every
> sentence — which the live Version B PASS gate (§7) verifies.

---

## 7. Wave 4 — config docs + full verification (1 agent)

### T4.1 — Update `.env.example`

**`.env.example`** — anchor block (expected count **1**). FIND:
```
# Leave ANTHROPIC_API_KEY UNSET unless you specifically want to bill against a
# paid Anthropic API key instead of using Claude Code subscription auth.
#
# ANTHROPIC_API_KEY=
```
REPLACE with:
```
# Leave ANTHROPIC_API_KEY UNSET unless you specifically want to bill against a
# paid Anthropic API key instead of using Claude Code subscription auth.
#
# ANTHROPIC_API_KEY=

# ─── Grounding gate mode (two-version switch) ────────────────────────
# substring (default) -> Version A: existing behavior, subscription only.
# both                -> Version B: Citations-API writer (needs ANTHROPIC_API_KEY)
#                        PLUS the stricter citation-coverage gate.
# citations           -> coverage gate ON; writer uses the API only if a key is set.
GATE_MODE=substring

# Which model the Citations writer uses (Version B). Default claude-sonnet-4-6 (matches the
# SDK section-writer tier). Use claude-opus-4-8 for higher-quality prose. Use BARE model ids —
# never append a date suffix (a dated id 404s on the first-party API).
# CITATIONS_MODEL=claude-sonnet-4-6
```
**PASS:**
```powershell
Select-String -Path .env.example -Pattern "GATE_MODE=substring"              # must match
Select-String -Path .env.example -Pattern "Leave ANTHROPIC_API_KEY UNSET"    # original comment intact
```

### Full end-to-end verification

**Version A (no key — the default):**
```powershell
Remove-Item Env:GATE_MODE -ErrorAction SilentlyContinue
Remove-Item Env:ANTHROPIC_API_KEY -ErrorAction SilentlyContinue
python -m pytest tests\test_run_gate.py tests\test_citations_client.py eval\test_overreach.py -q
python -m eval.parity
python -m eval.coverage_report
python -m eval.regression
python scripts\smoke_citations.py       # expect "SKIP: no ANTHROPIC_API_KEY"
```
Then start the app and drive one draft through generate → publish_pending → approve:
```powershell
python demo_app.py        # serves on port 8001; use the UI to generate + approve a draft
```
**PASS:** all pytest green; `divergences: 0`; `coverage_report` exits 0; `eval.regression`
matches baseline; smoke prints SKIP; a generated draft reaches `draft`, `publish_pending` needs a
trainer + clean grounding, and `approve` moves it to `Approved · in Library`.

**Version B (only on a machine WITH a paid key):**
```powershell
$env:GATE_MODE = "both"
$env:ANTHROPIC_API_KEY = "sk-ant-..."   # your key
python scripts\smoke_citations.py        # expect final line "PASS"
python -m pytest tests eval\test_overreach.py -q
python demo_app.py                        # generate a Jira-grounded draft; confirm spans carry Citations
```
**PASS:** smoke prints `PASS`; a generated draft's Jira-grounded section spans come from the
Citations API (`stop_reason: "citations"` in the section metadata); `approve` still enforces clean
grounding (now including coverage). If the writer emits an uncited claim, `approve` returns 409
with `citations.uncited_claims > 0` — that means tighten the writer prompt to cite every sentence,
not a gate bug.

---

## 8. Appendix (OPTIONAL — not a pass/fail gate): Batch API for eval cost

Prompt caching is already applied (the last ticket-document block carries
`cache_control: ephemeral`, so a section that retries reuses its document prefix at cache-read
rates; the cap of 4 breakpoints/request is respected by using a single breakpoint).

If you later want to run `eval/capability.py` pass@k trials through the **Message Batches API**
for ~50% lower cost, add a `--batch` flag that (a) prints `SKIP: no ANTHROPIC_API_KEY` and exits 0
when no key is present, and (b) with a key, submits the trial prompts via
`client.messages.batches.create(...)`, polls `retrieve(id).processing_status` to `"ended"`, reads
results **keyed by `custom_id`** (batch results are unordered), and asserts the pass@k matches the
non-batch path. Cost optimization only; it does not change grounding behavior, so it is out of the
core waves.

---

## 9. Task ↔ file summary (for the orchestrator)

| Task | Creates / edits | Verify command | Needs key? |
|---|---|---|---|
| T0.1 | `config.py` | `python -c "import config; ..."` | no |
| T0.2 | `requirements.txt`, `scripts/smoke_citations.py` | `python scripts\smoke_citations.py` | live-only |
| T1.1 | `citation_gate.py`, `tests/test_run_gate.py` | `pytest tests\test_run_gate.py` | no |
| T1.2 | `citations_client.py`, `tests/test_citations_client.py` | `pytest tests\test_citations_client.py` | no |
| T2.1 | `demo_app.py` (import + 6 reporting renames + 2 enforcement blocks), `demo_d.py` (import + 1 rename) | `integ = validate_citations(` counts 0/0 + `eval.regression` == baseline | no |
| T2.2 | `demo_d.py` (writer seam + helper) | `import demo_d` OK; regression green | no |
| T3.1 | `eval/test_overreach.py` | `pytest eval\test_overreach.py` | no |
| T3.2 | `eval/parity.py` | `python -m eval.parity` → `divergences: 0` | no |
| T3.3 | `eval/coverage_report.py` | `python -m eval.coverage_report` (exit 0) | no |
| T4.1 | `.env.example` | `Select-String ... GATE_MODE` | no |

**Ordering:** Wave 0 → Wave 1 (parallel) → Wave 2 (sequential) → Wave 3 (parallel) → Wave 4.
Do not start a wave until the previous wave's PASS gates are green.

**Guardrails (unchanged repo rules):** no Jira push; customer-facing exports still strip
`<!-- Source -->` comments; keep `ANTHROPIC_API_KEY` unset unless deliberately running Version B;
`agent_tasks.py` / `evaluator_runner.py` / `app.py` are left untouched.
