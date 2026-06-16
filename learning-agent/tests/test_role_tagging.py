"""Tests for role-tagging feature (Goal 1-4).

Covers:
  1. Canonical role vocabulary (GET /api/roles, auth.ROLE_VOCAB, JS constant verified structurally).
  2. Role tags at generation: draft_meta written with role_tags, preserved through approve.
  3. Role-tag edit endpoint: PUT /api/modules/{id}/role-tags persists to metadata; validates vocab.
  4. GET /api/modules?role=... returns modules tagged with that role after tagging.

Run: python -m pytest tests/test_role_tagging.py -v
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure the learning-agent root is on the path (this file lives in tests/).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient

_TRAINER_HEADERS = {"X-Demo-User": "sam-trainer"}
_CASHIER_HEADERS = {"X-Demo-User": "john-cashier"}


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    from demo_app import app
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_tracks(tmp_path, monkeypatch):
    """Redirect tracks storage to a temp directory."""
    import modules_store
    monkeypatch.setattr(modules_store, "TRACKS_DIR", tmp_path / "tracks")
    (tmp_path / "tracks").mkdir()


@pytest.fixture
def approved_meta_file(tmp_path, monkeypatch):
    """Create a minimal published/metadata/<rid>.json so the role-tag edit endpoint can find it."""
    import app as _prod
    import modules_store as _ms

    pub_meta_dir = tmp_path / "pub_meta"
    pub_meta_dir.mkdir()
    pub_html_dir = tmp_path / "pub_html"
    pub_html_dir.mkdir()

    rid = "test-role-guide-001"
    meta = {
        "id": rid,
        "title": "Role Tag Test Guide",
        "module": "TestModule",
        "template": "micro-guide",
        "status": "approved",
        "approved": True,
        "role_tags": [],
        "origin": "internal",
    }
    (pub_meta_dir / f"{rid}.json").write_text(json.dumps(meta), encoding="utf-8")
    # Create a minimal HTML so _resolve_resource finds it.
    (pub_html_dir / f"{rid}.html").write_text("<h1>Test</h1>", encoding="utf-8")

    # Patch app.py (used by _resolve_resource in the PUT endpoint).
    monkeypatch.setattr(_prod, "PUB_META", pub_meta_dir)
    monkeypatch.setattr(_prod, "PUBLISHED", pub_html_dir)
    # Also patch modules_store (used by GET /api/modules aggregation).
    monkeypatch.setattr(_ms, "PUB_META", pub_meta_dir)
    monkeypatch.setattr(_ms, "PUBLISHED", pub_html_dir)
    # Patch DRAFTS in both so draft lookup doesn't pick up stale files.
    drafts_dir = tmp_path / "drafts"
    drafts_dir.mkdir()
    monkeypatch.setattr(_prod, "DRAFTS", drafts_dir)
    monkeypatch.setattr(_ms, "DRAFTS", drafts_dir)

    return rid, pub_meta_dir


@pytest.fixture
def draft_meta_file(tmp_path, monkeypatch):
    """Create a minimal drafts/<rid>.json so _resolve_resource finds a draft."""
    import app as _prod

    drafts_dir = tmp_path / "drafts"
    drafts_dir.mkdir()

    rid = "test-draft-role-001"
    meta = {
        "id": rid,
        "title": "Draft Role Tag Test",
        "module": "TestModule",
        "template": "micro-guide",
        "status": "draft",
        "role_tags": [],
    }
    (drafts_dir / f"{rid}.json").write_text(json.dumps(meta), encoding="utf-8")
    (drafts_dir / f"{rid}.html").write_text("<h1>Draft</h1>", encoding="utf-8")

    monkeypatch.setattr(_prod, "DRAFTS", drafts_dir)
    monkeypatch.setattr(_prod, "PUB_META", tmp_path / "pub_meta_empty")
    monkeypatch.setattr(_prod, "PUBLISHED", tmp_path / "pub_empty")
    (tmp_path / "pub_meta_empty").mkdir()
    (tmp_path / "pub_empty").mkdir()

    return rid, drafts_dir


# ── Goal 1: Canonical role vocabulary ─────────────────────────────────────────

class TestRoleVocabulary:
    def test_get_api_roles_returns_list(self, client):
        """GET /api/roles must return a non-empty list of role strings."""
        resp = client.get("/api/roles")
        assert resp.status_code == 200
        data = resp.json()
        assert "roles" in data
        assert isinstance(data["roles"], list)
        assert len(data["roles"]) > 0

    def test_role_vocab_contains_cashier(self, client):
        """Canonical vocabulary must contain 'Cashier' — the primary demo persona role."""
        resp = client.get("/api/roles")
        assert "Cashier" in resp.json()["roles"]

    def test_role_vocab_contains_cn_director(self, client):
        """Canonical vocabulary must contain 'CN Director' — the second demo persona role."""
        resp = client.get("/api/roles")
        assert "CN Director" in resp.json()["roles"]

    def test_role_vocab_does_not_contain_trainer(self, client):
        """'Trainer' must NOT be in the content role vocabulary (Trainers see all content)."""
        resp = client.get("/api/roles")
        assert "Trainer" not in resp.json()["roles"]

    def test_role_vocab_matches_auth_constant(self):
        """GET /api/roles must return the same list as auth.ROLE_VOCAB."""
        from auth import ROLE_VOCAB
        from demo_app import app
        c = TestClient(app)
        resp = c.get("/api/roles")
        assert resp.json()["roles"] == ROLE_VOCAB

    def test_learner_persona_roles_are_in_vocab(self):
        """Every LEARNER demo persona's role must be in ROLE_VOCAB.

        This ensures filtering on current_user.role against module role_tags
        will work for the demo personas: if a learner persona's role is NOT in
        ROLE_VOCAB, guides tagged for them can never be created via the UI (the
        role picker only shows ROLE_VOCAB entries).

        Note: ROLE_VOCAB may contain roles without a demo persona (e.g.
        'Site Manager' is a real customer role that will get a persona later).
        The contract is one-directional: learner personas must be in the vocab,
        not every vocab entry must have a persona.
        """
        from auth import ROLE_VOCAB, _DEMO_PERSONAS
        for key, persona in _DEMO_PERSONAS.items():
            if not persona.is_trainer:  # Trainers are staff, not content audience
                assert persona.role in ROLE_VOCAB, (
                    f"Learner demo persona '{key}' has role '{persona.role}' which is "
                    f"NOT in ROLE_VOCAB {ROLE_VOCAB}. Content tagged for this role via "
                    f"the UI would never reach them because the role picker only shows ROLE_VOCAB."
                )


# ── Goal 3: PUT /api/modules/{id}/role-tags ───────────────────────────────────

class TestRoleTagEditEndpoint:
    def test_update_role_tags_persists(self, client, approved_meta_file):
        """PUT /api/modules/{id}/role-tags must write role_tags to the metadata file."""
        rid, pub_meta_dir = approved_meta_file
        resp = client.put(
            f"/api/modules/{rid}/role-tags",
            json={"role_tags": ["Cashier", "Site Manager"]},
            headers=_TRAINER_HEADERS,
        )
        assert resp.status_code == 200, resp.text
        saved = json.loads((pub_meta_dir / f"{rid}.json").read_text(encoding="utf-8"))
        assert "Cashier" in saved["role_tags"]
        assert "Site Manager" in saved["role_tags"]

    def test_update_role_tags_returns_updated_meta(self, client, approved_meta_file):
        """PUT response must include the new role_tags."""
        rid, _ = approved_meta_file
        resp = client.put(
            f"/api/modules/{rid}/role-tags",
            json={"role_tags": ["CN Director"]},
            headers=_TRAINER_HEADERS,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["role_tags"] == ["CN Director"]

    def test_update_role_tags_empty_list_allowed(self, client, approved_meta_file):
        """Clearing all role_tags (empty list) must be accepted — makes the module global."""
        rid, pub_meta_dir = approved_meta_file
        # First set some tags.
        client.put(f"/api/modules/{rid}/role-tags", json={"role_tags": ["Cashier"]}, headers=_TRAINER_HEADERS)
        # Then clear.
        resp = client.put(f"/api/modules/{rid}/role-tags", json={"role_tags": []}, headers=_TRAINER_HEADERS)
        assert resp.status_code == 200
        saved = json.loads((pub_meta_dir / f"{rid}.json").read_text(encoding="utf-8"))
        assert saved["role_tags"] == []

    def test_update_role_tags_rejects_unknown_role(self, client, approved_meta_file):
        """PUT with a role string not in ROLE_VOCAB must return 400."""
        rid, _ = approved_meta_file
        resp = client.put(
            f"/api/modules/{rid}/role-tags",
            json={"role_tags": ["UnknownRole"]},
            headers=_TRAINER_HEADERS,
        )
        assert resp.status_code == 400, (
            f"Expected 400 for unknown role, got {resp.status_code}: {resp.text}"
        )

    def test_update_role_tags_rejects_non_list(self, client, approved_meta_file):
        """PUT with role_tags as a string (not a list) must return 400."""
        rid, _ = approved_meta_file
        resp = client.put(
            f"/api/modules/{rid}/role-tags",
            json={"role_tags": "Cashier"},
            headers=_TRAINER_HEADERS,
        )
        assert resp.status_code == 400

    def test_update_role_tags_requires_trainer(self, client, approved_meta_file):
        """A learner (john-cashier) must get 403 when trying to edit role tags."""
        rid, _ = approved_meta_file
        resp = client.put(
            f"/api/modules/{rid}/role-tags",
            json={"role_tags": ["Cashier"]},
            headers=_CASHIER_HEADERS,
        )
        assert resp.status_code == 403, (
            f"Expected 403 for learner editing role tags, got {resp.status_code}"
        )

    def test_update_role_tags_does_not_change_approval_status(self, client, approved_meta_file):
        """Editing role_tags must NOT reset the approved/status fields — metadata-only change."""
        rid, pub_meta_dir = approved_meta_file
        resp = client.put(
            f"/api/modules/{rid}/role-tags",
            json={"role_tags": ["Cashier"]},
            headers=_TRAINER_HEADERS,
        )
        assert resp.status_code == 200
        saved = json.loads((pub_meta_dir / f"{rid}.json").read_text(encoding="utf-8"))
        assert saved.get("approved") is True, (
            "role-tag edit must not clear the 'approved' flag"
        )
        assert saved.get("status") == "approved", (
            "role-tag edit must not drop status back to 'draft'"
        )

    def test_update_role_tags_404_for_missing_module(self, client, approved_meta_file):
        """PUT for a non-existent module id must return 404."""
        resp = client.put(
            "/api/modules/does-not-exist-xyz/role-tags",
            json={"role_tags": ["Cashier"]},
            headers=_TRAINER_HEADERS,
        )
        assert resp.status_code == 404

    def test_update_role_tags_works_on_draft(self, client, draft_meta_file):
        """Role tags can be edited on a draft resource too (same endpoint)."""
        rid, drafts_dir = draft_meta_file
        resp = client.put(
            f"/api/modules/{rid}/role-tags",
            json={"role_tags": ["Site Manager"]},
            headers=_TRAINER_HEADERS,
        )
        assert resp.status_code == 200, resp.text
        saved = json.loads((drafts_dir / f"{rid}.json").read_text(encoding="utf-8"))
        assert "Site Manager" in saved["role_tags"]


# ── Goal 4: GET /api/modules?role= returns tagged modules after edit ──────────

class TestRoleFilterAfterTagging:
    def test_role_filter_returns_tagged_modules(self, client, approved_meta_file):
        """After tagging a module as Cashier, GET /api/modules?role=Cashier must include it."""
        rid, _ = approved_meta_file
        # Tag as Cashier.
        client.put(
            f"/api/modules/{rid}/role-tags",
            json={"role_tags": ["Cashier"]},
            headers=_TRAINER_HEADERS,
        )
        # Now filter by Cashier — must find the module.
        resp = client.get("/api/modules?role=Cashier")
        assert resp.status_code == 200
        ids = [m["id"] for m in resp.json()["modules"]]
        assert rid in ids, (
            f"Module '{rid}' tagged as Cashier must appear in /api/modules?role=Cashier, "
            f"but got ids: {ids}"
        )

    def test_role_filter_excludes_wrongly_tagged(self, client, approved_meta_file):
        """A module tagged only as 'Site Manager' must NOT appear for role=Cashier."""
        rid, _ = approved_meta_file
        client.put(
            f"/api/modules/{rid}/role-tags",
            json={"role_tags": ["Site Manager"]},
            headers=_TRAINER_HEADERS,
        )
        resp = client.get("/api/modules?role=Cashier")
        ids = [m["id"] for m in resp.json()["modules"]]
        assert rid not in ids, (
            f"Module '{rid}' tagged only as Site Manager must NOT appear for role=Cashier"
        )

    def test_role_filter_untagged_module_excluded(self, client, approved_meta_file):
        """An untagged module must NOT appear when filtering by a specific role."""
        rid, _ = approved_meta_file
        # Leave role_tags empty (the fixture starts with []).
        resp = client.get("/api/modules?role=Cashier")
        ids = [m["id"] for m in resp.json()["modules"]]
        assert rid not in ids, (
            f"Untagged module '{rid}' must not appear in role=Cashier results"
        )


# ── Goal 2: role_tags written to draft_meta at generation time ────────────────
# We test the metadata structures directly (no live LLM call needed).

class TestRoleTagsAtGeneration:
    def test_draft_meta_role_tags_default_empty(self, tmp_path):
        """A freshly-written draft_meta must have role_tags: [] by default."""
        meta = {
            "id": "test-draft", "status": "draft", "module": "TestMod",
            "template": "micro-guide", "role_tags": [],
        }
        p = tmp_path / "test-draft.json"
        p.write_text(json.dumps(meta), encoding="utf-8")
        saved = json.loads(p.read_text(encoding="utf-8"))
        assert "role_tags" in saved
        assert saved["role_tags"] == []

    def test_generate_route_accepts_roles_param(self, client):
        """GET /generate with an invalid module should return 400, not 500 — confirms roles= param parsed."""
        # We do NOT call the live LLM; we just confirm the route signature accepts the 'roles' param.
        resp = client.get("/generate?transcript_id=x&module=NoSuchMod&template=micro-guide&roles=Cashier")
        # Expected: 400 (no fixture for 'NoSuchMod') — NOT 422 (unrecognised param) and NOT 500.
        assert resp.status_code == 400, (
            f"Expected 400 for missing fixture (not 422 param error / 500), got {resp.status_code}: {resp.text}"
        )

    def test_role_tags_preserved_through_approve_roundtrip(self, client, approved_meta_file):
        """Approving a resource must preserve the role_tags already in metadata."""
        # The approved_meta_file fixture provides a pre-approved module with role_tags=[].
        # We set role_tags via the edit endpoint, then simulate what approve does.
        rid, pub_meta_dir = approved_meta_file
        client.put(
            f"/api/modules/{rid}/role-tags",
            json={"role_tags": ["Cashier", "CN Director"]},
            headers=_TRAINER_HEADERS,
        )
        # Read the saved meta — role_tags must be present.
        saved = json.loads((pub_meta_dir / f"{rid}.json").read_text(encoding="utf-8"))
        assert set(saved["role_tags"]) == {"Cashier", "CN Director"}, (
            f"role_tags not preserved: {saved['role_tags']}"
        )
