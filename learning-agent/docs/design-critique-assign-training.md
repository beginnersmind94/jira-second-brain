# UX Critique: "Assign training" slide-over
**Surface:** Trainer view — Assign training (Aldine ISD slide-over)  
**Primary persona:** Jaime's Implementation / CS team  
**Stage assumed:** Refinement mockup (correct if this is Dana's customer-side "My Team" assign — verdict shifts)  
**Date:** 2026-06-16

---

## Does it do the job? (Layer 1)

**[Observation]** Purpose is legible: "Assign training — Aldine ISD" + a single green primary CTA. No competing action. Fine.

**[Inference] Ceremony mismatched to the persona.** The panel exposes four configuration concepts at once — role targeting, a fixed due date, "Dynamic," and "Drip" — plus the auto-enroll/inheritance footer. This user "just wants to be told what to do" and "half of them don't even know what LMS stands for" (Dallas, Jun-04 [28:09], [38:36]). "Drip — release one track per week" and "Dynamic — 7 days from when each learner joins" are delivery-LMS jargon. This is a Layer-1 fit problem against the target user, not styling.

**[Observation] No blast-radius count.** "Cashier across all of Aldine ISD's sites" conveys scope but not numbers. "Assign to ~6 cashiers across 4 sites" is the difference between confidence and a fat-fingered over-assign.

**[Inference] Provenance not visible at the point content crosses to a customer.** CONTENT shows "(published)" but no origin badge (AI-grounded · human-authored · ICN link-out) and no preview. The hard approval gate is upstream, but the assign panel is the moment approved content crosses to a district — per the JTBD trust rule (*"escalate any trust/provenance regression one level over what its visual impact suggests — it's a one-way door"*), this is **🔴 Blocker**, not Serious. The trust bar does not have an "unless the gate was earlier" carve-out.

---

## Findings

| Finding | Type | Severity | Fix |
|---|---|---|---|
| **Deadline model is contradictory.** A fixed DUE DATE field *and* a "Dynamic (relative to join)" checkbox are two incompatible deadline models with no mutual exclusion. Check Dynamic with a date set → which wins is undefined. This corrupts per-learner due dates and is expensive to unwind once a district is enrolled. | obs | 🔴 | Collapse to a single deadline control — radio: "Fixed date" vs "Relative to join (7 days)" — defaulting to go-live (Jun 30) so the common case requires no input. |
| **No origin badge on CONTENT.** Assigning is where content crosses to a live district. Show AI-grounded / human-authored / ICN link-out provenance inline on the CONTENT row. | inf | 🔴 | Add origin badge to the CONTENT row; add "Preview" link alongside it. |
| **"Drip" no-ops on a single track.** CONTENT is one Track; "release one track per week" needs multiple. Either the field is secretly multi-select, or Drip is a dead toggle implying a capability the form doesn't offer. | inf | 🟠 | Hide Drip unless CONTENT holds ≥2 tracks, or make CONTENT explicitly multi-select. |
| **No enrollment count / confirmation before commit.** "Auto-enrolls matching learners" with no N and no summary before the final action. | obs | 🟠 | Show live count next to the role dropdown; add a one-line confirm: content · audience · count · deadline. |
| **No preview of what's being pushed.** Can't see the approved content before deploying it to a customer. | inf | 🟠 | "Preview" link on the CONTENT row (combined fix with origin badge above). |
| **"Awaiting your review" / approval queues must not surface here.** If any future version of this panel surfaces a review or approval action to Jaime, that's a wrong-persona assignment — POs are the approval gate; Jaime is downstream. She sees what's been approved and assigns it. Name this as a build guard now rather than fixing it after it ships. | inf | 🟠 | Confirm no approval affordance exists in this panel or its loading states; add a product note blocking it from future iteration. |
| **Screen-share chrome absent.** This is a panel Jaime's team would demo to a district contact. If the screen has no unambiguous Trainer-mode indicator (the Customer-view banner is a named safety fix in the build), she can inadvertently share internal chrome with a customer. | obs | 🟠 | Confirm the assign slide-over is inside the Trainer chrome boundary. If it can be opened in a shareable state, add a visible "Internal — Trainer view" indicator. |
| **Empty / error states unaccounted.** Static frame doesn't show: no published content available; due date in the past; the Dynamic + fixed conflict. | assumption | 🟡 | Define these; the past-date and conflict cases need inline validation, not post-submit errors. |

---

## Accessibility (Layer 4)

- **Contrast — needs a pass.** Helper text and the "Auto-enrolls…" footer are light gray on white — likely below the 4.5:1 AA floor for normal text (WCAG 2.2 SC 1.4.3). The white-on-green button label is borderline at mid-green and should be measured. Can't confirm exact ratios from a mockup.
- **Targets:** native checkboxes look small; flag if this panel is ever used on a tablet (WCAG 2.2 SC 2.5.8 — 24×24px minimum). The Trainer surface isn't bound by the learner's 375px NFR, so not applying that here.
- **Color-only meaning:** none in the panel — "(published)" is text. Good.

---

## The vision fork

This panel promises real delivery-LMS plumbing: role-based auto-enroll, per-learner relative deadlines, "future joiners inherit it while active." That is Matt's BRD MVP (roster sync, multi-tenant persistence) — tagged **façade** in `FEATURES.md`. **Demo-ready and on-narrative (Dallas ✓), but if claimed as production-ready, it presents façade rostering and persistence as real (Matt ✗).** Decide which frame this screen is making a promise in before it's shown as "built."

---

## Load-bearing strength — don't break this

**"Everyone in this role across all of Aldine ISD's sites."** This scope line is the only blast-radius signal on the screen. Any redesign that collapses it to just the dropdown value removes the one protection a non-technical user has against a silent over-assign. Keep it — and add the count.

---

## Fix first

**Collapse the deadline into one unambiguous control with a go-live default.** Highest impact ÷ effort: kills a real logic defect (conflicting inputs → wrong due dates), removes a chunk of the ceremony mismatch for Jaime's team, and the wrong-due-date failure is expensive to reverse across a live district.

**Next action:** convert DUE DATE + Dynamic into a radio — "Fixed (default Jun 30 / go-live)" vs "Relative to join."  
**Kill criteria:** if engineering says deadline type can't be a single enforced field this cycle, ship with the date field only and defer Dynamic to V2 rather than shipping the ambiguous pair.  
**Revisit:** at the next assign-flow review or first real Implementation-team usability session, whichever is first.

---

## References

- W3C. (2023). *Web Content Accessibility Guidelines (WCAG) 2.2*. https://www.w3.org/TR/WCAG22/ (SC 1.4.3 contrast; SC 2.5.8 target size)
- Walter, J. (2022). *How to develop product sense.* Lenny's Newsletter.
- Nielsen Norman Group. (1994/ongoing). *10 usability heuristics for user interface design.* https://www.nngroup.com/articles/ten-usability-heuristics/
- Learning Studio JTBD context pack (personas, trust bar, vision fork; attributes quotes to BRD §4/FR-RP, May-26 and Jun-04 calls). Persona/stage mapping is an inference from the visible nav and breadcrumb — confirm before relying on it.
