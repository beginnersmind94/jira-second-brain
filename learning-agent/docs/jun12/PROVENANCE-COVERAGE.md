# F1 Provenance Coverage Matrix

**Wave:** 1 · **Item:** F1 — Provenance sweep: badges + "show source" on every content surface
**Last updated:** 2026-06-12 · **Re-run:** at the end of every wave (Wave 2 and Wave 3 checkpoints mandatory)

## What this document is for

Dallas narrates on stage: "See this badge? AI-grounded, every claim cited. This one's USDA — credited and linked." That narration must match what the screen shows. This matrix is the per-wave check that it does.

**Re-run instructions:** At the end of each wave, open the app in demo mode, walk through every surface below, and update the Status column. A surface is only ✓ if the correct badge is visible without any additional interaction (except "Show source", which is one click/tap).

---

## The three provenance classes

| Class | Badge CSS | Label | When to use |
|---|---|---|---|
| `ai_grounded` | `.origin-badge.ai-grounded` | ✓ AI-grounded | AI-generated guide that passed `validate_citations` — every claim is a verbatim-cited Jira span. **ONLY this class.** |
| `human_authored` | `.origin-badge.human-authored` | ✎ Human-authored | Imported Cybersoft/SchoolCafé guides; manually written content; free-text descriptions (DEC-3). |
| `outside_vendor` | `.origin-badge.outside-vendor` | ↗ USDA / ICN | ICN/USDA content. Embedded or linked — never reproduced. Source name shown in label. |

**Over-claiming is the only unforgivable error.** `ai-grounded` must NEVER appear on `human_authored` or `outside_vendor` content. The `originBadgeHtml()` function enforces this by construction — it maps origin values to classes, callers never write the badge text directly.

---

## Surface coverage matrix (Wave 1 baseline)

| Surface | Code location | Expected badge | "Show source" | Status |
|---|---|---|---|---|
| **Library card row** (AI-generated) | `renderLibraryDemo` → `_originBadge()` col | `human-authored` or `ai-grounded` via `_originBadge` (legacy `.og` classes) | — (in detail panel) | Partial — `.og` classes render, `origin-badge` not on row itself |
| **Library detail panel** (AI-generated) | `reviewDemoItem` | `origin-badge.ai-grounded` | "Show source" button when `rid` known | ✓ |
| **Library detail panel** (human-authored) | `reviewDemoItem` | `origin-badge.human-authored` | Absent | ✓ |
| **Catalog card** (AI-generated) | `renderCatalogDemo` cards | `origin-badge.ai-grounded` | — | ✓ |
| **Catalog card** (human-authored / Cybersoft guide) | `renderCatalogDemo` cards | `origin-badge.human-authored` | — | ✓ |
| **Catalog card** (ICN asset) | `renderCatalogDemo` cards | `origin-badge.outside-vendor` | — | ✓ |
| **Catalog detail drawer** (AI-generated) | `openCatalogDetail` | `origin-badge.ai-grounded` + "AI-grounded." note | "Show source" when `rid` known | ✓ |
| **Catalog detail drawer** (human-authored) | `openCatalogDetail` | `origin-badge.human-authored` + "Human-authored." note | Absent | ✓ |
| **Catalog detail drawer** (outside-vendor) | `openCatalogDetail` | `origin-badge.outside-vendor` + "Outside-vendor content." note | Absent | ✓ |
| **Track module list** (AI_TRANSCRIPT module) | `_renderRealTrack` rows | `origin-badge.ai-grounded` | "Show source" link | ✓ |
| **Track module list** (HUMAN_GUIDE module) | `_renderRealTrack` rows | `origin-badge.human-authored` | Absent | ✓ |
| **Track module list** (ICN_DOC module) | `_renderRealTrack` rows | `origin-badge.outside-vendor` | Absent | ✓ |
| **Track hero path-stats** (all-AI track) | `_renderRealTrack` header | `origin-badge.ai-grounded` | — | ✓ |
| **Track hero path-stats** (all-ICN track) | `_renderRealTrack` header | `origin-badge.outside-vendor` | — | ✓ |
| **Track hero path-stats** (mixed track) | `_renderRealTrack` header | "✓ sources credited" (no class badge) | — | ✓ |
| **ICN path detail** path-stats | `openPath` header | `origin-badge.outside-vendor` ("USDA / ICN") | — | ✓ |
| **ICN path aside** | `openPath` aside | Text: "externally authored … nothing … AI-generated" | — | ✓ |
| **Quiz taker** (gate-generated quiz) | `openTaker` kicker | `origin-badge.ai-grounded` | — | ✓ |
| **Quiz taker** (ICN quiz) | `openTaker` kicker | `origin-badge.outside-vendor` | — | ✓ |
| **Quiz taker** (manual questions) | `openTaker` kicker | `origin-badge.human-authored` | — | ✓ |
| **Quiz answer feedback** source quote | `takerSubmit` `.quiz-src` | Verbatim quote shown per question | — | Pre-existing |
| **Lesson player** (guide lesson) | `_renderLessonPlayer` | No badge on pane yet (D1 Wave 2) | — | Planned (Wave 2 D1) |
| **Course view** (demo track) | `openCourse` path-stats | "✓ sources cited & credited" text | — | Pending (Wave 2 D1) |
| **Track builder library pane** | `tbSrcBadge` → `.src-badge` | `.src-badge--ai` / `--guide` / `--icn` (legacy) | — | Pre-existing (tbSrcBadge kept as-is) |
| **Customer avatar menu** "every claim cited" | `applyViewMode` | Text gated on `_viewMode === 'customer'` | → opens howitworks | Pre-existing guard |
| **Customer banner** | `#customer-banner` | Persistent green band; cannot be dismissed | — | Pre-existing |

---

## Over-claiming audit (grep check, run each wave)

Run these greps against `static/index.html` before each wave sign-off. All must return zero hits on the **wrong** pairing.

```bash
# 1. "every claim cited" text must NOT appear unconditionally —
#    it is only valid in the kicker slot (gated by openTaker's quizOrigin logic)
#    or the customer avatar menu (gated by _viewMode === 'customer').
grep -n "every claim cited" learning-agent/static/index.html

# 2. ai-grounded CSS class must NOT appear in human-authored or outside-vendor branches.
#    Visually inspect each hit to confirm it is guarded by an origin check.
grep -n "ai-grounded" learning-agent/static/index.html

# 3. originBadgeHtml is the canonical emitter — no code should hard-code badge HTML.
grep -n "origin-badge" learning-agent/static/index.html | grep -v "originBadgeHtml\|\.origin-badge\|css\|style"
```

---

## Wave 2 checkpoint (Jun 28)

Add these rows when D1 (unified course player) and B1 (question types) merge:

| Surface | Expected badge | Note |
|---|---|---|
| Course player lesson pane (guide) | `origin-badge.ai-grounded` or `human-authored` | D1 work |
| Course player lesson pane (video) | `origin-badge.outside-vendor` | C1 attribution band separate |
| Course player lesson pane (quiz) | `origin-badge.ai-grounded` | From openTaker |
| Course player lesson pane (flashcards) | `origin-badge.ai-grounded` | B2 work |
| Scenario/exercise step | `origin-badge.ai-grounded` | B5 work (if shipped) |
| Assessment question card | `origin-badge.ai-grounded` | B3 work |
| Certificate | No badge needed — completion artifact, not content | — |

## Wave 3 checkpoint (Jul 5)

Add these rows when gamification and practice mode merge:

| Surface | Expected badge | Note |
|---|---|---|
| Practice card (flashcard) | `origin-badge.ai-grounded` | D4 work |
| Practice card (quiz question) | `origin-badge.ai-grounded` | D4 work |
| Streak / XP strip | No provenance badge — not content | — |
