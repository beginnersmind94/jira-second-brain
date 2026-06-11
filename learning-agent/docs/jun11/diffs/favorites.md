# Favorites / bookmark — apply-ready diff spec

**Target file:** `learning-agent/static/index.html` (3,501 lines as read this session; the GROUND-TRUTH "3327 lines" was an earlier count — verify line numbers against the live file before applying, they drift if other Jun-11 diffs land first).
**Feature:** A star toggle on each Library resource card + a "My guides" filter, persisted in `localStorage` (no backend).
**Scope of the cards:** the **internal Library** (`<section id="view-library">`, `.lib-card` cards rendered by `loadLibrary()`), NOT the ICN Content library (`#view-content`, `.icn-card`). See "Why the internal Library" below.

> **DO NOT EDIT `index.html` from this spec.** This document only describes the diff. Apply it as a separate, reviewed change.

---

## Grounding note (read first — honesty about sourcing)

- **No transcript supports this feature.** The 15 files in `learning-agent/raw/transcripts/` are *product training recordings* (e.g. Sarah Chen teaching Item Management to the Brunswick County cohort — `20260605-104917-financials-…md:1-9`, "Recording ID: REC-2026-0515-IM-001"). None of them is a stakeholder/roadmap meeting, and none mentions favorites, bookmarks, "My guides," saved guides, or Library UX. I searched all transcripts for `favorit|favourite|bookmark|star|my guides|save this|come back to|find it again` — the only hits were incidental matches on the word "library"/"customer" in passing, not feature requests.
- **There were no separate "two meeting transcripts" to cite.** The task framing references a meeting; I could not find a meeting transcript in the repo, so I am not inventing `[MM:SS]` citations for it. If those transcripts exist outside the repo, the demand-side justification for this feature should be cited from them at apply time — this spec deliberately leaves that blank rather than fabricate it.
- **The feature's status as net-new is grounded in the task's GROUND-TRUTH block** ("GAP: no favorites/bookmark"), confirmed against code: a full-file search of `index.html` for `favorit|favourite|bookmark|★|☆|My guides|saved` returned **zero matches**. So this is genuinely additive — nothing to refactor.
- **`localStorage` is currently unused** in `index.html` (only `sessionStorage` for the demo-login gate at `index.html:3158` and `:3165`). So introducing a `localStorage` key collides with nothing.

---

## Why the internal Library (`#view-library`), not the ICN Content tab

The task says "the customer Library." Two libraries exist:

1. **Internal Library** — `<section id="view-library">` (`index.html:1512`), filter panel at `:1514-1549`, cards rendered as `.lib-card` in `loadLibrary()` (`:3272-3358`). This is the one with resource cards keyed by `r.id` (`card.dataset.id = r.id`, `:3330`) and the approve/publish workflow.
2. **ICN Content library** — `<section id="view-content">` (`:1575`), cards are `.icn-card` in `#icn-grid`, externally-authored ICN/USDA assets.

The task pins this to the internal Library explicitly: it names `setViewMode`, "resource cards," and the `lib-card` cards. The Library tab stays visible to customers — `applyViewMode()` (`:1818-1835`) hides only `tab-author` and `tab-evals` for `_viewMode === 'customer'`; it never hides `tab-library` (the nav button at `:1353`). So a customer in customer-view sees the Library tab and its cards. That is where "My guides" belongs.

> **Demo caveat to flag to stakeholders, not a blocker for this diff:** per GROUND-TRUTH the *published* Library is currently empty (0 approved guides). The default Status filter is "In Library (approved)" (`index.html:1532`), so with 0 approved guides the grid is empty and there is nothing to star. For the demo, either (a) approve ≥1 guide first (the lead is handling the empty-library gap separately), or (b) switch the Status filter to "All" / "Awaiting review" so cards render. Favorites works identically regardless of status — it keys off `r.id`, not approval state.

---

## Design summary

- **Persistence:** one `localStorage` key, `ls_fav_resources`, holding a JSON array of resource ids (`r.id` strings). Helpers `getFavs()` / `isFav(id)` / `toggleFav(id)`. All wrapped in `try/catch` (private-mode / disabled-storage safe), mirroring the existing `sessionStorage` try/catch style at `:3158`.
- **Star toggle:** a `<button class="fav-star">` absolutely positioned top-right inside each `.lib-card`. Click toggles favorite and `stopPropagation()`s so it does **not** trigger `selectLibResource(r)` (the card's own click handler at `:3355`). `aria-pressed` reflects state; keyboard-focusable.
- **"My guides" filter:** a checkbox/toggle in the filter panel. When on, `loadLibrary()` filters the list to favorited ids. State is itself persisted (`ls_fav_filter_on`) so the demo can deep-link into "My guides."
- **No backend:** no new route. `loadLibrary()` already does all filtering client-side (status `:3304-3306`, search `:3308-3310`, sort `:3311-3320`); the favorites filter slots into that same pipeline.

---

## DIFF 1 — CSS for the star + "My guides" toggle

**Anchor (find this — `index.html:802`, the last `.lib-card` rule):**

```css
    .lib-card .row span:last-child { margin-left: auto; font-family: var(--mono); }
```

**Insert immediately AFTER line 802** (new block; uses only existing design tokens):

```css

    /* ── Favorites: star toggle on each card ── */
    /* Card title must not run under the star (card padding is 15px right; star sits in the corner). */
    .lib-card .title { padding-right: 26px; }
    .fav-star {
      position: absolute;
      top: 10px;
      right: 10px;
      z-index: 2;                 /* above the card; card has no other abs children but the ::before rail */
      display: inline-grid;
      place-items: center;
      width: 26px;
      height: 26px;
      padding: 0;
      border: 0;
      border-radius: var(--radius-sm);
      background: transparent;
      color: var(--muted-soft);   /* hollow star = not-favorited (decorative stroke tone) */
      cursor: pointer;
      line-height: 0;
      transition: color .14s ease, background .14s ease, transform .12s ease;
    }
    .fav-star:hover { background: var(--accent-soft); color: var(--accent); transform: scale(1.08); }
    .fav-star svg { width: 16px; height: 16px; display: block; }
    .fav-star[aria-pressed="true"] { color: var(--accent); }
    .fav-star[aria-pressed="true"] svg { fill: var(--accent); stroke: var(--accent); }
    .fav-star:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

    /* ── "My guides" filter row in the Library filter panel ── */
    .lib-fav-filter {
      display: flex;
      align-items: center;
      gap: 9px;
      margin: 0 0 18px;
      padding: 10px 12px;
      background: var(--surface);
      border: 1px solid var(--border-strong);
      border-radius: var(--radius-sm);
      cursor: pointer;
      user-select: none;
      font-size: 13px;
      font-weight: 650;
      color: var(--text-soft);
    }
    .lib-fav-filter input { width: 16px; height: 16px; accent-color: var(--accent); cursor: pointer; }
    .lib-fav-filter .fav-count { margin-left: auto; font-family: var(--mono); font-size: 11px; color: var(--muted); }
```

**Notes:**
- The `.fav-star` reduced-motion behavior is already covered defensively: the global `prefers-reduced-motion` block (`:998-1005`) doesn't touch `.fav-star`, but the only motion here is a `:hover`/`:focus` `transform: scale`, which is acceptable under reduced-motion guidance (it's user-initiated, not autoplaying). If you want to be strict, add `.fav-star { transition: none; }` inside that block — optional, not required.
- `--muted-soft` (`:26`) is documented "DECORATIVE ONLY (dots, icon strokes)" — a hollow star icon stroke is exactly that use, so this is on-spec for the design system.
- The `:focus-visible` rule is redundant with the global focus ring at `:926-933` (which already lists buttons) but is kept explicit so the star's rounded outline matches its small size.

---

## DIFF 2 — Star markup inside each rendered card

**Anchor (find this — `index.html:3346-3354`, the `card.innerHTML` template in `loadLibrary()`):**

```js
    card.innerHTML = `
      <p class="title">${libTypeIcon(r.template)}${r.module || '?'} | ${r.template || '?'}</p>
      <p class="lib-src">↳ ${srcLine}</p>
      <div class="row">
        <span class="badge ${sb.cls}" title="${escAttr(sb.tip)}">${sb.label}</span>
        <span class="badge ${evalClass}" title="${escAttr(evalTitle)}">${evalLabel}</span>
        <span>${(r.created_at || '').slice(0, 16).replace('T', ' ')}</span>
      </div>
    `;
```

**Replace with** (adds the star as the first child of the card; everything else byte-for-byte unchanged):

```js
    const favOn = isFav(r.id);
    card.innerHTML = `
      <button class="fav-star" type="button" aria-pressed="${favOn}"
              title="${favOn ? 'Remove from My guides' : 'Save to My guides'}"
              aria-label="${favOn ? 'Remove from My guides' : 'Save to My guides'}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
      </button>
      <p class="title">${libTypeIcon(r.template)}${r.module || '?'} | ${r.template || '?'}</p>
      <p class="lib-src">↳ ${srcLine}</p>
      <div class="row">
        <span class="badge ${sb.cls}" title="${escAttr(sb.tip)}">${sb.label}</span>
        <span class="badge ${evalClass}" title="${escAttr(evalTitle)}">${evalLabel}</span>
        <span>${(r.created_at || '').slice(0, 16).replace('T', ' ')}</span>
      </div>
    `;
```

**Then, immediately AFTER the existing card click wiring (find this — `index.html:3355`):**

```js
    card.addEventListener('click', () => selectLibResource(r));
```

**Insert immediately AFTER line 3355:**

```js
    const star = card.querySelector('.fav-star');
    if (star) star.addEventListener('click', (e) => {
      e.stopPropagation();              // do NOT open/select the card
      const nowFav = toggleFav(r.id);
      star.setAttribute('aria-pressed', String(nowFav));
      const lbl = nowFav ? 'Remove from My guides' : 'Save to My guides';
      star.title = lbl; star.setAttribute('aria-label', lbl);
      updateFavCount();
      // If "My guides" is active and we just un-favorited, drop the card from view.
      if (favFilterOn() && !nowFav) loadLibrary();
    });
```

**Why `stopPropagation` is mandatory:** the card itself has a click handler (`:3355`) that calls `selectLibResource(r)` (`:3387`), which fetches `/resources/{id}` and swaps the preview pane. Without `stopPropagation`, clicking the star would also open the guide — wrong UX. The star is `z-index: 2` (DIFF 1) but z-index alone doesn't stop event bubbling; the JS guard is what prevents the card select.

---

## DIFF 3 — "My guides" toggle in the filter panel

**Anchor (find this — `index.html:1529-1536`, the Status `.field` in the Library filter panel):**

```html
      <div class="field">
        <label for="lib-status">Status</label>
        <select id="lib-status">
          <option value="library" selected>In Library (approved)</option>
          <option value="awaiting">Awaiting review</option>
          <option value="">All</option>
        </select>
      </div>
```

**Insert immediately AFTER that `</div>` (i.e. after line 1536), before the Sort `.field` at `:1537`:**

```html
      <label class="lib-fav-filter" for="lib-fav-only">
        <input type="checkbox" id="lib-fav-only" />
        <span>My guides</span>
        <span class="fav-count" id="lib-fav-count">0</span>
      </label>
```

This places "My guides" directly under the Status dropdown and above "Sort by" — a natural filter grouping. It is plain HTML inside the existing `.panel-body` (`:1516`), so it inherits the panel's layout with no extra wrapper.

---

## DIFF 4 — JS: persistence helpers + filter wiring

**Anchor (find this — `index.html:2895-2897`, the `inLibrary` helper at the top of the "Library" JS section):**

```js
function inLibrary(r) {
  return r.approved === true || r.status === 'approved' || r.status === 'published';
}
```

**Insert immediately AFTER line 2897** (new block — co-located with the other Library helpers):

```js

// ─── Favorites (client-only; localStorage, no backend) ─────────────
// One key holds an array of resource ids the user starred. Storage is wrapped
// in try/catch the same way the demo-login gate is (see sessionStorage at ~:3158),
// so private-mode / disabled-storage degrades to "nothing favorited" instead of throwing.
const FAV_KEY = 'ls_fav_resources';
const FAV_FILTER_KEY = 'ls_fav_filter_on';
function getFavs() {
  try { const v = JSON.parse(localStorage.getItem(FAV_KEY) || '[]'); return Array.isArray(v) ? v : []; }
  catch (e) { return []; }
}
function saveFavs(arr) {
  try { localStorage.setItem(FAV_KEY, JSON.stringify(arr)); } catch (e) {}
}
function isFav(id) { return getFavs().indexOf(id) !== -1; }
function toggleFav(id) {
  const arr = getFavs();
  const i = arr.indexOf(id);
  if (i === -1) arr.push(id); else arr.splice(i, 1);
  saveFavs(arr);
  return i === -1;            // true if it is now favorited
}
function favFilterOn() {
  const el = document.getElementById('lib-fav-only');
  return !!(el && el.checked);
}
function updateFavCount() {
  const el = document.getElementById('lib-fav-count');
  if (el) el.textContent = getFavs().length;
}
```

**Then wire the toggle's persistence + listener.** **Anchor (find this — `index.html:3360-3363`, the existing Library filter listeners):**

```js
['lib-module', 'lib-template', 'lib-status', 'lib-sort'].forEach(id => {
  document.getElementById(id).addEventListener('change', loadLibrary);
});
document.getElementById('lib-search').addEventListener('input', loadLibrary);
```

**Replace with** (adds `lib-fav-only` to the change-listener set + restores its persisted state + seeds the count):

```js
['lib-module', 'lib-template', 'lib-status', 'lib-sort', 'lib-fav-only'].forEach(id => {
  const el = document.getElementById(id);
  if (el) el.addEventListener('change', loadLibrary);
});
document.getElementById('lib-search').addEventListener('input', loadLibrary);
// Restore "My guides" toggle + count on load (persisted so the demo can deep-link into it).
(function initFavFilter() {
  const el = document.getElementById('lib-fav-only');
  if (el) {
    try { el.checked = localStorage.getItem(FAV_FILTER_KEY) === '1'; } catch (e) {}
    el.addEventListener('change', () => {
      try { localStorage.setItem(FAV_FILTER_KEY, el.checked ? '1' : '0'); } catch (e) {}
    });
  }
  updateFavCount();
})();
```

**Defensive note on the original `.forEach`:** the existing code (`:3360-3362`) calls `document.getElementById(id).addEventListener(...)` with no null-guard. That is safe today because all four ids exist in the static HTML. The replacement adds an `if (el)` guard so a future markup change can't throw — a free hardening, behavior-identical for the existing ids.

---

## DIFF 5 — JS: apply the favorites filter inside `loadLibrary()`

**Anchor (find this — `index.html:3304-3310`, the status filter + search filter inside `loadLibrary()`):**

```js
  // The Library proper shows only approved resources; the gate is human approval.
  if (view === 'library') list = list.filter(inLibrary);
  else if (view === 'awaiting') list = list.filter(r => !inLibrary(r));
  // client-side free-text search
  const q = (document.getElementById('lib-search').value || '').toLowerCase().trim();
  if (q) list = list.filter(x =>
    `${x.module || ''} ${x.template || ''} ${x.status || ''} ${x.id || ''}`.toLowerCase().includes(q));
```

**Insert the favorites filter between the status filter and the search filter — i.e. immediately AFTER line 3306** (`else if (view === 'awaiting') ...`) and before the `// client-side free-text search` comment:

```js
  // "My guides" — client-only favorites filter (localStorage). Applied after the
  // status filter so it intersects with whatever status view is selected.
  if (favFilterOn()) {
    const favs = getFavs();
    list = list.filter(r => favs.indexOf(r.id) !== -1);
  }
```

That is the entire data-path change. Sort (`:3311-3320`), count (`:3321`), and the empty-state ("No matching resources." `:3324`) all run downstream and need no edits — when "My guides" is on and nothing is starred, the existing empty-state already renders. The count badge `#lib-count` (`:3321`, `:1552`) will correctly read the favorited count.

> Optional polish (not required for apply): give the empty grid a favorites-specific message. If desired, change the empty-state at `:3323-3325` to branch on `favFilterOn()` ("You haven't saved any guides yet — tap the ☆ on a card."). Left out of the core diff to keep the change minimal and avoid touching unrelated copy.

---

## Manual test checklist (no automated tests exist for `index.html`)

1. Load app → Library tab → set Status to "All" (or approve a guide) so cards render.
2. Click a card's star → star fills terracotta, `aria-pressed="true"`, card does **not** open the preview.
3. Reload page → star is still filled (localStorage persisted).
4. Check "My guides" → grid filters to starred cards only; `#lib-fav-count` and `#lib-count` match.
5. Un-star a card while "My guides" is on → card disappears from the grid.
6. Reload with "My guides" checked → it stays checked and filtered.
7. Switch to Customer view (`setViewMode('customer')`) → Library tab still visible; stars + "My guides" work identically.
8. Keyboard: Tab to a star → terracotta focus ring; Enter/Space toggles it.
9. Private/incognito (storage may throw) → no console errors; favorites simply don't persist.
