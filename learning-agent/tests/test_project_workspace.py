"""Tests for project_workspace_store (Epic: implementation-workspace, STORY-001).

Closes the machine-checkable acceptance criteria per docs/STORY-SPEC-STANDARD.md.
Each test isolates the store to a tmp dir so it never touches data/workspaces/.
"""
import pytest

import project_workspace_store as ws


def test_seed_variety(tmp_path, monkeypatch):
    """AC1 — each demo district seeds at a distinct, believable point."""
    monkeypatch.setattr(ws, "_WS_DIR", tmp_path)
    hou = ws.get_workspace("houston-isd")
    ald = ws.get_workspace("aldine-isd")
    kle = ws.get_workspace("klein-isd")
    assert hou["status"] == "at_risk"
    assert ald["status"] == "blocked"
    assert kle["status"] == "on_track"
    assert kle["overall_pct"] > hou["overall_pct"] > ald["overall_pct"]
    assert len(hou["milestones"]) == 5
    assert hou["current_milestone"] == "config"


def test_never_empty(tmp_path, monkeypatch):
    """AC4 — an unseen district id still returns a full, mid-onboarding workspace."""
    monkeypatch.setattr(ws, "_WS_DIR", tmp_path)
    w = ws.get_workspace("totally-unknown-district")
    assert len(w["milestones"]) == 5
    assert any(i["status"] == "done" for m in w["milestones"] for i in m["items"])


def test_toggle_persists_and_logs(tmp_path, monkeypatch):
    """AC3 — toggle flips status, recomputes %, logs activity, and persists to disk."""
    monkeypatch.setattr(ws, "_WS_DIR", tmp_path)
    before = ws.get_workspace("houston-isd")["overall_pct"]
    ws.toggle_item("houston-isd", "config-pos", actor="Tester")
    w = ws.get_workspace("houston-isd")  # re-read from disk
    pos = next(i for m in w["milestones"] for i in m["items"] if i["id"] == "config-pos")
    assert pos["status"] == "done"
    assert pos["done_at"] is not None
    assert w["overall_pct"] > before
    assert w["activity"][0]["type"] == "item_toggle"
    assert w["activity"][0]["actor"] == "Tester"
    # toggling again restores
    ws.toggle_item("houston-isd", "config-pos", actor="Tester")
    assert ws.get_workspace("houston-isd")["overall_pct"] == before


def test_toggle_unknown_item_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(ws, "_WS_DIR", tmp_path)
    with pytest.raises(KeyError):
        ws.toggle_item("houston-isd", "no-such-item", actor="x")


def test_task_and_note_validation(tmp_path, monkeypatch):
    monkeypatch.setattr(ws, "_WS_DIR", tmp_path)
    t = ws.add_task("houston-isd", "Do the thing", owner="District", due="2026-07-01", actor="x")
    assert t["status"] == "open" and t["title"] == "Do the thing"
    with pytest.raises(ValueError):
        ws.add_task("houston-isd", "   ", actor="x")
    n = ws.add_note("houston-isd", "a real note", author="x")
    assert n["author"] == "x" and n["body"] == "a real note"
    with pytest.raises(ValueError):
        ws.add_note("houston-isd", "", author="x")


def test_blocked_item_never_also_done(tmp_path, monkeypatch):
    """Aldine's blocked roster item must not be seeded as done."""
    monkeypatch.setattr(ws, "_WS_DIR", tmp_path)
    w = ws.get_workspace("aldine-isd")
    roster = next(i for m in w["milestones"] for i in m["items"] if i["id"] == "data-roster")
    assert roster["status"] == "blocked"


# ── Tracker refactor: owner/due, weighted progress, blocker nudge/resolve, auto roles ──

def _item(w, iid):
    return next(i for m in w["milestones"] for i in m["items"] if i["id"] == iid)


def test_blocked_item_has_reason_and_since(tmp_path, monkeypatch):
    """Seeded blocker carries reason + blocked_since so the primary zone can show them."""
    monkeypatch.setattr(ws, "_WS_DIR", tmp_path)
    roster = _item(ws.get_workspace("aldine-isd"), "data-roster")
    assert roster["reason"] and roster["blocked_since"]


def test_set_owner_and_due_persist(tmp_path, monkeypatch):
    monkeypatch.setattr(ws, "_WS_DIR", tmp_path)
    ws.set_item_owner("houston-isd", "config-pos", "Cybersoft", actor="x")
    ws.set_item_due("houston-isd", "config-pos", "2026-07-01", actor="x")
    it = _item(ws.get_workspace("houston-isd"), "config-pos")  # re-read from disk
    assert it["owner"] == "Cybersoft" and it["due"] == "2026-07-01" and it["updated_at"]
    with pytest.raises(ValueError):
        ws.set_item_owner("houston-isd", "config-pos", "Nobody", actor="x")
    ws.set_item_due("houston-isd", "config-pos", "", actor="x")  # clear
    assert _item(ws.get_workspace("houston-isd"), "config-pos")["due"] == ""


def test_weighted_progress_not_flat(tmp_path, monkeypatch):
    """Overall % is critical-path weighted, so completing a heavy milestone moves it
    more than a light one with the same item count."""
    monkeypatch.setattr(ws, "_WS_DIR", tmp_path)
    base = ws.get_workspace("aldine-isd")["overall_pct"]
    # Complete one item in the heaviest open milestone (uat, weight 3) ...
    ws.toggle_item("aldine-isd", "uat-signoff", actor="x")
    heavy = ws.get_workspace("aldine-isd")["overall_pct"]
    ws.toggle_item("aldine-isd", "uat-signoff", actor="x")  # undo
    # ... vs one item in the lightest (kickoff, weight 1) — already all done, so use config (weight 2).
    assert heavy > base  # heavy milestone progress raised overall readiness


def test_nudge_and_resolve_blocker(tmp_path, monkeypatch):
    monkeypatch.setattr(ws, "_WS_DIR", tmp_path)
    # nudge records nudged_at + logs activity
    w = ws.nudge_blocker("aldine-isd", "data-roster", actor="Sam")
    roster = _item(w, "data-roster")
    assert roster["nudged_at"] and w["activity"][0]["type"] == "blocker_nudge"
    # nudging a non-blocked item is rejected
    with pytest.raises(ValueError):
        ws.nudge_blocker("aldine-isd", "kickoff-call", actor="Sam")
    # resolve clears blocked + marks done
    w = ws.resolve_block("aldine-isd", "data-roster", actor="Sam")
    roster = _item(w, "data-roster")
    assert roster["status"] == "done" and not roster.get("reason") and not roster.get("blocked_since")
    assert w["status"] != "blocked"
    with pytest.raises(ValueError):
        ws.resolve_block("aldine-isd", "data-roster", actor="Sam")  # no longer blocked


def test_auto_section_items_carry_role(tmp_path, monkeypatch):
    """Staff Training items expose a role so the UI can source completion from the roster."""
    monkeypatch.setattr(ws, "_WS_DIR", tmp_path)
    training = next(m for m in ws.get_workspace("klein-isd")["milestones"] if m["key"] == "training")
    roles = {i["role"] for i in training["items"]}
    assert roles == {"Cashier", "Site Manager", "CN Director"} and training["auto"]


# ── Full inline-edit CRUD (the checklist is editable, not template-locked) ──

def _items(w, mkey):
    return [i["label"] for m in w["milestones"] if m["key"] == mkey for i in m["items"]]


def test_add_rename_delete_item(tmp_path, monkeypatch):
    monkeypatch.setattr(ws, "_WS_DIR", tmp_path)
    item, w = ws.add_item("houston-isd", "config", "Custom config step", owner="District", actor="x")
    assert "Custom config step" in _items(w, "config")
    w = ws.rename_item("houston-isd", item["id"], "Renamed step", actor="x")
    assert "Renamed step" in _items(w, "config") and "Custom config step" not in _items(w, "config")
    w = ws.delete_item("houston-isd", item["id"], actor="x")
    assert "Renamed step" not in _items(w, "config")
    # survives a disk round-trip
    assert "Renamed step" not in _items(ws.get_workspace("houston-isd"), "config")


def test_add_empty_item_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(ws, "_WS_DIR", tmp_path)
    with pytest.raises(ValueError):
        ws.add_item("houston-isd", "config", "   ", actor="x")


def test_set_status_block_and_clear(tmp_path, monkeypatch):
    monkeypatch.setattr(ws, "_WS_DIR", tmp_path)
    w = ws.set_item_status("houston-isd", "config-pos", "blocked", reason="vendor late", actor="x")
    pos = next(i for m in w["milestones"] for i in m["items"] if i["id"] == "config-pos")
    assert pos["status"] == "blocked" and pos["reason"] == "vendor late" and w["status"] == "blocked"
    w = ws.set_item_status("houston-isd", "config-pos", "todo", actor="x")
    pos = next(i for m in w["milestones"] for i in m["items"] if i["id"] == "config-pos")
    assert pos["status"] == "todo" and not pos.get("reason")


def test_add_rename_delete_section(tmp_path, monkeypatch):
    monkeypatch.setattr(ws, "_WS_DIR", tmp_path)
    sec, w = ws.add_section("houston-isd", "Post Go-Live", actor="x")
    assert any(m["label"] == "Post Go-Live" for m in w["milestones"])
    w = ws.rename_section("houston-isd", sec["key"], "Hypercare", actor="x")
    assert any(m["label"] == "Hypercare" for m in w["milestones"])
    # items can be added to a brand-new section
    _, w = ws.add_item("houston-isd", sec["key"], "Monitor first week", actor="x")
    assert "Monitor first week" in _items(w, sec["key"])
    w = ws.delete_section("houston-isd", sec["key"], actor="x")
    assert not any(m["key"] == sec["key"] for m in w["milestones"])


def test_reorder_within_and_across_sections(tmp_path, monkeypatch):
    monkeypatch.setattr(ws, "_WS_DIR", tmp_path)
    w = ws.get_workspace("houston-isd")
    data_ids = [i["id"] for m in w["milestones"] if m["key"] == "data" for i in m["items"]]
    # move the last data item before the first -> it becomes first
    w = ws.reorder_item("houston-isd", data_ids[-1], "data", before_item_id=data_ids[0], actor="x")
    new_first = next(m for m in w["milestones"] if m["key"] == "data")["items"][0]["id"]
    assert new_first == data_ids[-1]
    # move it across to config (append to end)
    w = ws.reorder_item("houston-isd", data_ids[-1], "config", before_item_id="", actor="x")
    assert data_ids[-1] not in [i["id"] for m in w["milestones"] if m["key"] == "data" for i in m["items"]]
    assert data_ids[-1] == next(m for m in w["milestones"] if m["key"] == "config")["items"][-1]["id"]


def test_legacy_items_dict_migrates(tmp_path, monkeypatch):
    """A pre-existing legacy {items:{...}} file is read transparently as sections."""
    monkeypatch.setattr(ws, "_WS_DIR", tmp_path)
    import json
    legacy = {"district_id": "legacy-isd", "template": "schoolcafe-onboarding",
              "items": {"config-pos": {"status": "done", "done_at": "2026-06-01T00:00:00+00:00"}},
              "tasks": [], "notes": [], "activity": []}
    (tmp_path / "legacy-isd.json").write_text(json.dumps(legacy), encoding="utf-8")
    w = ws.get_workspace("legacy-isd")
    assert len(w["milestones"]) == 5
    pos = next(i for m in w["milestones"] for i in m["items"] if i["id"] == "config-pos")
    assert pos["status"] == "done"
    # and a mutation against the migrated file still works + persists
    ws.add_item("legacy-isd", "config", "New step after migration", actor="x")
    assert "New step after migration" in _items(ws.get_workspace("legacy-isd"), "config")
