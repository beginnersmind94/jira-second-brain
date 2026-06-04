# SOP — Building a PrimeroEdge Function FAQ from Freshdesk

Standard operating procedure for turning a Freshdesk support filter into a customer-facing
FAQ (`.docx` + `.pdf`) plus a rejected-tickets register. Follow this so we don't reinvent
the wheel each time. See `README.md` for the directory layout; this file is the *playbook*.

**Golden rule:** FAQ *content* (the answers) comes only from the support conversations.
*Navigation/breadcrumbs* come from the PrimeroEdge Quick Step guide. *Framing/context* comes
from the jira-brain wiki. Never invent capabilities the conversations don't demonstrate
(CLAUDE.md anti-hallucination rules apply).

---

## 0. Inputs you need before starting

| Input | Where it comes from | Notes |
|---|---|---|
| Ticket filter CSV | Freshdesk → export the function's filter | First column **must** be `Ticket ID`; header row present |
| PrimeroEdge Quick Step guide (PDF) | The function's official guide | Breadcrumbs/labels only. If none exists, ground breadcrumbs in tickets and **say so** in the FAQ nav note |
| Freshdesk API key | hardcoded in `fetch/fetch_conversations.py` | **Never commit fetch scripts with the key to git** |
| jira-brain wiki | `../wiki/concepts/*.md`, `../wiki/workflows/*.md` | Product framing/context only |

**Sanity check first:** note the ticket count shown in the Freshdesk filter UI. After fetch,
the fetched count **must equal** that number. (We once had 83 in the filter but 82 in the CSV —
one ticket silently missing. Reconcile counts before building anything.)

---

## 1. Fetch the conversations (lossless)

```
python fetch/fetch_function.py "<path/to/tickets.csv>" conversations_<function>
```
Outputs `conversations/conversations_<function>.jsonl` + `_digest.txt`.

- The digest keeps **raw** body text (signatures, quoted history, chat timestamps). That is
  intentional — the LLM parses it; do **not** regex-clean it.
- Confirm the run prints `fetched == filter count`, `skipped: 0`. If any skipped, investigate
  before proceeding.

## 2. Extract guide breadcrumbs (navigation only)

Convert the guide PDF to text into `build/guides/guide_<function>.txt` (pypdf). Pull the exact
menu path, tab names, button/field labels. These are the ONLY source for navigation in the FAQ.

## 3. Draft the content spec

Read the **entire** digest (every ticket, end to end). For large sets, delegate one
**analysis agent per function** (see Appendix A) — but the agent must read the full digest
directly, not snippets. Produce `build/specs/<function>_spec.py`:

```python
TITLE = "Transfer Items"
OUT_BASENAME = "PrimeroEdge-Transfer-Items-FAQ"
INTRO = "..."          # 2-3 sentences; note it's from real support cases + one wiki-framing sentence
NAV_NOTE = "..."       # core breadcrumb from the guide
SECTIONS = [
    ("Section heading", [
        ("Question?", ["Answer paragraph.", "Optional second paragraph."], "Tickets 123456, 234567"),
    ]),
]
CLOSING = "Still stuck? PrimeroEdge Customer & Expert Care ... 866.442.6030 ..."
SOURCE_NOTE = "Source: ... ticket numbers are internal references only. ..."
```

Rules while drafting:
- **Every answer cites ≥1 ticket** in its `sources` string. No support → don't write it.
- **One question often combines several tickets** — list them all in `sources`.
- **PII redaction:** no district names, person names, emails, or phone numbers in FAQ text.
  Ticket numbers are internal references and are kept.
- **Breadcrumbs from the guide; behavior from tickets.** If the guide and a ticket conflict on a
  label, the guide wins for navigation; flag the conflict.
- Standalone functions (Ingredients, Menu Cycles) live in `make_<function>_faq.py` with the same
  `SECTIONS` shape inline instead of a spec file.

## 4. Wiki framing pass

Read the matching wiki concept/workflow (`Inventory`, `Production`, `Menu-Planning`, etc.).
Weave **one** framing sentence into the INTRO (the "why"), reconcile terminology, and note the
cross-check in `SOURCE_NOTE`. Do not add behavioral claims that aren't ticket-backed.
(`build/apply_wiki_framing.py` is the helper used last time.)

## 5. Coverage reconciliation — ONE rule, applied to every ticket (authoritative)

**Classification rule — do NOT vary it between functions:**
- **USED** = the conversation contains a concrete, reusable answer/resolution that an FAQ question reflects — a fix, a setting, a navigation/how-to, a documented behavior or limitation, a "request X from Expert Care" path, or a documented bulk process. Operationally, **USED ⟺ the ticket is cited by a Q&A in the FAQ.**
- **REJECTED** = no FAQ answer is based on it. Pick one category: Self-resolved; No resolution captured (call/GTA/escalation with no outcome, trails off, inconclusive); Transient/system error; Training/resource request; Routed/out-of-scope; Other-module/integration; Data fix (no user guidance); No content.
- **Tie-break:** any concrete reusable guidance → USED.

Apply it identically across functions (one parallel classifier agent per function — Appendix A — writing `build/audit/<fn>.json`). Then reconcile against the authored FAQ **deterministically** (`build/reconcile_audit.py`):
- Strip a rejected ticket from a Q&A's `sources` only if that Q&A keeps ≥1 used source (drops redundant "padding" citations — this is the consistency fix).
- If a Q&A's *only* source is agent-rejected, keep it cited (the answer is grounded on it) rather than deleting the answer.
- **FINAL rejected = every filter ticket not cited after the strip.** It goes in the register (step 7), never the FAQ.

Guarantees, verified every run: `USED ∪ REJECTED = filter`, `USED ∩ REJECTED = ∅`, no answer gutted. Do not re-introduce per-function judgment — that is exactly the inconsistency this rule removes.

Helpers:
- `build/augment_specs.py` — fold extra ticket IDs into existing Q&A `sources`, add new Q&As, for
  spec-based functions.
- `build/patch_standalone.py` — same for the standalone `make_*.py` builders.
- For a large gap, delegate a **reconcile agent** (Appendix A) that maps each uncited ticket to
  `fold` / `new` / `reviewed` and writes `build/specs/<function>_reconcile.py`.

**Definition of "rejected" categories:** Self-resolved; Transient/system error; Training/resource
request; Routed/out-of-scope; Other-module/integration; Data fix (no user guidance); No content.

## 6. Build the documents

```
python make_all_faqs.py                 # all spec-based functions -> deliverables/
python make_<function>_faq.py           # one standalone function -> deliverables/
```
`faq_builder.py` renders the `.docx` then converts to `.pdf` via **MS Word COM (pywin32)**.
Word COM is **single-threaded** — builds run sequentially; never parallelize PDF conversion.

## 7. Rejected-tickets register (Excel)

1. Run a **workflow** (Appendix B) — one agent per function reads its rejected tickets and returns,
   for each: `subject`, `date`, `category`, one-sentence `reason`, and a **verbatim** `citation`
   (strip emails/phones from the quote).
2. `python build/build_rejected_xlsx.py` → `deliverables/PrimeroEdge-FAQ-Rejected-Tickets.xlsx`:
   - **Rejected Tickets** sheet: Document · Ticket ID · Freshdesk URL · Subject · Date · Category ·
     Why rejected · Citation.
   - **Coverage Summary** sheet (the funnel): `Total unique → Tickets used → Combined into
     (questions) → Rejected`, with `Total unique = Tickets used + Rejected`.

## 8. Verify before handoff (quality gates)

Run the parity check — for each function, the tickets printed in the doc plus the rejected ones
must equal the filter set, with nothing left over:

```python
# pull unique ticket #s from the actual deliverable docx and reconcile vs filter + rejected excel
from docx import Document; import re, json, os, openpyxl
ids = lambda p: set(re.findall(r"\b\d{5,7}\b", "\n".join(x.text for x in Document(p).paragraphs)))
# assert ids(doc) | rejected_ids == filter_ids   and   ids(doc) & rejected_ids == set()
```

Gates (all must pass):
- [ ] fetched count == Freshdesk filter count (step 0)
- [ ] every Q&A has a non-empty `sources`
- [ ] doc-cited ∪ rejected == filter; doc-cited ∩ rejected == ∅
- [ ] grounding spot-check: a few distinctive claims appear verbatim in the digest
- [ ] PII scan: no names/emails/phones in FAQ body (ticket #s OK)
- [ ] breadcrumbs match the guide; navigation with no guide is flagged in the nav note

## 9. Hand off

Deliverables live in `deliverables/`. Share the `.pdf` (and `.docx` for editing) with the SME,
plus the rejected-tickets `.xlsx` so the triage decisions are auditable.

---

## Appendix A — Analysis / reconcile agent prompt skeleton

> You are drafting (or reconciling) the PrimeroEdge "<Function>" FAQ. Content comes ONLY from the
> support conversations. (1) Read the FULL digest `conversations/conversations_<fn>_digest.txt`
> end to end (chunk through it; ignore email/chat boilerplate). (2) Read
> `build/guides/guide_<fn>.txt` for breadcrumbs/labels ONLY. (3) Rules: every answer cites ≥1
> ticket; redact PII; breadcrumbs from guide, behavior from tickets; don't invent; group multi-
> ticket cases into one Q&A; skip low-signal tickets. (4) Write the spec / reconcile file in the
> exact shape above. (5) Final message: tickets-read count, low-signal IDs, Q&A count, and 3-4
> verbatim digest quotes + ticket IDs so the orchestrator can audit grounding.

One agent per function; they're independent → launch in parallel (background). Have each **write
its spec file** rather than returning huge text. Do the PDF build yourself (Word COM, sequential).

## Appendix B — Rejected-register workflow shape

`Workflow` with one phase; `parallel()` over the functions that have rejected tickets; each
`agent(..., {schema})` returns `{rows:[{ticket_id, subject, date, category, reason, citation}]}`;
the script flattens and returns them; you assemble the `.xlsx` with `build/build_rejected_xlsx.py`.
(Only opt into Workflow when the user asks for multi-agent orchestration.)

## Appendix C — Known gotchas

- **API key**: `fetch/*.py` hold the Freshdesk key in plaintext — keep them out of git.
- **Word COM only**: no `docx2pdf`/LibreOffice here. PDF = Word COM via pywin32, Windows only,
  sequential. `pdftoppm` is **not** installed (can't rasterize PDFs); read `.docx`/digests instead.
- **`openpyxl` is available** (3.1.x) for the Excel.
- **Filter vs fetch count**: always reconcile (the 83-vs-82 lesson). A missing ticket is invisible
  unless you check.
- **Stale deliverables**: after edits, always regenerate into `deliverables/` and re-verify against
  the *generated doc*, not the spec — a measurement on an old file is the usual source of confusion.
- **Paths**: builders resolve everything from their own location (`build/specs/`, `deliverables/`).
  If files get moved, fix the path constants (we did this once during a repo reorg).
- **Low-signal tickets** (CLAUDE.md): Duplicate/Won't-Do or empty tickets are expected to land in
  the rejected register, not the FAQ.
