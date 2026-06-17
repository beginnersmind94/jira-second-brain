"""Tests for LRN-5 — peer knowledge board comment store.

Run from learning-agent/ with:
    ..\\..\\learning-agent\\.venv\\Scripts\\python.exe -m pytest tests/test_comment_store.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import comment_store as cs  # noqa: E402


# ── Fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def isolated_comments(tmp_path, monkeypatch):
    monkeypatch.setattr(cs, "_COMMENTS_DIR", tmp_path / "comments")
    yield


RID  = "GUIDE-LRN5-TEST"
UID  = "learner-001"
NAME = "Alex Learner"


# ── Test 1: empty store returns empty list ────────────────────────────────────

def test_list_comments_empty():
    result = cs.list_comments(RID)
    assert result == []


# ── Test 2: add_comment creates a well-formed comment ────────────────────────

def test_add_comment_returns_correct_fields():
    c = cs.add_comment(RID, UID, NAME, "Great tip about the override workflow!")
    assert c["resource_id"] == RID
    assert c["author_id"] == UID
    assert c["author_name"] == NAME
    assert c["body"] == "Great tip about the override workflow!"
    assert c["pinned"] is False
    assert "id" in c
    assert "created_at" in c

    # Confirm it persists.
    all_c = cs.list_comments(RID)
    assert len(all_c) == 1
    assert all_c[0]["id"] == c["id"]


# ── Test 3: pinned comments sort before unpinned ─────────────────────────────

def test_pinned_comments_sort_first():
    c1 = cs.add_comment(RID, UID, NAME, "First note")
    c2 = cs.add_comment(RID, "trainer-t1", "Sam Trainer", "Pinned tip")

    cs.pin_comment(c2["id"], RID)

    ordered = cs.list_comments(RID)
    assert ordered[0]["id"] == c2["id"], "Pinned comment should be first"
    assert ordered[1]["id"] == c1["id"]


# ── Test 4: pin_comment toggles pin state ────────────────────────────────────

def test_pin_comment_toggles():
    c = cs.add_comment(RID, UID, NAME, "Toggle me")
    assert c["pinned"] is False

    updated = cs.pin_comment(c["id"], RID)
    assert updated["pinned"] is True

    unpin = cs.pin_comment(c["id"], RID)
    assert unpin["pinned"] is False


# ── Test 5: validation guards ─────────────────────────────────────────────────

def test_add_comment_rejects_empty_body():
    with pytest.raises(ValueError, match="empty"):
        cs.add_comment(RID, UID, NAME, "   ")


def test_add_comment_rejects_oversized_body():
    with pytest.raises(ValueError, match="1000"):
        cs.add_comment(RID, UID, NAME, "x" * 1001)
