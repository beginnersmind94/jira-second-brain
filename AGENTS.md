# Jira Second Brain — Operating Instructions

## Purpose
Turn every Jira ticket into institutional knowledge that new hires can learn from.
The wiki is the deliverable. Tickets are the raw material.

## Directory Rules
- `raw/tickets/` — one file per issue, filename = issue key (FIN-1234.md). **Filename is stable; field contents mirror Jira.** Each ingestion run rewrites a ticket file when its Jira fields differ from what's on disk; identical content is a no-op.
- `raw/comments/` — comments grouped by issue key. Append-only.
- `raw/_imports/` — drop zone for Jira exports. Move to `_imports/processed/` after ingestion.
- `wiki/` — you own this. Compile, link, and lint it.

### Mirror semantics caveat for wiki citations
Because ticket field contents track Jira (status, sprint, resolution, description, AC, components), wiki text that *paraphrases* a ticket's description can drift if Jira edits that description later. The wikilink target is always live — but the wiki page's prose may no longer match the ticket it cites. When citing, prefer naming what the ticket *did* (shipped behavior, decisions, scope) over quoting how it *was described*. Re-verify wiki claims against tickets if a major Jira edit pass happens.

## Page Types in wiki/

### concepts/
Domain or product concepts that recur across tickets. Each page:
- What the concept is, in plain language
- How it shows up in our product
- Tickets that shaped current behavior (wikilinks to raw/)
- Open questions or known edge cases

### workflows/
How we do things. Each workflow cites 3–8 example tickets.

### entities/
People, teams, modules, customers. Cross-linked everywhere relevant.

### decisions/
Architectural or product decisions. Format: Context → Options → Decision →
Consequences → Source tickets.

### onboarding/
Role-specific starter guides, DERIVED from concepts + workflows + decisions.

### training/
Training documents for specific skills/topics.

## Wiki-Writing Rules
1. Every factual claim must wikilink back to a source ticket in `raw/tickets/`.
2. Use plain language. Assume the reader is a new hire who joined yesterday.
3. When two tickets contradict, flag with `> [!warning] Contradiction` listing both.
4. Prefer concepts/ and workflows/ over ticket-by-ticket summaries.
5. Redact customer PII (names, emails, phones). Use role labels like `<District A>`.
   PII may remain in raw/.
6. Update `wiki/index.md` and append to `wiki/log.md` on every ingestion run.

## Low-Signal Tickets
Tickets resolved as Duplicate or Won't Do, OR with no description AND <2 comments,
are low-signal. Create the raw/ file with `low_signal: true` in frontmatter.
Do NOT create wiki pages from them unless they demonstrate an otherwise-invisible
workflow pattern.

## Linting Rules
- Every wiki page must have ≥1 source ticket link.
- Every entity mentioned by name must have an entities/ page.
- Scan for broken wikilinks.
- Flag concept pages with <3 source tickets as merge candidates.
- Flag pages with no new tickets in 90+ days as stale.

## Anti-Hallucination Rules (for customer-facing and onboarding docs)

These exist because customer-facing writing ("plain English, reads well") creates
pressure to smooth over gaps in source evidence. Every rule below is a specific
guard against a failure mode that has actually occurred.

### 1. Persona-first, always
Before writing a single sentence of a customer-facing doc, grep every source
ticket for `^As a` / `^As an` and list the personas. The actor in the doc's verbs
must match one of those personas. If your sentence says "the district admin does X"
but every ticket says "the Cybersoft Implementation team does X," the sentence is
wrong regardless of how natural it sounds.

**Failure mode guarded:** fluency-over-grounding. When doc tone pushes toward
customer-friendly voice, "As a Cybersoft Implementation team member" silently
becomes "As a district user" — and the doc now claims agency the product doesn't give.

### 2. Cite or cut
Every non-obvious claim — whether backed by a Jira ticket, an external article,
or a research paper — needs a named source before it ships. If you can't name
the source, delete the claim. Pattern-matching ("the product probably supports X
because other modules do") is not evidence.

**Failure mode guarded:** ghost references / fabricated features. E.g. inventing
cross-district form sharing because other multi-tenant features allow it.

### 3. No cross-feature pattern matching
Do not import capability claims from one feature area into another without
source-ticket evidence in the target area. Audit trails in Accountability tickets
do NOT imply audit trails in Forms. Each feature gets grounded independently.

**Failure mode guarded:** context contamination. E.g. writing an "audit trail"
FAQ entry for Forms because it was a real feature of Accountability.

### 4. Tag ownership on every action
In onboarding docs, every step has an owner tag: `Cybersoft`, `Your team`,
`Cybersoft + Your input`, or `Parent/applicant`. If you can't assign ownership
from source tickets, the step is unresearched — stop and research before shipping.

**Failure mode guarded:** implied-agency drift. Customers read unqualified verbs
as "we do this ourselves" by default.

### 5. Verify before ready
Before any artifact is marked ready (customer-facing draft, citation, claim, output):
- (a) Each claim traces to its source.
- (b) Each source has been read directly — not surfaced from search snippets.
- (c) "Reads well" is not the standard; "matches what it cites" is.

When a capability is ambiguous, the safe default is "not supported today" — never
invent a feature to close a gap.

**Failure modes guarded:** the "helpful yes" hallucination (inventing capabilities
to produce smoother answers), knowledge-saying disconnect (reading the right
tickets but writing contradictory output), citation unfaithfulness (a
real-but-misapplied citation is still a hallucination), and missing verification
("reads well" ≠ "is accurate").

---

## Sources that informed these rules (verified by direct read)
Each entry tagged by `source_type` so the incentive structure is visible at the
point of citation: `peer-reviewed` · `independent` · `vendor-marketing` · `other`.

- Alansari, A. & Luqman, H. *Large Language Models Hallucination: A Comprehensive Survey.* arXiv:2510.06265v3 (2025). `source_type: peer-reviewed-adjacent` (arXiv preprint). https://arxiv.org/html/2510.06265v3
- Tay, A. *Why Ghost References Still Haunt Us in 2025 — And Why It's Not Just About LLMs.* Substack, Dec 22, 2025. `source_type: independent`. https://aarontay.substack.com/p/why-ghost-references-still-haunt
- Lema, C. *AI Context Failures: Nine Ways Your AI Agent Breaks.* Feb 9, 2026. `source_type: independent`. https://chrislema.com/ai-context-failures-nine-ways-your-ai-agent-breaks/
- MindStudio Team. *AI Agent Failure Modes: 4 Ways Your Agent Knows the Answer But Says the Wrong Thing.* Mar 19, 2026. `source_type: vendor-marketing` (MindStudio sells AI agent infra). https://www.mindstudio.ai/blog/ai-agent-failure-modes-reasoning-action-disconnect
- Glean Team. *Understanding LLM hallucinations in enterprise applications.* Nov 6, 2025. `source_type: vendor-marketing` (Glean sells enterprise RAG). https://www.glean.com/perspectives/when-llms-hallucinate-in-enterprise-contexts-and-how-contextual-grounding

---

## On expanding this rule set
If a new failure mode appears in a future session, first check whether an existing
rule already covers it and just wasn't applied. Five rules produce more careful
behavior than eight. Resist the urge to add Rule 6.
