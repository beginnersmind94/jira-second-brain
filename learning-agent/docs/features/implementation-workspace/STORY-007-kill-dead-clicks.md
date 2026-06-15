# Story 007: Kill the legacy dead clicks (pre-pitch trust pass)

**Epic:** [Implementation Workspace](EPIC.md)
**Status:** Done ✓
**Points:** 3   ·   **Persona:** all (trust gate)   ·   **Depends on:** STORY-005 (activity feed)

## TL;DR
Removed the three fake/dead clicks on the demo path — the things that blow up a live pitch and, for a
trust-first product, "kill credibility instantly." Every control now does a real, honest thing.

## Scope
**In scope:** the staff-drawer "View progress" `alert()`; the help-request "Respond" fake `alert('Reply sent')`; the assignment people-picker that discarded identities. Also softened the two "Reminder sent" alerts to honest "logged" toasts.
**Out of scope:** a real outbound message/notification channel (doesn't exist; not claimed) — "Respond" records the response, it does not assert delivery.

## Requirements
1.1 Staff-drawer "View progress" → toggles a real inline progress detail (completion bar, status, last active) via `_ddToggleProgress`; no `alert()`.
1.2 `respondHelp` → `async`; POSTs a real note to the district workspace (lands in its activity feed), clears the help flag, re-renders, and shows an honest toast ("Response logged…") — never "Reply sent".
1.3 People-picker (`asnAudChange`) checkboxes carry `value="<name>"`; `asnSave` collects the actual selected names (array), not a count; `_asnAudLabel`/`_asnCount` read the array.

## Edge / Empty / Error states
| Case | Behavior |
|---|---|
| Respond POST fails | flag still clears, toast still shows (best-effort log; non-fatal) |
| No people selected | "Pick at least one person." (validates the array length) |
| `_showToast` unavailable | falls back to a plain (non-fake) message |

## Acceptance criteria
- [x] **AC1 — View progress is real.** *When* clicked, *Then* an inline detail reveals (hidden→shown, button → "Hide progress"); **no alert**.
      ✓ Live: `wasHidden:true → nowHidden:false`, btn "Hide progress", alert spy empty.
- [x] **AC2 — Respond is a real recorded action.** *When* responding to Aldine's help request, *Then* a note is persisted to its workspace (appears in activity), the flag clears, honest toast; **no "Reply sent"**.
      ✓ Live: Aldine activity gained the note; `helpCleared:true`; alert spy empty.
- [x] **AC3 — people-picker keeps identities.** *Then* each checkbox value = a learner name and the selection collects names, not a count.
      ✓ Live: 8 rendered, all valued, captured `["Maria Garcia","James Nguyen","Aisha Brown"]`.
- [x] **AC4 — no dead clicks on the demo path.** ✓ `window.alert` spied across all three flows → **0 calls**; console errors = none.

> **Done evidence:** verified live on :8011 (sam-trainer) with `window.alert` instrumented to catch any fake/dead click — none fired across View progress, Respond, and the people-picker. Mutated seed reset afterward.

## Notes
"Respond" records the response as a workspace note (body carries the text; activity shows a note event). A richer reply-thread / real delivery channel is a future feature, deliberately not faked here.
