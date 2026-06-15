"""project_workspace_store.py — Implementation Workspace (Epic: implementation-workspace, STORY-001).

The per-district onboarding **project workspace**: a milestone checklist, tasks/follow-ups,
notes, and an activity log. This is the BRD's MVP onboarding-management layer (FR-CP-05 checklist
steps, FR-RP-03 milestone progress, FR-IN-06 event log) that the build had only as a decorative
stage stepper.

Demo-real: seeded, but every mutation persists. Storage matches the existing store pattern:
    data/workspaces/<safe-district-id>.json

Persisted raw shape (what's on disk):
    {district_id, template, items: {<item_id>: {status, done_at}}, tasks: [..], notes: [..], activity: [..]}

The READ payload (get_workspace) is computed from the template + raw overrides — milestones with
per-item + per-milestone progress, overall %, derived status, current milestone, tasks, notes,
activity. See docs/features/implementation-workspace/EPIC.md → "API & Data Contract (LOCKED)".

Seed is SYNTHETIC and not the authoritative SchoolCafe/PrimeroEdge runbook — the real one is
co-authored with CS after approval (see epic Scope).
"""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

_WS_DIR = Path(__file__).resolve().parent / "data" / "workspaces"

# ── Synthetic onboarding template (milestone -> items as (id, label, owner)) ──
# owner ∈ {"Cybersoft", "District", "Shared"}. The "training" milestone is auto-fed
# from completion data in a later story; seeded statically here.
_TEMPLATE = [
    {"key": "kickoff", "label": "Kickoff & Discovery", "items": [
        ("kickoff-call", "Kickoff call held", "Cybersoft"),
        ("kickoff-stakeholders", "Stakeholders identified", "Shared"),
        ("kickoff-plan", "Implementation plan shared", "Cybersoft"),
    ]},
    {"key": "data", "label": "Data Migration", "items": [
        ("data-sites", "Site list imported", "District"),
        ("data-roster", "Staff roster imported", "District"),
        ("data-validate", "Historical data validated", "Shared"),
    ]},
    {"key": "config", "label": "Configuration", "items": [
        ("config-prices", "Meal prices configured", "District"),
        ("config-eligibility", "Eligibility rules set", "Shared"),
        ("config-pos", "POS hardware check", "District"),
    ]},
    {"key": "training", "label": "Staff Training", "auto": True, "items": [
        ("train-cashiers", "Cashiers trained", "District"),
        ("train-managers", "Site managers trained", "District"),
        ("train-director", "CN Director onboarded", "District"),
    ]},
    {"key": "uat", "label": "UAT & Go-Live", "items": [
        ("uat-signoff", "UAT sign-off", "Shared"),
        ("uat-date", "Go-live date confirmed", "Cybersoft"),
        ("uat-golive", "Go-live", "Shared"),
    ]},
]

_MILESTONE_ORDER = [m["key"] for m in _TEMPLATE]
_ITEM_INDEX: dict[str, dict] = {}
for _m in _TEMPLATE:
    for _iid, _label, _owner in _m["items"]:
        _ITEM_INDEX[_iid] = {"label": _label, "owner": _owner, "milestone": _m["key"]}

# ── Per-district seed profiles — each demo district at a DISTINCT, believable point ──
# done_through: every item up to & including this milestone is done.
# extra_done: individual items beyond that also done. blocked: items flagged blocked.
_SEED_PROFILES: dict[str, dict] = {
    "houston-isd": {"done_through": "data", "extra_done": ["config-prices", "config-eligibility"]},  # mid-Configuration
    "aldine-isd":  {"done_through": "kickoff", "extra_done": ["data-sites"], "blocked": ["data-roster"]},  # blocked on Data Migration
    "klein-isd":   {"done_through": "training", "extra_done": ["uat-signoff", "uat-date"]},  # near Go-Live
}

# Seeded tasks / notes per district (synthetic). Fixed dates so seeds are deterministic.
_SEED_TASKS: dict[str, list] = {
    "houston-isd": [{"title": "Chase POS vendor on terminal delivery", "owner": "District", "due": "2026-06-18"}],
    "aldine-isd":  [{"title": "Walk Aldine through Direct Certification import", "owner": "Cybersoft", "due": "2026-06-16"}],
    "klein-isd":   [{"title": "Confirm go-live comms with CN Director", "owner": "Shared", "due": "2026-06-19"}],
}
_SEED_NOTES: dict[str, list] = {
    "houston-isd": [{"body": "Config call went well — meal prices + eligibility done. POS check pending vendor.", "at": "2026-06-12T15:10:00+00:00"}],
    "aldine-isd":  [{"body": "Staff roster import failing on Direct Cert rows. SM aware; scheduling a walkthrough.", "at": "2026-06-13T09:40:00+00:00"}],
    "klein-isd":   [{"body": "UAT signed off. Go-live date locked; just need final go-live confirmation.", "at": "2026-06-11T16:00:00+00:00"}],
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe(s: str) -> str:
    return re.sub(r"[^\w\-]", "_", s)[:80]


def _path(district_id: str) -> Path:
    return _WS_DIR / f"{_safe(district_id)}.json"


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


# ── Seeding ───────────────────────────────────────────────────────────────────

def _profile_for(district_id: str) -> dict:
    """Return the seed profile for a district. Known demo stars get hand-tuned
    profiles; any other district id gets a deterministic mid-onboarding profile so
    a workspace is NEVER empty."""
    if district_id in _SEED_PROFILES:
        return _SEED_PROFILES[district_id]
    h = int(hashlib.md5(district_id.encode()).hexdigest(), 16)
    through = ["kickoff", "data", "config"][h % 3]
    return {"done_through": through, "extra_done": [], "blocked": []}


def _seed_raw(district_id: str) -> dict:
    prof = _profile_for(district_id)
    through_idx = _MILESTONE_ORDER.index(prof.get("done_through", "kickoff"))
    done, blocked = set(prof.get("extra_done", [])), set(prof.get("blocked", []))
    for m in _TEMPLATE:
        if _MILESTONE_ORDER.index(m["key"]) <= through_idx:
            for iid, _, _ in m["items"]:
                done.add(iid)
    done -= blocked  # a blocked item is never also done

    items: dict[str, dict] = {}
    for iid in done:
        items[iid] = {"status": "done", "done_at": "2026-06-12T12:00:00+00:00"}
    for iid in blocked:
        items[iid] = {"status": "blocked", "done_at": None}

    activity = [{"id": _new_id(), "type": "seed", "label": "Onboarding project created", "actor": "System", "at": "2026-06-10T08:00:00+00:00"}]
    notes = [{"id": _new_id(), "subject_type": "district", "subject_id": district_id,
              "body": n["body"], "author": "Sam Rivera", "created_at": n["at"]}
             for n in _SEED_NOTES.get(district_id, [])]
    tasks = [{"id": _new_id(), "title": t["title"], "owner": t["owner"], "due": t["due"],
              "status": "open", "created_at": "2026-06-12T12:00:00+00:00"}
             for t in _SEED_TASKS.get(district_id, [])]

    return {"district_id": district_id, "template": "schoolcafe-onboarding",
            "items": items, "tasks": tasks, "notes": notes, "activity": activity}


def _read_raw(district_id: str) -> dict:
    p = _path(district_id)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    raw = _seed_raw(district_id)
    _write_raw(district_id, raw)
    return raw


def _write_raw(district_id: str, raw: dict) -> None:
    _WS_DIR.mkdir(parents=True, exist_ok=True)
    _path(district_id).write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")


# ── Read payload (computed) ─────────────────────────────────────────────────────

def _compute(raw: dict) -> dict:
    overrides = raw.get("items", {})
    milestones, done_total, item_total, any_blocked, current = [], 0, 0, False, None
    for m in _TEMPLATE:
        items, m_done = [], 0
        for iid, label, owner in m["items"]:
            ov = overrides.get(iid, {})
            status = ov.get("status", "todo")
            if status == "done":
                m_done += 1
            if status == "blocked":
                any_blocked = True
            items.append({"id": iid, "label": label, "owner": owner, "status": status,
                          "done_at": ov.get("done_at"), "source": "auto" if m.get("auto") else "manual"})
        n = len(items)
        pct = round(100 * m_done / n) if n else 0
        done_total += m_done
        item_total += n
        if current is None and m_done < n:
            current = m["key"]
        milestones.append({"key": m["key"], "label": m["label"], "auto": bool(m.get("auto")),
                           "pct": pct, "done": m_done, "total": n, "items": items})
    overall = round(100 * done_total / item_total) if item_total else 0
    status = "blocked" if any_blocked else ("at_risk" if overall < 60 else "on_track")
    return {
        "district_id": raw.get("district_id"),
        "template": raw.get("template"),
        "milestones": milestones,
        "overall_pct": overall,
        "status": status,
        "current_milestone": current or _MILESTONE_ORDER[-1],
        "tasks": raw.get("tasks", []),
        "notes": sorted(raw.get("notes", []), key=lambda n: n.get("created_at", ""), reverse=True),
        "activity": sorted(raw.get("activity", []), key=lambda a: a.get("at", ""), reverse=True),
    }


def get_workspace(district_id: str) -> dict:
    return _compute(_read_raw(district_id))


# ── Mutations (all persist + log activity) ──────────────────────────────────────

def _log(raw: dict, type_: str, label: str, actor: str) -> None:
    raw.setdefault("activity", []).append(
        {"id": _new_id(), "type": type_, "label": label, "actor": actor or "Trainer", "at": _now()})


def toggle_item(district_id: str, item_id: str, actor: str = "") -> dict:
    if item_id not in _ITEM_INDEX:
        raise KeyError(item_id)
    raw = _read_raw(district_id)
    items = raw.setdefault("items", {})
    cur = items.get(item_id, {}).get("status", "todo")
    new = "todo" if cur == "done" else "done"
    items[item_id] = {"status": new, "done_at": _now() if new == "done" else None}
    label = _ITEM_INDEX[item_id]["label"]
    _log(raw, "item_toggle", f"{'Checked' if new == 'done' else 'Unchecked'} “{label}”", actor)
    _write_raw(district_id, raw)
    return _compute(raw)


def add_task(district_id: str, title: str, owner: str = "Shared", due: str = "", actor: str = "") -> dict:
    title = (title or "").strip()
    if not title:
        raise ValueError("title required")
    raw = _read_raw(district_id)
    task = {"id": _new_id(), "title": title, "owner": owner or "Shared", "due": due,
            "status": "open", "created_at": _now()}
    raw.setdefault("tasks", []).append(task)
    _log(raw, "task_add", f"Added task “{title}”", actor)
    _write_raw(district_id, raw)
    return task


def toggle_task(district_id: str, task_id: str, actor: str = "") -> dict | None:
    raw = _read_raw(district_id)
    for t in raw.get("tasks", []):
        if t["id"] == task_id:
            t["status"] = "open" if t["status"] == "done" else "done"
            _log(raw, "task_toggle", f"{'Reopened' if t['status'] == 'open' else 'Completed'} task “{t['title']}”", actor)
            _write_raw(district_id, raw)
            return t
    return None


def add_note(district_id: str, body: str, subject_type: str = "district",
             subject_id: str = "", author: str = "") -> dict:
    body = (body or "").strip()
    if not body:
        raise ValueError("body required")
    raw = _read_raw(district_id)
    note = {"id": _new_id(), "subject_type": subject_type or "district",
            "subject_id": subject_id or district_id, "body": body[:2000],
            "author": author or "Trainer", "created_at": _now()}
    raw.setdefault("notes", []).append(note)
    _log(raw, "note_add", "Added a note", author)
    _write_raw(district_id, raw)
    return note
