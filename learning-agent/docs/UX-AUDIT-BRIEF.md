# Learning Studio — Full UX & Correctness Audit Brief

**Purpose:** a complete, repeatable audit of the Learning Studio demo — not a leftover-name
hunt. Run it in a clean context (a fork) the day before a stakeholder demo, or any time the
build has drifted.

**Pair with:** the `learning-studio-jtbd` skill (personas, JTBD, the trust bar, the
Dallas/Matt/Jaime lenses) + `design:design-critique` + `design:accessibility-review`.

## How to run
1. Load `learning-studio-jtbd` first so every finding is judged against the real user + job.
2. Start the app: `python demo_app.py` (Windows Proactor loop, port **8001**). **Drive it live**
   (preview tools / browser) — walk each surface in **both** Trainer and Customer view. Do not
   audit from source alone; render + click every state.
3. For each surface, score **all eight dimensions (A–H)** below and record findings.
4. Synthesize: one prioritized fix list + a **Demo-day blockers** callout + a single **fix-first**.
5. Severity = **impact × reversibility** (one-way doors rank higher). **Escalate one level** any
   trust, identity, or scope regression — those are the failure classes that have actually shipped here.

## Surfaces to walk (every view, both personas)
- **Trainer:** Home / day-view · Create (upload → generate → approve) · Library → **Studio** ·
  Library → **Catalog** · **Content Library** (track-builder module pool) · **Districts**
  (portfolio → one district → roster) · **Assignment** modal · **Tracks/Courses builder** ·
  **Quality** · **How it works**.
- **Customer:** **Catalog** · **Learn** (Track → Course → Lesson; the "Viewing as <role>"
  selector) · **My Team** · the **certificate**.

## Audit dimensions (score each surface A–H)
- **A. Does it do the job? (JTBD / Layer 1).** Who is viewing, what is their job-to-be-done, and
  does the screen deliver it faster/clearer than today? Is the single primary action obvious?
- **B. Trust / grounding legibility (the moat).** Provenance/origin badges present (AI-grounded ·
  human-authored · ICN/outside-vendor); per-claim source reachable; "✓ every claim cited"; the
  approval gate is visible and human-only; no path lets an un-cited product claim onto a screen;
  ICN is link-out + credited; the guarantee is **not over-claimed** on imported/ICN content.
- **C. Seam integrity (does it actually work end-to-end, not just render).** build → assign →
  learn; generate → approve → module; transcript/roster import → downstream use. What **persists**
  (disk) vs **resets** (in-memory) on reload/restart? Is anything **façade presented as real**
  without a tag?
- **D. Scope consistency (V1 = single-district customer).** No multi-tenant / state→district
  artifacts anywhere a customer or assignment surface can reach. Every label, option, and axis
  matches V1. No control implies unbuilt scope.
- **E. Identity & label correctness (the recurring failure class).** Every label matches **who is
  actually viewing**: no showing the logged-in user their own name; no persona-name collisions; no
  stale names; demo/seeded data honestly tagged; counts/roles correct for the viewer.
- **F. Friction & failure states (Layers 2–3).** Empty / first-run, error, loading/latency, edge
  data (long names, zero/negative, huge lists, missing fields), permission / partial access. Which
  states are unaccounted for? (Listing an unhandled state is itself a finding.)
- **G. Accessibility (Layer 4 — CONTRACTUAL per BRD §6, not optional).** WCAG 2.1 AA contrast
  (text 4.5:1, large/UI 3:1); target size (AA ≥24px; platform 44/48); **no color-only meaning**
  (status/required/error need text or icon); visible focus + sane tab order; **mobile usable to
  375px** ("cafeteria staff don't sit at desks"); course player **< 3s** load. Cite the FR/NFR id.
- **H. Consistency & polish (Layer 5).** Design-system consistency; the **three-names problem**
  (Studio / Catalog / Content Library — same noun, different things); redundant filters; the
  **Source filter vs Origin badge** vocabulary mismatch; spacing/type scale.

## Known-good decisions — DO NOT flag as bugs (feed these to the auditor)
- `search_kb` is **live but a navigation cross-check**, not a citation source — citations stay
  Jira/transcript verbatim spans. Generated guides not quoting your guides is **correct**.
- Imported Cybersoft guides + ICN are **delivered as-is**, not AI-rewritten; ICN is **link-out +
  credited** by fair-use policy. "The AI didn't rewrite my guide" is by design, not a gap.
- **Façade** rows that are clearly tagged demo/seeded are intentional; flag only if presented as
  real **without** a tag (that's a Dimension-C honesty finding).
- A **trainer serving multiple district clients** (Sam Rivera → Houston/Aldine/Klein) is legitimate
  (the trainer's book of business). That is **not** the state→district multi-tenant model — which
  IS out of scope and **should** be flagged if it leaks into a customer or assignment surface.
- **Per-learner identity** (log in as John the cashier) is deferred; **"Viewing as <role>"** is the
  V1 stand-in. Flag only if a screen claims real per-person identity (e.g. a cert with a real name).

## Output format
1. **Per-surface findings table:** `Finding · Dimension (A–H) · obs/inf/assumption · Severity (🔴/🟠/🟡) · Fix (the *what*)`.
2. **Prioritized fix list** — top to bottom by impact ÷ effort.
3. **Demo-day blockers** — anything that would break or embarrass in front of Jaime / Dallas / Matt.
4. **Fix-first** — the single highest-impact, least-reversible change. Name exactly one.

## Recurring failure mode — hunt its siblings explicitly
Leftover labels/scope/identity that don't match who's actually looking. Found + fixed so far:
- Persona-name collision (Dana = trainer **and** CN Director).
- Multi-tenant assign axes ("Entire organization" / "By district") when the customer **is** the district.
- Logged-in user shown their own name (Districts header).

These are symptoms of one disease: **demo/scope-creep leftovers**. Sweep every surface for more —
any label, count, option, default, or hierarchy that assumes the wrong viewer or unbuilt scope.
