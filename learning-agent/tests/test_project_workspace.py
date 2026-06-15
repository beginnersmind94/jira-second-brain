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
