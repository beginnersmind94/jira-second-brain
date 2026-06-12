# Learning Studio — Production Readiness Guide

**Audience:** A developer who has the demo running locally and wants to activate each integration point for a real deployment.

**Demo baseline:** `python demo_app.py` → http://127.0.0.1:8001, all env vars absent, all integrations in stub mode.

---

## Quick summary table

| Module | Demo (stub) behaviour | Production requirement | Env vars needed | Status |
|---|---|---|---|---|
| Identity / SSO | `X-Demo-User` header bypass; always resolves to a demo persona | Implement `_get_sso_user()` in `auth.py` to decode the SchoolCafé JWT / session cookie | None (code change) | **Code change required** |
| Multi-tenant isolation | API-layer `assert_district_access()` enforcement; seeded district list | Already enforced at API layer; no env var needed. District list comes from roster data once SSO lands | None | **Works as-is** |
| Completion persistence | Disk JSON under `data/completion/`; demo-seed fallback for `id.startswith("demo-")` | Disk backend works for single-node. Replace `CompletionStore` with Postgres/SQLite for multi-node | None (code change for multi-node) | **Works as-is (single-node)** |
| Roster sync + writeback | Seeded deterministic roster; writeback logged to `logs/writeback-stub.jsonl` | Set `SCHOOLCAFE_API_URL` + `SCHOOLCAFE_API_KEY` | `SCHOOLCAFE_API_URL`, `SCHOOLCAFE_API_KEY` | **Env vars activate** |
| xAPI / LRS | Statements appended to `logs/xapi-stub.jsonl` | Set `LRS_ENDPOINT` + `LRS_KEY` | `LRS_ENDPOINT`, `LRS_KEY` | **Env vars activate** |
| SCORM export | Works out of the box; no credentials required | No change needed — ready | None | **Ready** |
| Content generation | `claude` CLI subprocess (Anthropic API via claude auth) | Replace CLI subprocess with direct Anthropic API call per ADR-001 | `ANTHROPIC_API_KEY` (for direct API) | **CLI works for single-node; direct API for prod** |
| ICN content | Visible when `EXTERNAL_LEARNING=1` (default) | Set `EXTERNAL_LEARNING=0` until ICN fair-use agreement is signed | `EXTERNAL_LEARNING` | **Env var gates** |

---

## 1. Identity / SSO (`auth.py`)

### What the stub does

`get_current_user()` resolves identity in this order:

1. `_get_sso_user(request)` — always returns `None` today (stub).
2. `X-Demo-User` request header — maps to one of three demo personas (`john-cashier`, `dana-director`, `sam-trainer`).
3. `?demo_user=` query param — same lookup, for tools that can't set headers.
4. Default persona (`john-cashier`) — preserves existing demo behaviour.

All routes read identity exclusively through `get_current_user()`. No route is allowed to hardcode a user or district.

### What production requires

Implement `_get_sso_user(request: Request) -> CurrentUser | None` in `auth.py`. When a valid session is found, return a `CurrentUser`; when no session is present (unauthenticated), return `None`.

```python
def _get_sso_user(request: Request) -> CurrentUser | None:
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    # OR: token = request.cookies.get("session")
    if not token:
        return None
    claims = _validate_jwt(token, secret=JWT_SECRET, audience=JWT_AUDIENCE)
    return CurrentUser(
        id=claims["sub"],
        name=claims.get("name", ""),
        role=claims.get("role", "Cashier"),
        district_id=claims.get("district_id"),
        districts=claims.get("districts", []),
        is_trainer=claims.get("is_trainer", False),
    )
```

Key points:
- The JWT secret / JWKS endpoint is not yet wired — refer to ADR-001 §Auth for the agreed shape.
- `CurrentUser.id` must be a stable, unique identifier (UUID or product login id). This is the key used by `completion_store.py` and `roster_sync.py` — changing it mid-deployment orphans completion records.
- `CurrentUser.districts` is the Trainer's book of business (list of ISD ids). `CurrentUser.district_id` is the learner's home district.
- Once `_get_sso_user()` returns a real user, the demo bypass (`X-Demo-User`) is automatically ignored — the resolution order ensures SSO takes priority.

**Test:** Send `Authorization: Bearer <real JWT>` to `GET /api/tracks`; verify the response is scoped to the correct district and role.

---

## 2. Multi-tenant isolation (`tenancy.py`)

### Already architecture-enforced — no env var needed

Every district-scoped route calls `assert_district_access(user, isd)` before returning data. A cross-district read raises `HTTP 403` with `{"error": "district_access_denied"}`. This is enforced at the API layer, not by seed data — the guard is a list membership check against `CurrentUser.districts` / `CurrentUser.district_id`, both of which come from the identity layer.

```python
# Pattern used in every district-scoped route:
assert_district_access(current_user, requested_isd)
```

### What to verify before go-live

1. Audit every route in `demo_app.py` that accepts an `isd` parameter and confirm `assert_district_access()` is called before any data is read. The 18 test cases in `tests/test_tenancy.py` cover the known routes — run them: `python -m pytest tests/test_tenancy.py -v`.
2. Confirm that Trainer accounts (`is_trainer=True`) have `districts` populated by the SSO JWT, not hardcoded. A Trainer with an empty `districts` list will receive empty results on every district-scoped query.
3. The demo has 4 seeded districts (`houston-isd`, `dallas-isd`, `austin-isd`, `cy-fair-isd`). Production district IDs come from the roster API — they must match what the JWT claims carry. Mismatched IDs are the most likely production failure mode.

### Adding a new district-scoped route

Always call `assert_district_access(current_user, isd)` as the first line after extracting the `isd` parameter. See `tenancy.py` for the three public helpers: `assert_district_access`, `filter_to_accessible_districts`, `get_user_districts`.

---

## 3. Per-learner completion persistence (`completion_store.py`)

### What the stub does

Progress and certificate records are stored as JSON files under `data/completion/<user_id>/`:

```
data/completion/
  demo-user-001/
    track-20260610-abc123.json   ← progress record
    certs/
      cert-20260610-120000-ab1234.json
```

File writes are atomic on POSIX (write temp + rename). On Windows, writes are direct — acceptable for single-process demo use.

Demo-user fallback: when a user id starts with `"demo-"` and no progress record exists on disk, `get_progress()` seeds 40% completion so the UI shows meaningful data on first load. **This guard must be disabled in production.**

### Production path

**Single-node deployment:** The disk backend works as-is. No code changes needed. Ensure the `data/completion/` directory is on a persistent volume (not ephemeral container storage) and is writable by the server process.

**Multi-node / cloud deployment:** Replace `completion_store` with a database-backed implementation. The public interface (`get_progress`, `set_module_done`, `issue_certificate`, `get_certificate`, `get_all_progress`) is the contract — swap the storage backend without touching any callers.

Recommended: Postgres with a `completions` table indexed on `(user_id, track_id)` and a `certificates` table indexed on `cert_id`.

**Disable the demo-seed fallback:** In `completion_store.get_progress()`, the line:

```python
is_demo = user_id.startswith("demo-")
if is_demo and module_ids:
    return _demo_seed_for(track_id, module_ids)
```

...should be removed or gated behind an explicit `DEMO_MODE=1` env var. In production, a new learner with no progress should see 0% — not seeded 40%.

**Certificate scan:** `get_certificate(cert_id)` currently scans all user subdirectories (acceptable for tens of demo users). For production scale, add a flat `cert_id → user_id` index (a single lookup table or Redis key).

---

## 4. Roster sync + completion writeback (`roster_sync.py`)

### What the stub does

`RosterSyncClient` checks whether both `SCHOOLCAFE_API_URL` and `SCHOOLCAFE_API_KEY` are set. If either is absent, `is_stub` is `True`:

- `get_district_roster(isd)` returns deterministic seeded data (18–32 staff per district, same list on every call for a given ISD id).
- `sync_completion(...)` appends a JSONL record to `logs/writeback-stub.jsonl` and returns `True`.

### Activating production mode

Set both env vars in `.env`:

```
SCHOOLCAFE_API_URL=https://api.schoolcafe.com/v3
SCHOOLCAFE_API_KEY=sk-live-abc123
```

Once set, `RosterSyncClient.is_stub` becomes `False` and:

- `get_district_roster(isd)` calls `GET {SCHOOLCAFE_API_URL}/api/districts/{isd}/staff`, authenticated as `Authorization: Bearer {SCHOOLCAFE_API_KEY}`. The response must be a JSON array of staff objects, or a dict with a `"staff"` key.
- `sync_completion(...)` POSTs to `{SCHOOLCAFE_API_URL}/api/completions` with the same bearer auth.

**Verify it's live:** `GET /api/sync/status` returns:

```json
{"stub": false, "last_sync": "2026-06-12T14:00:00", "env_configured": true}
```

**Fallback behaviour:** Both methods are non-fatal. A network error or HTTP failure in `sync_completion` is logged and re-raised; the **caller in `demo_app.py` wraps it in a try/except and continues** — completion records are written to `completion_store` before the writeback call, so a failed writeback never loses local progress. A failed `get_district_roster` raises (callers should handle it).

**httpx dependency:** Production mode imports `httpx`. Ensure it is in `requirements.txt`:

```
httpx>=0.27
```

---

## 5. xAPI / LRS (`xapi_client.py`)

### What the stub does

`XAPIClient` checks `LRS_ENDPOINT` at instantiation. If absent, `stub` is `True` and all statements are appended to `logs/xapi-stub.jsonl` (JSONL format, one statement per line). The stub log is useful for verifying statement shape during development.

### Activating production mode

Add to `.env`:

```
LRS_ENDPOINT=https://lrs.example.com/xapi/statements
LRS_KEY=username:password
```

`LRS_KEY` formats accepted:
- `username:password` — HTTP Basic auth (base64-encoded).
- `Bearer eyJ...` — Bearer token (the prefix is passed as-is).
- Bare token (no colon, no `Bearer ` prefix) — treated as a bearer token.

**Verify it's live:** `GET /api/xapi/status` returns:

```json
{"stub": false, "lrs_configured": true}
```

### Statement shape (xAPI 1.0.3)

Two statement types are emitted:

**Track completed** (emitted when a certificate is issued):
```json
{
  "id": "<UUID v4>",
  "actor": {
    "objectType": "Agent",
    "name": "John Doe",
    "mbox": "mailto:jdoe@houstonisd.org"
  },
  "verb": {
    "id": "http://adlnet.gov/expapi/verbs/completed",
    "display": {"en-US": "completed"}
  },
  "object": {
    "objectType": "Activity",
    "id": "https://learning.cybersoft.net/tracks/<track-id>",
    "definition": {
      "type": "http://adlnet.gov/expapi/activities/course",
      "name": {"en-US": "New Cashier Onboarding"}
    }
  },
  "result": {
    "score": {"scaled": 1.0, "raw": 100.0, "min": 0.0, "max": 100.0},
    "completion": true,
    "success": true
  },
  "timestamp": "2026-06-12T14:00:00.000Z",
  "context": {
    "platform": "Learning Studio (Cybersoft)",
    "language": "en-US"
  }
}
```

**Module progressed** (emitted on module completion):
- Verb: `http://adlnet.gov/expapi/verbs/progressed`
- Object type: `http://adlnet.gov/expapi/activities/module`
- `context.contextActivities.parent` references the parent track.

**Actor IFI:** If the learner has no email, the actor uses an `account` IFI with `homePage: https://learning.cybersoft.net`.

**Non-fatal guarantee:** `emit_completed` and `emit_progressed` never raise. A failed POST logs a warning and returns `False`; cert issuance and progress updates are never blocked by an LRS outage.

---

## 6. SCORM export (`scorm_export.py`)

### No env vars needed — works out of the box

`GET /api/tracks/{id}/scorm` returns a SCORM 1.2 `.zip`. The "Export as SCORM" button is in the track builder actions card (Trainer view).

### What the package contains

```
<track-id>.zip
  imsmanifest.xml          ← SCORM 1.2-compliant manifest
  index.html               ← SCO launch page with SCORM API shim + nav
  content/
    <module-id>.html       ← one file per module (from published/ or drafts/)
  quiz/
    <module-id>.json       ← quiz JSON for modules that have a quiz (if present)
```

### Compatible LMS requirements

Any SCORM 1.2-compliant LMS (Moodle, Cornerstone, Blackboard, SCORM Cloud, etc.). The package sets `cmi.core.lesson_status = "completed"` and `cmi.core.score.raw = 100` when all modules are marked done, so an LMS that gates by score will not show a failure state.

### Known limitations

- **Single SCO:** All modules are served from one SCO launch page (`index.html`). Module-level SCORM tracking is handled via `postMessage` between the iframe content and the launch page — not via separate SCO items per module. Some enterprise LMSes expect one SCO per learning object; test against your target LMS.
- **No suspend/resume state beyond completion:** The shim does not persist `cmi.suspend_data` across sessions. A learner who closes the window mid-track will start from the first module on re-launch, though any modules they marked "complete" will not be re-tracked by the LMS.
- **Content from published/ directory:** Module HTML is read from `published/<module-id>.html` (then `drafts/<module-id>.html`). If a module has no HTML file (e.g. an ICN link-out or imported guide), a yellow placeholder page is included. Replace the placeholder with the approved HTML before distributing.
- **No password protection:** The zip is unencrypted. Apply LMS-level access controls.

---

## 7. Content generation (`demo_app.py`, `demo_d.py`, `demo.py`)

### How it works in demo mode

Generation (Tasks 1–4) runs as a single `claude` CLI subprocess call via the Claude Agent SDK (`claude_agent_sdk.py`). The `claude` CLI reads Anthropic API credentials from its own auth store (set via `claude auth login` or `ANTHROPIC_API_KEY`).

The demo generates against pre-captured Jira fixtures in `data/demo/*-fixture.json` — no live Jira network call at showtime. The LLM call is real; only the Jira reads are cached.

### What production requires

Per ADR-001, the production `app.py` path replaces the `claude` CLI subprocess with a direct Anthropic API call. This removes the Windows ProactorEventLoop dependency and the `~32 KB` CLI arg limit.

Set `ANTHROPIC_API_KEY` in `.env` for the direct API path:

```
ANTHROPIC_API_KEY=sk-ant-api03-...
```

The `demo_app.py` demo server can continue using the CLI subprocess for demos. The direct API path is the production target.

### The deterministic grounding gate

`validate_citations` (in `demo.py`) is a pure string-match gate: every `[CITE:id]` marker must resolve to a verbatim substring of its source field at the correct tier. This has no external dependencies — it works the same in production as in the demo. It is the publish gate; approval is blocked until it passes.

The gate is pinned by `eval/regression.py` (REG-01 through REG-16). Run the regression suite before any deployment:

```
python -m eval.regression
```

---

## 8. ICN content (`EXTERNAL_LEARNING` flag)

### What the flag controls

`EXTERNAL_LEARNING` (read in `demo_app.py`) is a single master switch for the entire external-learning layer: the ICN Content tab (85 assets), roster-based study set assignment, and ICN modules in tracks.

Default: `EXTERNAL_LEARNING=1` (visible). Set to `0` to hide the entire layer:

```
EXTERNAL_LEARNING=0
```

When `0`:
- The Content tab does not appear in the UI.
- ICN modules are excluded from `/api/modules`.
- Existing tracks that include ICN modules continue to work (the modules are still served if requested directly), but new ICN additions are blocked at the UI layer.

### When to enable

Enable `EXTERNAL_LEARNING=1` **only after** the ICN fair-use agreement is signed. The credit/attribution block travels with every card and quiz; `link_only` assets are never reproduced — they open the ICN source URL. These constraints are in the application code, not just documentation, but they depend on the flag being enabled only for authorized deployments.

---

## Environment variables reference

| Variable | Module | Required for | Default (stub mode) | Example value |
|---|---|---|---|---|
| `SCHOOLCAFE_API_URL` | `roster_sync.py` | Real roster reads + completion writeback | Seeded data | `https://api.schoolcafe.com/v3` |
| `SCHOOLCAFE_API_KEY` | `roster_sync.py` | Real roster reads + completion writeback | Seeded data | `sk-live-abc123` |
| `LRS_ENDPOINT` | `xapi_client.py` | xAPI statement writeback to a real LRS | `logs/xapi-stub.jsonl` | `https://lrs.example.com/xapi/statements` |
| `LRS_KEY` | `xapi_client.py` | LRS authentication | Stub mode (no auth) | `admin:password` or `Bearer eyJ...` |
| `EXTERNAL_LEARNING` | `demo_app.py` | ICN content visibility | `1` (visible) | `0` to hide |
| `ANTHROPIC_API_KEY` | Claude CLI / ADR-001 | Content generation | `claude` CLI auth store | `sk-ant-api03-...` |
| `DEMO_MODULE` | `demo_app.py` | Default fixture loaded at startup | `Item Management` | `Accountability` |
| `DEMO_TRANSCRIPT_MODULES` | `demo_app.py` | Modules with no Jira fixture (transcript-only) | `Financials` | `Financials,Payroll` |

---

## What is still stub / not yet production-ready

These items cannot be activated by env vars alone — they require code changes or external agreements.

| Item | What's missing | Notes |
|---|---|---|
| SSO JWT integration | Code change in `auth._get_sso_user()` | Interface is stubbed; JWT validation logic must be written against the SchoolCafé / PrimeroEdge IdP. See ADR-001 §Auth. |
| Demo-seed fallback in completion store | Remove the `id.startswith("demo-")` guard in `completion_store.get_progress()` | Seeded 40% progress will appear for any real user id that doesn't already have a stored record. |
| Per-learner DB persistence (multi-node) | Swap `completion_store` storage backend to Postgres / SQLite | Disk JSON works for single-node. `get_certificate` scans all user dirs — needs an index for production scale. |
| District provisioning UI | No admin UI to add or manage districts | Districts are seeded; production districts come from the SSO JWT claims. No web interface to add/remove districts without code changes. |
| Evaluator (Task 5) | Not implemented | The LLM grader, failure routing, and retry logic described in `CLAUDE.md` §Evaluator are the target spec. V1's publish gate is the deterministic `validate_citations`. |
| Chroma vector retrieval | `match_tickets` uses JQL text search | V1.5 upgrade: index NXT tickets in Chroma for semantic similarity matching. |
| ICN fair-use agreement | Signed agreement required before `EXTERNAL_LEARNING=1` is safe | ICN content and attribution rules are in the code; the agreement governs whether deployment is authorized. |

---

## Zero-to-production checklist

Follow these steps in order on a fresh deployment.

1. [ ] Copy `.env.example` to `.env` (or set env vars in your deployment config).
2. [ ] Set `SCHOOLCAFE_API_URL` and `SCHOOLCAFE_API_KEY` for real roster + writeback.
3. [ ] Set `LRS_ENDPOINT` and `LRS_KEY` for xAPI writebacks.
4. [ ] Set `EXTERNAL_LEARNING=0` **unless** the ICN fair-use agreement has been signed.
5. [ ] Set `ANTHROPIC_API_KEY` if using the direct Anthropic API path (ADR-001 production port).
6. [ ] Implement `_get_sso_user()` in `auth.py` with your IdP's JWT validation.
7. [ ] Remove or gate the demo-seed fallback in `completion_store.get_progress()` (the `id.startswith("demo-")` block).
8. [ ] Ensure `data/completion/` is on a persistent volume writable by the server process.
9. [ ] Install `httpx` (`pip install httpx`) — required for production roster sync and xAPI.
10. [ ] Verify `/api/sync/status` returns `{"stub": false, "env_configured": true}`.
11. [ ] Verify `/api/xapi/status` returns `{"stub": false, "lrs_configured": true}`.
12. [ ] Run the regression suite: `python -m eval.regression` — all 16 cases must pass.
13. [ ] Run the tenancy tests: `python -m pytest tests/test_tenancy.py -v` — all 18 cases must pass.
14. [ ] Run the SCORM + xAPI tests: `python -m pytest tests/test_scorm_xapi.py -v`.
15. [ ] Run the roster sync tests: `python -m pytest tests/test_roster_sync.py -v`.
16. [ ] Send a test request with a real JWT to `GET /api/tracks` and verify identity resolves correctly.
17. [ ] Confirm no `X-Demo-User` header is accepted by the production deployment (block it at the API gateway or remove the demo bypass in `auth.py` for production builds).

---

## Related documents

- `docs/ADR-001-production-architecture.md` — production `app.py` spec, SSO auth design, direct Anthropic API path.
- `CLAUDE.md` — enforcement vs. convention guide; which guarantees are in code vs. in prose.
- `HANDOFF.md` — run gotchas (Windows ProactorEventLoop, big-text CLI limit), repo layout, what's next.
- `eval/EVAL-SPEC.md` — eval harness spec including the triage classifier eval.
- `tests/` — full test suite covering tenancy, SCORM/xAPI, roster sync, scorers, auth, and regression.
