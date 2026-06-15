# Story Spec Standard + Definition of Done

**Scope:** every unit of work in this repo — `jira-brain/` (FIN/Jira), `learning-agent/`, and any
sub-project. Down to a 5-pointer. No exceptions for "tiny" stories; tiny stories are where façade
hides best.

**Status:** standing standard. Both project workflows reference it:
- `learning-agent/CLAUDE.md` → *Feature development workflow*
- `jira-brain/CLAUDE.md` → *Repeatable workflows*
- `.claude/commands/new-feature.md` scaffolds to this shape.

---

## Why this exists

The recurring failure mode is **wide, shallow façades** — surfaces that render seeded data, log a
FEATURES row, and look finished, but aren't wired end-to-end. `learning-agent/FEATURES.md` even uses
"Façade data" as a status, so half-done reads as shipped.

A free-text acceptance checklist is what lets it through. `- [ ] show a roster grid` is satisfied by
a roster grid full of seeded names. The fix is not "try harder" — it's a spec whose acceptance
criteria **cannot be satisfied by a façade**, plus a Definition of Done that requires those criteria
to be *demonstrated* green against the running system before the work is `Done ✓`.

This is the feature-side equivalent of the content grounding gate. Just as `demo.validate_citations`
blocks publish until every claim traces to a verbatim source at the correct tier, the **Definition of
Done blocks `Done ✓` until every acceptance criterion is demonstrated against real data.** Grounding
is a property of the system, not a hope — and so is "it works."

---

## The one rule that makes a spec façade-proof

> **Every acceptance criterion must be an executable black-box test against the running system that
> names exact observable values** — exact columns, exact format, exact forbidden outputs, a concrete
> example input and its exact required output.

If an AC can be passed by rendering a placeholder, it is not an AC yet. Rewrite it until **only the
real behavior passes.** The canonical example: an Oracle FBDI report AC that enumerates the six
columns that must appear *and* the eight constant columns that must **not** — you cannot satisfy that
without generating the real file and diffing it. Seeded data fails it instantly.

---

## The spec contract — seven parts

Every story carries all seven. A part that is genuinely N/A is written `N/A — <reason>`, never
omitted (an empty section is a question you didn't answer).

### 1. Header + pinned dependencies
Title, status, points/severity, persona. **Every dependency named by id** — upstream tickets, the
data set it builds on, framework tickets, external doc URLs. Nothing free-floating. If it depends on
work that isn't done, say so (`Depends on: NXT-73628`).

### 2. Scope — in *and* out
Two lists. **Out-of-scope is mandatory and load-bearing**: it fences scope creep *and* gold-plating.
"No constant-value column (does not exist)", "no turnkey delivery", "no changes to the framework" —
each out-of-scope line is something a reader might otherwise assume you'd build.

### 3. Requirements — numbered and exact
`1.1, 1.2, 3.2 …` so each is independently addressable in review and commits. Name **exact** field
names, column order, target mappings, formats. This is `CLAUDE.md` anti-hallucination **Rule 4 — No
invented specifics** applied to the spec: if you don't know the exact label/value/format, you don't
guess — you write `[TO VERIFY at onboarding]` and name the failure if the assumption is wrong (e.g.
"a mismatch produces a valid-but-wrong file").

### 4. Edge / Empty / Error states — a table
| Case | Behavior |
Enumerate them: empty input, zero rows, max scale, the boundary values, the "user did the dangerous
thing" path. **This is where façades die**, so it is mandatory — empty period → headers only; N
segments → exactly N columns; modify-without-clone → persists, no restore.

### 5. Defaults
The values chosen when the user specifies nothing. (`Contains PII = No`, `no constants`, sort order,
initial filter.) State them; don't let them be discovered in the code.

### 6. Acceptance criteria — Given / When / Then, executable
Each AC is `Given <real precondition>, When <action>, Then <exact observable outcome>`, with a
concrete example value where a format or boundary is involved. See the rule above. One AC per
distinct behavior; an AC that needs "and" twice is two ACs.

### 7. Future option — explicitly deferred
What you are deliberately *not* building now, and the rationale that **nothing built now is thrown
away** when it lands later. Prevents "build it all now" and records the upgrade path so the deferral
is a decision, not an omission.

---

## Definition of Done (the gate)

A story is marked `Done ✓` **only when every one of these holds.** Until then it is `In progress`,
no matter how finished it looks.

1. **Every Gherkin AC demonstrated green against the running app with real (non-seeded) data.** Each
   AC line carries a one-line **evidence note** — the command run, the observed output, or the test
   name. "Demonstrated" means *shown* (run output / screenshot / passing test), **never asserted.**
2. **Every Out-of-scope item verified still untouched** — you didn't quietly build or break one.
3. **Every Edge / Empty / Error row exercised**, not merely coded — each was triggered and observed.
4. **Cross-surface consistency:** no other surface shows a different value for the same fact (the
   dashboard, the detail view, and the report agree because they read one computation).
5. **Machine-checkable ACs have a test** committed in the same change.
6. **No new façade.** If any part is stubbed, it is labeled an explicit, time-boxed **spike** with an
   expiry, called out in Notes — and the story is **not** `Done ✓`. Façade is never a done state.

The AC checklist therefore looks like this when done:

```markdown
- [x] AC2 — report outputs ledger columns only.
      ✓ Verified: ran report for 2026-06 on austin-isd → CSV header = Posted Date,Segment1..4,Debit,
        Credit,Transaction Number,Description; grep confirmed no STATUS/LEDGER_ID/... columns present.
        Test: tests/test_oracle_fbdi.py::test_no_constant_columns.
```

A bare `- [x]` with no evidence note is treated as **not done** in review.

---

## Annotated micro-example (the shape, in miniature)

> **Story:** Export learner list as CSV · 3 pts · Persona: CN Director · Depends on: roster API
> (`/api/roster`).
> **In scope:** a "Download CSV" button on the district roster; one row per learner.
> **Out of scope:** XLSX; scheduled delivery; columns beyond the five below.
> **Req 1.1:** columns, in order — `Name, Role, Site, Status, Last active`. **1.2:** `Status` uses the
> exact roster labels (`Complete / In progress / Not started / Overdue`), not derived strings.
> **Edge:** empty roster → file with header row only. Name with a comma → field is quoted.
> **Default:** filename `roster-<district-id>-<YYYY-MM-DD>.csv`; UTF-8.
> **AC1:** *Given* austin-isd has 28 learners, *When* the director clicks Download CSV, *Then* the
> file has 29 lines (1 header + 28) and line 1 is exactly `Name,Role,Site,Status,Last active`.
> **AC2:** *Given* a learner named `Garcia, Jr.`, *When* exported, *Then* that field renders as
> `"Garcia, Jr."` (quoted) and the row still has 5 fields.
> **Future option:** XLSX + scheduled email — additive; the CSV builder is reused, nothing rebuilt.

A reference story written to full fidelity lives at
`learning-agent/docs/features/real-overdue-deadlines/STORY-001-bind-deadline-to-overdue.md`.
