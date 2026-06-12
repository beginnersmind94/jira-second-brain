# Demo Ops — Conference mode & generation theater

**Last updated:** 2026-06-12  
**For:** ANC July 13 booth operators (Dallas / Sam)

---

## 1. Starting in conference mode

```bash
# From learning-agent/ using the sibling .venv
DEMO_MODE=conference python demo_app.py
```

Or add to `.env` (never commit `.env` — the file is gitignored):
```
DEMO_MODE=conference
```

On startup you will see:
```
[demo_app] CONFERENCE MODE active — watermarks suppressed, reset endpoint enabled
[demo_app] Conference mode: pre-warm complete
```

**What changes in conference mode:**
- Compliance PDF and resource PDF are served without the "DEMO DATA" / "PENDING REVIEW" banners
- `POST /api/demo/reset` becomes available (403 in normal mode — cannot be called by accident)
- Boot pre-warm runs: library docs + ICN catalog are cached eagerly so first page load is instant
- Generation theater: if a pre-recorded trace exists for a resource, `/generate` replays it instead of calling the LLM
- `window._config.conferenceMode = true` is exposed in the browser for the operator reset UI

---

## 2. Pristine reset between booth visitors

**Keyboard chord (preferred — hands never leave the keyboard):**
1. Open the app in the browser
2. Navigate to `/?operator=1` (once per browser session — this reveals the "Reset demo" button)
3. Click "Reset demo" — shows a "Resetting…" toast, then reloads to John Cashier's view

**URL param mode (visible button):**
- Navigate to `http://localhost:8001/?operator=1` to reveal the floating "Reset demo" button

**API call (scripts / automated testing):**
```bash
curl -X POST http://localhost:8001/api/demo/reset
```

Response:
```json
{"ok": true, "reset_at": "2026-07-13T14:30:00", "users_reset": ["demo-user-001", "demo-user-002", "demo-user-003"], "elapsed_ms": 120}
```

**What reset does:**
1. Deletes all completion records and certificates for the 3 demo personas (john-cashier, dana-director, sam-trainer)
2. Deletes `data/leads/*.jsonl` (the booth lead log, written by G5)
3. Invalidates the in-memory library index (next `/api/library/ask` rescans fresh)
4. Must complete in under 10 seconds (functional requirement)

**What reset does NOT touch:**
- Real user records (any user whose id does not start with `demo-`)
- Approved guides, tracks, or the fixture data — content is untouched
- Server process — no restart needed

---

## 3. Generation theater (replay mode)

Live generation takes 2–4 minutes. For the "watch it build" stage moment, use a pre-recorded trace:

### Recording a trace
1. Run a live generation (`/generate?module=Item+Management&template=micro-guide&...`)
2. After generation completes, find the trace: `logs/<rid>.jsonl`
3. Copy it to `data/demo/generation-replay-<rid>.jsonl`

### How replay works
When `DEMO_MODE=conference` is set and `/generate` is called:
1. `demo_app.py` computes the resource id that the generation *would* produce (`prod._resource_id(module, template)`)
2. If `data/demo/generation-replay-<rid>.jsonl` exists, it streams the trace line-by-line instead of calling the LLM
3. Each event is emitted with an 80ms delay (configurable via `DEMO_REPLAY_DELAY_MS` env var)
4. If no replay file exists, falls through to a live LLM call — the system works honestly either way

### Narrating on stage
Honest framing: "We kicked off a generation at the top of the talk — this is the actual trace streaming back. The real thing is building in the background."

Never claim the replay is a live run — the `system` event `replaying_recorded_generation` is visible in the stream if anyone looks.

---

## 4. Operator reset UI — discovery prevention

The reset button is deliberately invisible to booth visitors:

- It does NOT appear in any navigation, menu, or visible control
- It is NOT reachable by tabbing through the normal UI
- The floating button only appears when `?operator=1` is in the URL
- The keyboard chord (triple-R on the hidden anchor) requires focus on an invisible element

A visitor browsing normally cannot stumble on it. The element has `aria-hidden="true"` so screen readers also skip it.

---

## 5. Booth reset checklist (between visitors)

1. Click "Reset demo" (or press the chord) — wait for the reload
2. Confirm John Cashier's Learn home shows 0% progress on "New Cashier Onboarding"
3. Confirm Dana's My Team shows John as "Not started"
4. Hand the device to the next visitor

Total reset time: under 10 seconds (server) + ~2 seconds page reload = ~12 seconds total.

---

## 6. Environment variables reference

| Variable | Default | Effect |
|---|---|---|
| `DEMO_MODE` | (unset) | Set to `conference` to enable presentation mode |
| `DEMO_REPLAY_DELAY_MS` | `80` | Milliseconds between replayed SSE events |
| `EXTERNAL_LEARNING` | `1` | Set to `0` to disable ICN catalog (if no Wi-Fi) |

**NEVER set `DEMO_MODE=conference` in a real district deployment.** This flag suppresses honest "demo data" labels that exist to prevent confusion between demo and real data.
