"""STORY-003 regression: approval / edit / publish endpoints require an authorized
(Product Owner / trainer) caller. A learner must never be able to approve, release,
edit, or publish content.

Run from learning-agent/ with the sibling .venv:
    ../../learning-agent/.venv/Scripts/python.exe -m pytest tests/test_approval_authz.py -v

Side-effect-free by design: every id is non-existent. The role check is the FIRST
statement in each handler, so a learner is rejected with 403 *before* any resource is
resolved; an authorized trainer passes the gate and then hits 404 (not found) — never
403. No real atom is approved, published, or edited.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from demo_app import app

client = TestClient(app)

# (path, json body) for each gated endpoint.
GATED_ENDPOINTS = [
    ("/resources/NONEXISTENT-RID/approve", {}),
    ("/resources/NONEXISTENT-RID/publish_pending", {}),
    ("/resources/NONEXISTENT-RID/revise", {"instruction": "noop"}),
    ("/api/quizzes/NONEXISTENT-QID/approve", {}),
    ("/api/flashcards/NONEXISTENT-DECK/approve", {}),
    ("/api/tracks/NONEXISTENT-TID/publish", {}),
]


def test_learner_is_blocked_from_every_approval_endpoint():
    """A Cashier (learner) gets 403 on all approval/edit/publish endpoints."""
    for path, body in GATED_ENDPOINTS:
        r = client.post(path, json=body, headers={"X-Demo-User": "john-cashier"})
        assert r.status_code == 403, f"{path}: learner should be 403, got {r.status_code} {r.text[:200]}"


def test_director_is_blocked_too():
    """A CN Director is not a content approver either — only POs/trainers are."""
    for path, body in GATED_ENDPOINTS:
        r = client.post(path, json=body, headers={"X-Demo-User": "dana-director"})
        assert r.status_code == 403, f"{path}: director should be 403, got {r.status_code} {r.text[:200]}"


def test_trainer_passes_the_role_gate():
    """A trainer clears the authZ gate; a non-existent id then yields a non-403
    (404/409/422/502) — proving the gate does not block authorized callers."""
    for path, body in GATED_ENDPOINTS:
        r = client.post(path, json=body, headers={"X-Demo-User": "sam-trainer"})
        assert r.status_code != 403, f"{path}: trainer should NOT be 403, got {r.status_code} {r.text[:200]}"
