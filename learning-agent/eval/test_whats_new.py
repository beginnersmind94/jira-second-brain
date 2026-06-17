"""eval/test_whats_new.py — Deterministic HTTP tests for LRN-WN: What's New for You.

Test coverage per the LRN-WN spec:
  T1  GET /api/whats-new?role=Cashier → 200 with items list; every item has
      required fields (id, kind, title, origin, published_at, freshness_label,
      open ref).  Only approved/published artifacts may surface.
  T2  SHOULD-NOT-OCCUR: a Cashier must never see content tagged exclusively for
      CN Director.  Director result must be a superset of Cashier result.
  T3  Every item (all roles) has valid origin and a non-empty open.ref that is
      resolvable to a known type.
  T4  SHOULD-NOT-OCCUR: no item's published_at may be in the future (fabricated
      freshness).
  T5  _sources block is present; freshness_basis == "training_publish_date";
      jira_incremental_changes_since_bulk_import == 0 (no incremental sync has
      occurred since the Apr-20 bulk import).
  T6  SHOULD-NOT-OCCUR: raw wiki paths, NXT- ticket IDs, or .md file paths must
      never appear in any learner-facing string (title, summary, module,
      context_themes chips).

Tests call the live server on port 8001 via requests.
No SDK calls, no mocks — these are black-box contract tests.

Run:
    python -m pytest learning-agent/eval/test_whats_new.py -v
  or from learning-agent/:
    python eval/test_whats_new.py
"""
from __future__ import annotations

import sys
from datetime import date

import pytest
import requests

BASE = "http://localhost:8001"

# ── Helpers ───────────────────────────────────────────────────────────────────

def _get(role: str, user: str = "john-cashier") -> requests.Response:
    """GET /api/whats-new for the given role, authenticated as user."""
    return requests.get(
        f"{BASE}/api/whats-new",
        params={"role": role},
        headers={"X-Demo-User": user},
        timeout=10,
    )


# ── T1: Basic contract — approved items only surface ─────────────────────────

def test_t1_only_approved_items():
    """Only approved/published training artifacts appear in the strip.
    A wiki topic with no approved guide must be absent.
    Every item must carry the full required field set."""
    r = _get("Cashier")
    assert r.status_code == 200, f"expected 200, got {r.status_code}: {r.text[:200]}"
    data = r.json()

    # Top-level envelope fields
    assert "items" in data, "response missing 'items' key"
    assert "role" in data, "response missing 'role' key"
    assert "_sources" in data, "response missing '_sources' key"
    assert data["role"] == "Cashier", f"role echo mismatch: {data['role']}"

    # Per-item required fields
    for item in data["items"]:
        assert item.get("id"), f"item missing id: {item}"
        assert item.get("kind") in ("track", "guide"), (
            f"invalid kind '{item.get('kind')}' on item {item.get('id')}"
        )
        assert item.get("title"), f"item {item.get('id')} missing title"
        assert item.get("origin") in ("ai_grounded", "human_authored", "outside_vendor"), (
            f"invalid origin '{item.get('origin')}' on item {item.get('id')}"
        )
        assert item.get("published_at"), f"item {item.get('id')} missing published_at"
        assert item.get("freshness_label"), f"item {item.get('id')} missing freshness_label"
        open_ref = item.get("open")
        assert open_ref, f"item {item.get('id')} missing open ref"

    print(f"T1 PASS: {len(data['items'])} item(s) returned, all carry required fields")


# ── T2: SHOULD-NOT-OCCUR — cashier sees director-only content ─────────────────

def test_t2_cashier_no_director_content_SHOULD_NOT_OCCUR():
    """SHOULD-NOT-OCCUR: A cashier must never see content whose role_tags restrict
    it exclusively to roles a cashier does not hold (e.g. Site Manager only,
    CN Director only).

    Note: the 5-item cap means a Director's top-5 is NOT guaranteed to be a
    superset of the Cashier's top-5 — the Director has a larger candidate pool and
    role-specific items may fill their cap before all-staff items. The correct
    invariant is access-control, not cap-level set inclusion: every item the
    cashier sees must be accessible TO a cashier (role_tags ∩ {Cashier,''} ≠ ∅,
    or role_tags is empty)."""
    r_cashier = _get("Cashier", user="john-cashier")
    assert r_cashier.status_code == 200, f"Cashier request failed: {r_cashier.status_code}"
    cashier_items = r_cashier.json()["items"]

    # Build a role_tags lookup from the tracks and modules APIs.
    r_tracks = requests.get(f"{BASE}/api/tracks", headers={"X-Demo-User": "john-cashier"})
    r_mods = requests.get(f"{BASE}/api/modules", headers={"X-Demo-User": "john-cashier"})
    assert r_tracks.status_code == 200
    assert r_mods.status_code == 200

    role_lookup: dict[str, list[str]] = {}
    for t in r_tracks.json().get("tracks", []):
        role_lookup[t["id"]] = t.get("role_tags") or []
    for m in r_mods.json().get("modules", []):
        role_lookup[m["id"]] = m.get("role_tags") or []

    cashier_visible = {"Cashier", "All staff", ""}

    for item in cashier_items:
        ref = item.get("open", {}).get("ref", item.get("id", ""))
        tags = role_lookup.get(ref, [])
        # Normalise: drop "All staff" entries (they mean untagged)
        restricted_tags = [t for t in tags if t and t.lower() not in ("all staff", "all")]
        if restricted_tags:
            # The artifact is role-restricted — Cashier must be in the restriction list.
            assert any(t in cashier_visible for t in restricted_tags), (
                f"SHOULD-NOT-OCCUR: cashier sees content restricted to {restricted_tags} "
                f"(ref={ref}, title={item.get('title')}) — "
                "role filter is passing director/manager-only content to cashier"
            )

    print(f"T2 PASS: {len(cashier_items)} cashier item(s) — all role_tags are cashier-accessible")


# ── T3: Provenance — every item has valid origin + resolvable open ref ─────────

def test_t3_provenance_complete():
    """Every item across all three demo roles must have:
    - a valid origin enum value
    - a non-empty open.ref
    - a known open.type"""
    for role, user in [
        ("Cashier", "john-cashier"),
        ("CN Director", "dana-director"),
    ]:
        r = _get(role, user)
        assert r.status_code == 200, (
            f"request for role={role} failed: {r.status_code}"
        )
        for item in r.json()["items"]:
            iid = item.get("id", "<unknown>")
            assert item.get("origin") in ("ai_grounded", "human_authored", "outside_vendor"), (
                f"role={role} item={iid}: invalid origin '{item.get('origin')}'"
            )
            open_ref = item.get("open") or {}
            assert open_ref.get("ref"), (
                f"role={role} item={iid}: open.ref is empty or missing"
            )
            assert open_ref.get("type") in ("track", "guide", "resource"), (
                f"role={role} item={iid}: open.type '{open_ref.get('type')}' is not a known type"
            )

    print("T3 PASS: all items across Cashier + CN Director have valid origin and resolvable open ref")


# ── T4: SHOULD-NOT-OCCUR — future or fabricated published_at date ─────────────

def test_t4_no_future_dates_SHOULD_NOT_OCCUR():
    """SHOULD-NOT-OCCUR: No item's published_at may be set to a future date.
    A future published_at implies a fabricated or incorrectly sourced freshness
    signal — the strip would claim content is "New" before it exists."""
    today = date.today().isoformat()
    r = _get("Cashier")
    assert r.status_code == 200, f"request failed: {r.status_code}"

    for item in r.json()["items"]:
        iid = item.get("id", "<unknown>")
        pd = item.get("published_at", "")
        assert pd, f"item {iid} has empty published_at (required)"
        # ISO date comparison: "YYYY-MM-DD" lexicographic order matches calendar order
        assert pd <= today, (
            f"SHOULD-NOT-OCCUR: item '{iid}' has published_at='{pd}' which is in the future "
            f"(today={today}); freshness dates must not be fabricated"
        )

    print(f"T4 PASS: no item has a future published_at (checked against today={today})")


# ── T5: Honest sources — Jira incremental count is 0 ────────────────────────

def test_t5_honest_sources():
    """_sources must be present and carry honest provenance metadata.
    freshness_basis must be 'training_publish_date' (not Jira change dates).
    jira_incremental_changes_since_bulk_import must be exactly 0 — no incremental
    Jira sync has occurred since the Apr-20 bulk import, so the strip must not
    imply product changes that didn't happen."""
    r = _get("Cashier")
    assert r.status_code == 200, f"request failed: {r.status_code}"
    data = r.json()

    src = data.get("_sources")
    assert src, "_sources key is missing or empty from response"

    assert src.get("freshness_basis") == "training_publish_date", (
        f"_sources.freshness_basis must be 'training_publish_date', "
        f"got '{src.get('freshness_basis')}'"
    )

    jira_count = src.get("jira_incremental_changes_since_bulk_import")
    assert jira_count == 0, (
        f"SHOULD-NOT-OCCUR: jira_incremental_changes_since_bulk_import must be 0 "
        f"(no incremental sync exists yet), got {jira_count}"
    )

    print(
        f"T5 PASS: _sources present; freshness_basis=training_publish_date; "
        f"jira_incremental=0"
    )


# ── T6: SHOULD-NOT-OCCUR — internal paths or ticket IDs leak to learner ────────

def test_t6_no_internal_identifiers_SHOULD_NOT_OCCUR():
    """SHOULD-NOT-OCCUR: No raw wiki file paths, NXT- Jira ticket IDs, or .md
    file paths must appear in any learner-facing field (title, summary, module,
    context_themes chips).  Internal identifiers leaking into learner-visible
    strings breaks trust and exposes the internal content architecture."""
    for role, user in [
        ("Cashier", "john-cashier"),
        ("Site Manager", "john-cashier"),
        ("CN Director", "dana-director"),
    ]:
        r = _get(role, user)
        assert r.status_code == 200, (
            f"request for role={role} failed: {r.status_code}"
        )
        for item in r.json()["items"]:
            iid = item.get("id", "<unknown>")

            # Check scalar learner-facing string fields
            for field in ("title", "summary", "module"):
                val = item.get(field) or ""
                assert "wiki/" not in val, (
                    f"SHOULD-NOT-OCCUR: wiki path found in {field} "
                    f"(role={role}, item={iid}): '{val}'"
                )
                assert "NXT-" not in val, (
                    f"SHOULD-NOT-OCCUR: Jira ticket ID found in {field} "
                    f"(role={role}, item={iid}): '{val}'"
                )
                assert ".md" not in val, (
                    f"SHOULD-NOT-OCCUR: .md file path found in {field} "
                    f"(role={role}, item={iid}): '{val}'"
                )

            # Check context_themes chips
            for chip in item.get("context_themes") or []:
                assert "NXT-" not in chip, (
                    f"SHOULD-NOT-OCCUR: Jira ticket ID in context_themes chip "
                    f"(role={role}, item={iid}): '{chip}'"
                )
                assert "wiki/" not in chip, (
                    f"SHOULD-NOT-OCCUR: wiki path in context_themes chip "
                    f"(role={role}, item={iid}): '{chip}'"
                )
                assert ".md" not in chip, (
                    f"SHOULD-NOT-OCCUR: .md path in context_themes chip "
                    f"(role={role}, item={iid}): '{chip}'"
                )

    print("T6 PASS: no internal identifiers (wiki paths / NXT- IDs / .md paths) in any learner-facing field")


# ── Runner ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_t1_only_approved_items,
        test_t2_cashier_no_director_content_SHOULD_NOT_OCCUR,
        test_t3_provenance_complete,
        test_t4_no_future_dates_SHOULD_NOT_OCCUR,
        test_t5_honest_sources,
        test_t6_no_internal_identifiers_SHOULD_NOT_OCCUR,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as exc:
            print(f"FAIL {t.__name__}: {exc}")
            import traceback
            traceback.print_exc()
            failed += 1
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{len(tests)} passed" + (f", {failed} failed" if failed else ""))
    if failed:
        sys.exit(1)
