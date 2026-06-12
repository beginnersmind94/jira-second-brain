"""G-Rule-3 + G-Rule-4 — Model pinning and cost-per-artifact logging tests.

Run from learning-agent/ with:
    python -m pytest eval/test_model_pinning.py -v

Test inventory (5 tests):

  1. SHOULD-NOT-OCCUR: no 'fable' model string anywhere in Python files.
     Fable 5 free window closes Jun 22; any call defaulting to it is a ~10x
     cost jump the day billing starts.

  2. SHOULD-NOT-OCCUR: every messages.create / ClaudeAgentOptions call that
     exists in the codebase has an explicit model= pin. Unpinned calls silently
     pick the API default, which could become Fable 5 after the free window.

  3. Every explicit model= string in Python files uses an approved model id
     (claude-sonnet-4-6 or claude-haiku-4-5-20251001 for lightweight classifiers).
     No partial strings like 'claude-sonnet' without a version suffix.

  4. Metadata schema: published/metadata/*.json files that have generation_stats
     must contain a 'model' field matching an approved string.

  5. GET /api/stats/content returns avg_gen_seconds and total_cost_usd fields
     (may be None if no data yet — presence is required, not truthiness).

All tests are deterministic and offline — no SDK, no Jira, no LLM calls.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Make learning-agent/ importable regardless of cwd.
_LA = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_LA))

# Approved model strings (G-Rule-3).
_APPROVED_MODELS = {
    "claude-sonnet-4-6",            # primary — all generation calls
    "claude-haiku-4-5-20251001",    # lightweight classifiers only
}

# Python files to scan (all .py under learning-agent/, excluding __pycache__ and .venv).
def _py_files() -> list[Path]:
    return [
        p for p in _LA.rglob("*.py")
        if "__pycache__" not in p.parts and ".venv" not in p.parts
    ]


# ---------------------------------------------------------------------------
# Test 1 — SHOULD-NOT-OCCUR: no 'fable' in any model= string
# ---------------------------------------------------------------------------

class TestNoFableModel:
    """G-Rule-3: Fable 5 must not appear in any model= call.

    SHOULD-NOT-OCCUR: any 'fable' reference in a model= argument would mean
    a call could resolve to claude-fable-5, which is off the approved list and
    would cause a ~10x cost jump the day the free window closes (Jun 22).
    """

    def test_no_fable_model_string_anywhere(self):
        """Grep all .py files for any model string containing 'fable' (case-insensitive).

        A hit here means the free window is wired into production code — the
        billing clock is ticking and the cost jump happens silently.
        """
        fable_re = re.compile(r'model\s*=\s*["\'][^"\']*fable[^"\']*["\']', re.IGNORECASE)
        hits: list[str] = []
        for p in _py_files():
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if fable_re.search(line):
                    hits.append(f"{p.relative_to(_LA)}:{i}: {line.strip()}")

        assert not hits, (
            "SHOULD-NOT-OCCUR (G-Rule-3): Found 'fable' in model= argument(s). "
            "Fable 5 free window closes Jun 22 — these calls will silently become ~10x "
            "more expensive after billing starts.\n"
            "Occurrences:\n" + "\n".join(hits)
        )

    def test_no_fable_anywhere_in_codebase(self):
        """Broader check: 'fable' must not appear in any model= string value
        (claude-fable-*, fable-5, etc.) anywhere in the codebase.

        This checks model= argument values only — prose comments explaining
        the G-Rule-3 billing risk are fine and are excluded from the scan.
        The scan looks for the pattern only inside quoted string literals
        that follow model=, not in comments or explanatory text.
        """
        # Match model='...' or model="..." where the value contains 'fable'
        fable_in_model_re = re.compile(
            r"""model\s*=\s*["'][^"']*fable[^"']*["']""", re.IGNORECASE
        )
        hits: list[str] = []
        for p in _py_files():
            # Skip this test file itself.
            if p.name == "test_model_pinning.py":
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if fable_in_model_re.search(line):
                    hits.append(f"{p.relative_to(_LA)}:{i}: {line.strip()}")

        assert not hits, (
            "SHOULD-NOT-OCCUR (G-Rule-3): Fable model string found in a model= "
            "argument. This is a live API call that will silently switch to ~10x "
            "cost after Jun 22. Remove before the billing window closes.\n"
            "Occurrences:\n" + "\n".join(hits)
        )


# ---------------------------------------------------------------------------
# Test 2 — SHOULD-NOT-OCCUR: no unpinned messages.create / ClaudeAgentOptions
# ---------------------------------------------------------------------------

class TestNoPinnedModelMissing:
    """G-Rule-3: every API call must have an explicit model= pin.

    SHOULD-NOT-OCCUR: a ClaudeAgentOptions() or messages.create() call without
    model= will use the SDK/API default — which could silently switch to an
    expensive model after a version bump or pricing change.
    """

    def test_claude_agent_options_always_has_model(self):
        """Every ClaudeAgentOptions(...) call must contain model= on the same
        or a nearby line (within 5 lines of the opening paren).
        """
        call_re = re.compile(r"ClaudeAgentOptions\s*\(")
        model_re = re.compile(r"\bmodel\s*=")
        unpinned: list[str] = []

        for p in _py_files():
            try:
                lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for i, line in enumerate(lines):
                if call_re.search(line):
                    # Check the call line and the next 5 lines for a model= argument.
                    window = "\n".join(lines[i: i + 6])
                    if not model_re.search(window):
                        unpinned.append(f"{p.relative_to(_LA)}:{i+1}: {line.strip()}")

        assert not unpinned, (
            "SHOULD-NOT-OCCUR (G-Rule-3): ClaudeAgentOptions() call(s) without "
            "an explicit model= pin. Add model='claude-sonnet-4-6' to each.\n"
            "Unpinned calls:\n" + "\n".join(unpinned)
        )

    def test_messages_create_always_has_model(self):
        """Every .messages.create( call must have a model= argument within 5 lines."""
        call_re = re.compile(r"\.messages\.create\s*\(")
        model_re = re.compile(r"\bmodel\s*=")
        unpinned: list[str] = []

        for p in _py_files():
            try:
                lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for i, line in enumerate(lines):
                if call_re.search(line):
                    window = "\n".join(lines[i: i + 6])
                    if not model_re.search(window):
                        unpinned.append(f"{p.relative_to(_LA)}:{i+1}: {line.strip()}")

        assert not unpinned, (
            "SHOULD-NOT-OCCUR (G-Rule-3): .messages.create() call(s) without "
            "an explicit model= pin.\n"
            "Unpinned calls:\n" + "\n".join(unpinned)
        )


# ---------------------------------------------------------------------------
# Test 3 — Every explicit model= string uses an approved model id
# ---------------------------------------------------------------------------

class TestApprovedModelStrings:
    """G-Rule-3: all model= strings must be from the approved set.

    Approved set: claude-sonnet-4-6 (primary), claude-haiku-4-5-20251001
    (lightweight classifiers). No partial strings, no version-less aliases.
    """

    def test_all_model_strings_are_approved(self):
        """Extract every model='...' string from Python files and check approval."""
        # Matches model="..." or model='...' with any content.
        model_val_re = re.compile(r"""model\s*=\s*["']([^"']+)["']""")
        unapproved: list[str] = []

        for p in _py_files():
            # Exclude test file itself (has approved strings as test data).
            if p.name == "test_model_pinning.py":
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                for m in model_val_re.finditer(line):
                    val = m.group(1)
                    # Skip non-model model= arguments (e.g. Django model= in form fields).
                    if not val.startswith("claude"):
                        continue
                    if val not in _APPROVED_MODELS:
                        unapproved.append(
                            f"{p.relative_to(_LA)}:{i}: model={val!r} — "
                            f"not in approved set {_APPROVED_MODELS}"
                        )

        assert not unapproved, (
            "G-Rule-3 violation: unapproved claude model string(s) found. "
            "Use 'claude-sonnet-4-6' (primary) or 'claude-haiku-4-5-20251001' "
            "(lightweight classifiers only).\n"
            "Violations:\n" + "\n".join(unapproved)
        )

    def test_no_versionless_model_strings(self):
        """Reject model strings like 'claude-sonnet' without a version suffix.

        A version-less string resolves to whatever the API considers 'latest' —
        which can silently upgrade to a more expensive model on the next release.
        """
        versionless_re = re.compile(
            r"""model\s*=\s*["'](claude-(?:sonnet|haiku|opus|fable)["'])""",
            re.IGNORECASE
        )
        hits: list[str] = []
        for p in _py_files():
            if p.name == "test_model_pinning.py":
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if versionless_re.search(line):
                    hits.append(f"{p.relative_to(_LA)}:{i}: {line.strip()}")

        assert not hits, (
            "G-Rule-3: version-less model string(s) found. Use the full versioned "
            "id (e.g. 'claude-sonnet-4-6', not 'claude-sonnet').\n"
            "Hits:\n" + "\n".join(hits)
        )


# ---------------------------------------------------------------------------
# Test 4 — generation_stats.model must be an approved string
# ---------------------------------------------------------------------------

class TestMetadataGenerationStats:
    """G-Rule-4: metadata files with generation_stats must have an approved model.

    When generation_stats is written by _stream_celld or _stream_celld_transcript,
    it must record model='claude-sonnet-4-6'. If the model field is wrong, the
    cost logged in token_cost_usd was computed against the wrong pricing rates.
    """

    def test_generation_stats_model_is_approved(self):
        """All drafts/*.json files that have generation_stats.model must use
        an approved model string.
        """
        drafts_dir = _LA / "drafts"
        if not drafts_dir.exists():
            pytest.skip("drafts/ directory does not exist — no metadata to check")

        violations: list[str] = []
        checked = 0
        for mf in drafts_dir.glob("*.json"):
            if mf.name.endswith(".eval.json"):
                continue
            try:
                meta = json.loads(mf.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            gs = meta.get("generation_stats")
            if not gs or not isinstance(gs, dict):
                continue
            checked += 1
            model_val = gs.get("model")
            if model_val and model_val not in _APPROVED_MODELS:
                violations.append(
                    f"drafts/{mf.name}: generation_stats.model={model_val!r} "
                    f"not in approved set {_APPROVED_MODELS}"
                )

        if checked == 0:
            pytest.skip(
                "No drafts/*.json files have generation_stats yet "
                "(pre-dating G-Rule-4 logging — expected for legacy guides)"
            )

        assert not violations, (
            "G-Rule-4: generation_stats.model is not an approved string in "
            f"{len(violations)} metadata file(s). The token_cost_usd was "
            "computed against the wrong pricing rates.\n"
            "Violations:\n" + "\n".join(violations)
        )

    def test_generation_stats_has_required_fields(self):
        """generation_stats blocks, when present, must have gen_seconds,
        token_cost_usd, and model fields (the Beat 3 scoreboard needs these).
        """
        drafts_dir = _LA / "drafts"
        if not drafts_dir.exists():
            pytest.skip("drafts/ directory does not exist")

        missing_fields: list[str] = []
        checked = 0
        for mf in drafts_dir.glob("*.json"):
            if mf.name.endswith(".eval.json"):
                continue
            try:
                meta = json.loads(mf.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            gs = meta.get("generation_stats")
            if not gs or not isinstance(gs, dict):
                continue
            checked += 1
            for field in ("gen_seconds", "token_cost_usd", "model"):
                if field not in gs:
                    missing_fields.append(f"drafts/{mf.name}: missing {field}")

        if checked == 0:
            pytest.skip("No generation_stats blocks to check yet")

        assert not missing_fields, (
            "G-Rule-4: generation_stats block(s) missing required fields. "
            "Beat 3 scoreboard reads gen_seconds + token_cost_usd + model.\n"
            "Missing:\n" + "\n".join(missing_fields)
        )


# ---------------------------------------------------------------------------
# Test 5 — GET /api/stats/content returns G-Rule-4 fields
# ---------------------------------------------------------------------------

class TestStatContentGRule4Fields:
    """G-Rule-4: /api/stats/content must return avg_gen_seconds and total_cost_usd.

    These fields power the Beat 3 scoreboard. They may be None when no AI-generated
    guides with generation_stats exist yet — but the fields themselves must always
    be present in the response so the JS doesn't throw on missing keys.
    """

    def _make_stats_app(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        import demo_app

        mini = FastAPI()
        mini.add_api_route("/api/stats/content", demo_app.stats_content, methods=["GET"])
        return TestClient(mini, raise_server_exceptions=True)

    def test_avg_gen_seconds_field_present(self):
        """avg_gen_seconds must be present (may be seeded or real; never absent)."""
        client = self._make_stats_app()
        data = client.get("/api/stats/content").json()

        assert "avg_gen_seconds" in data, (
            "G-Rule-4: 'avg_gen_seconds' field missing from /api/stats/content. "
            "The Beat 3 scoreboard reads this field — a missing key crashes the JS."
        )

    def test_total_cost_usd_field_present(self):
        """total_cost_usd must be present (the real measured sum, or seeded fallback).

        SHOULD-NOT-OCCUR: a missing total_cost_usd means the cost transparency
        story at Beat 3 has no number — the 'X cents per guide' pitch falls flat.
        """
        client = self._make_stats_app()
        data = client.get("/api/stats/content").json()

        assert "total_cost_usd" in data, (
            "SHOULD-NOT-OCCUR (G-Rule-4): 'total_cost_usd' field missing from "
            "/api/stats/content. Beat 3 needs this for the cost-per-artifact story."
        )

    def test_resources_with_cost_data_field_present(self):
        """resources_with_cost_data must be present and be a non-negative integer."""
        client = self._make_stats_app()
        data = client.get("/api/stats/content").json()

        assert "resources_with_cost_data" in data, (
            "G-Rule-4: 'resources_with_cost_data' field missing from response. "
            "This count tells the dashboard how many real cost readings exist."
        )
        count = data["resources_with_cost_data"]
        assert isinstance(count, int) and count >= 0, (
            f"resources_with_cost_data must be a non-negative int, got {count!r}"
        )

    def test_model_pinned_field_present(self):
        """_model_pinned must be present and equal 'claude-sonnet-4-6'.

        Structural pin: if anyone changes the pinned model, this field changes
        and the test catches it immediately — before the cost jump is silent.
        """
        client = self._make_stats_app()
        data = client.get("/api/stats/content").json()

        assert "_model_pinned" in data, (
            "G-Rule-3: '_model_pinned' field missing from /api/stats/content. "
            "This field must name the pinned model for on-stage auditability."
        )
        assert data["_model_pinned"] == "claude-sonnet-4-6", (
            f"G-Rule-3: _model_pinned={data['_model_pinned']!r} but expected "
            "'claude-sonnet-4-6'. If the approved model changed, update G-Rule-3 docs "
            "and this test in the same commit."
        )

    def test_cost_note_is_none_or_string(self):
        """_cost_note must be None or a non-empty string (never an empty string)."""
        client = self._make_stats_app()
        data = client.get("/api/stats/content").json()

        # _cost_note is optional in the sense that it may be None.
        # When it IS set, it must not be empty.
        assert "_cost_note" in data, (
            "G-Rule-4: '_cost_note' key missing from response. "
            "It must be present (None or a warning string)."
        )
        note = data["_cost_note"]
        if note is not None:
            assert isinstance(note, str) and len(note.strip()) > 0, (
                f"_cost_note must be None or a non-empty string, got {note!r}"
            )
