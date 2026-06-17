# Cashier Training Studio — self-contained share file

**Deliverable:** [`cashier-training-studio.html`](cashier-training-studio.html) — one file, no server.
Send it to the trainer; she opens it in any browser (double-click works). All her work is
saved in the browser (localStorage); nothing is sent anywhere.

## What it is
It is the **real Learning Studio app** (`static/index.html`, verbatim) with the backend
replaced by an in-page shim. The look, the learner course player, the track/quiz builders,
the certificate flow — all the real UI. Two things are changed for this share:

1. **District management is removed** (cashier-only scope).
2. **It opens on the learner view** so the trainer immediately sees what a cashier sees.
   Use the **Trainer / Customer** toggle in the top chrome to switch to the build side.

## What's seeded (all real content from the live system)
- **Track "Cashier Onboarding — Point of Sale & Food Safety"** with 3 gated chapters.
- **Webinars as the primary content** (step 1 of chapters 1 & 3) — your two GoToWebinar
  recordings, link-out (registration pages can't be embedded). The quizzes are framed as
  *supplemental*.
- **Real ICN/USDA hand-hygiene video** (embedded), **real POS cashier quiz** (8 Qs, all
  formats: multiple-choice, true/false, fill-in-blank, ordering), **real food-safety quiz**.
- **Chapter gating**: a learner can't skip ahead — each step unlocks the next, and the
  final **certificate is blocked until the track assessment is passed**.

The trainer can build her own variety from scratch in the **Trainer → Create / Library**
side (track builder, quiz builder with all formats); everything persists and previews live.

## Rebuild (when the source content or app changes)
```
# 1. start the real backend (so we can capture real content)        → :8001
python demo_app.py
# 2. capture real API responses
python share/_capture/capture_api.py
# 3. assemble the share file
python share/build_share.py        # → share/cashier-training-studio.html
```
- `_shim/shim_head.js` — the fetch shim (Block A): serves `/api`, `/resources`, `/api/icn`
  from a baked seed + localStorage; injected at the top of the app script.
- `_shim/shim_tail.js` — the UI layer (Block B): removes district mgmt, adds sequential
  gating, lands on the learner view; injected at the bottom of the app script.
- `build_share.py` — assembles the seed and injects both blocks into a copy of the app.

## Known limits (by design, for a shareable single file)
- The **webinar links and the ICN video need internet** (they open / embed from
  GoToWebinar / YouTube). Everything else works fully offline.
- **PDF export** of guides is disabled (no server to render PDFs).
- Brand fonts load from the web when online; otherwise the browser falls back gracefully.

---

# District / Customer Studio — self-contained share file (admin + learner)

**Deliverable:** [`district-admin-studio.html`](district-admin-studio.html) — one file, no server.
Send it to the training team; they open it in any browser (double-click works). It is the
**district customer's whole view** of the product — *both* halves, switchable with the
**"Previewing as"** selector in the top chrome:
- **CN Director → My Team** — the district training-supervisor / **admin** view.
- **Cashier → Learn** — the **learner** view (gated lessons, quizzes, gated certificate).

It opens on the CN Director (My Team) by default; flip "Previewing as" to **Cashier** for the
learner experience. (In the real app, "customer view" *is* exactly this role switch — this file
reproduces it faithfully.)

## What it is
The **real Learning Studio app** (`static/index.html`, verbatim) with the backend replaced by
an in-page shim. The shim is **persona-aware**: `/api/tracks`, `/api/roster`, What's-new etc.
are served per persona, so the CN Director sees the district roster and the Cashier sees the
real onboarding track — no cross-persona bleed. It reuses the cashier studio's interactive
backend (so the learner half is fully real: scoring, sequential gating, gated cert) and layers
in the CN Director's captured roster + assigned track (so the admin half is fully real).
This is **not a hand-built mockup** — it is the production UI on cached content.

## What's seeded (all REAL, captured from the live backend)
- **Admin (dana-director):** Houston ISD + its **28-person roster** (`/api/roster`,
  `/api/roster/<track>`), the director's assigned track **Manager Essentials**, the
  **141-module catalog**, regulatory dates.
- **Learner (john-cashier):** the **Cashier Onboarding — Point of Sale & Food Safety** track
  (2 GoToWebinar recordings, real ICN/USDA hand-hygiene video, real POS + food-safety quizzes,
  assessment-gated certificate).
- Writes (nudge / assign / lesson progress / quiz attempts) score or **honestly acknowledge**
  ("Reminder logged … delivery requires live roster sync (offline preview)") — never a fake
  "sent". Progress persists to localStorage; reset via `window.__dasReset()`.

## Rebuild (when source content or the app changes)
```
# 1. start the real backend (so we can capture real content)        → :8001
python demo_app.py
# 2. capture real API responses — learner (cashier) AND CN Director personas
python share/_capture/capture_api.py
python share/_capture/capture_director.py
# 3. assemble the unified share file
python share/build_share_studio.py       # → share/district-admin-studio.html
```
- `_shim/shim_head.js` — Block A: the interactive backend shim (cashier studio's); the studio
  build patches it for multi-track + the director's persona-aware roster routes.
- `_shim/shim_tail_studio.js` — Block B: boots customer + CN Director, dismisses the simulated
  sign-in, lands on My Team, and adds sequential gating to the learner player.
- `build_share_studio.py` — reuses `build_share.build_seed()` (cashier) + the director captures,
  patches the shim, and injects both blocks.
- *(Legacy, superseded by the studio build: `build_share_director.py` + `shim_head_director.js`
  + `shim_tail_director.js` — an admin-only replay build kept for reference.)*

## Known limits (by design)
- **Compliance-report PDF**, full **guide bodies**, webinar links and the ICN video are
  server-/internet-rendered, so they link out or show an "not available in the offline preview"
  page. Everything else works fully offline.
- My Team renders the live per-track roster (`renderMyTeamE1`); the real app shows a static
  "DEMO DATA" section header above the live body — a pre-existing real-app cosmetic quirk,
  not introduced by this build.
