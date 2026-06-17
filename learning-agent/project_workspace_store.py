"""project_workspace_store.py — Implementation Workspace (Epic: implementation-workspace, STORY-001).

The per-district onboarding project workspace: a milestone checklist, tasks/follow-ups,
notes, and an activity log.

Storage shape (persisted on disk):
    {district_id, template, sections: [{key, label, auto, items: [{id, label, owner, status, done_at}]}],
     tasks: [..], notes: [..], activity: [..]}

Legacy shape (migrated transparently on first read):
    {district_id, template, items: {<item_id>: {status, done_at}}, tasks, notes, activity}
"""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

_WS_DIR = Path(__file__).resolve().parent / "data" / "workspaces"

# ── Template — used ONLY for seeding and legacy migration ──────────────────────
# `weight` is the milestone's share of go-live readiness (critical-path weighting,
# NOT flat item count): the data import, training, and UAT/go-live milestones carry
# more readiness weight than kickoff. `role` on an auto item maps it to a roster role
# so the frontend can source "{done}/{total} {role} complete" from real completion.
_TEMPLATE = [
    {"key": "kickoff", "label": "Kickoff & Discovery", "weight": 1, "items": [
        ("kickoff-call", "Kickoff call held", "Cybersoft"),
        ("kickoff-stakeholders", "Stakeholders identified", "Shared"),
        ("kickoff-plan", "Implementation plan shared", "Cybersoft"),
    ]},
    {"key": "data", "label": "Data Migration", "weight": 3, "items": [
        ("data-sites", "Site list imported", "District"),
        ("data-roster", "Staff roster imported", "District"),
        ("data-validate", "Historical data validated", "Shared"),
    ]},
    {"key": "config", "label": "Configuration", "weight": 2, "items": [
        ("config-prices", "Meal prices configured", "District"),
        ("config-eligibility", "Eligibility rules set", "Shared"),
        ("config-pos", "POS hardware check", "District"),
    ]},
    {"key": "training", "label": "Staff Training", "auto": True, "weight": 3, "items": [
        ("train-cashiers", "Cashiers trained", "District", "Cashier"),
        ("train-managers", "Site managers trained", "District", "Site Manager"),
        ("train-director", "CN Director onboarded", "District", "CN Director"),
    ]},
    {"key": "uat", "label": "UAT & Go-Live", "weight": 3, "items": [
        ("uat-signoff", "UAT sign-off", "Shared"),
        ("uat-date", "Go-live date confirmed", "Cybersoft"),
        ("uat-golive", "Go-live", "Shared"),
    ]},
]


def _tmpl_item(tup):
    """Template item tuples are (id, label, owner) or (id, label, owner, role)."""
    iid, label, owner = tup[0], tup[1], tup[2]
    role = tup[3] if len(tup) > 3 else None
    return iid, label, owner, role

_SEED_PROFILES: dict[str, dict] = {
    "houston-isd": {"done_through": "data", "extra_done": ["config-prices", "config-eligibility"]},
    "aldine-isd":  {"done_through": "kickoff", "extra_done": ["data-sites"], "blocked": ["data-roster"]},
    "klein-isd":   {"done_through": "training", "extra_done": ["uat-signoff", "uat-date"]},
}

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


# ── Schema helpers ─────────────────────────────────────────────────────────────

def _hydrate_sections(raw: dict) -> list:
    """Build a sections list from the legacy items-dict + the template."""
    overrides = raw.get("items", {})
    sections = []
    for m in _TEMPLATE:
        items = []
        for tup in m["items"]:
            iid, label, owner, role = _tmpl_item(tup)
            ov = overrides.get(iid, {})
            status = ov.get("status", "todo")
            item: dict = {"id": iid, "label": label, "owner": owner,
                          "status": status, "done_at": ov.get("done_at"),
                          "due": ov.get("due", ""), "updated_at": ov.get("done_at")}
            if role:
                item["role"] = role
            if status == "blocked":
                item["reason"] = ov.get("reason", "")
                item["blocked_since"] = ov.get("blocked_since")
            items.append(item)
        sections.append({"key": m["key"], "label": m["label"],
                         "auto": bool(m.get("auto")), "weight": m.get("weight", 1),
                         "items": items})
    return sections


def _ensure_sections(raw: dict) -> None:
    """Migrate legacy {items: {...}} format to {sections: [...]} in-place."""
    if "sections" not in raw:
        raw["sections"] = _hydrate_sections(raw)


def _find_item(raw: dict, item_id: str) -> tuple[dict | None, dict | None]:
    for sec in raw.get("sections", []):
        for it in sec.get("items", []):
            if it["id"] == item_id:
                return sec, it
    return None, None


# ── Seeding ────────────────────────────────────────────────────────────────────

def _profile_for(district_id: str) -> dict:
    if district_id in _SEED_PROFILES:
        return _SEED_PROFILES[district_id]
    h = int(hashlib.md5(district_id.encode()).hexdigest(), 16)
    through = ["kickoff", "data", "config"][h % 3]
    return {"done_through": through, "extra_done": [], "blocked": []}


def _seed_raw(district_id: str) -> dict:
    prof = _profile_for(district_id)
    milestone_order = [m["key"] for m in _TEMPLATE]
    through_idx = milestone_order.index(prof.get("done_through", "kickoff"))
    done, blocked = set(prof.get("extra_done", [])), set(prof.get("blocked", []))
    for m in _TEMPLATE:
        if milestone_order.index(m["key"]) <= through_idx:
            for tup in m["items"]:
                done.add(tup[0])
    done -= blocked

    sections = []
    for m in _TEMPLATE:
        items = []
        for tup in m["items"]:
            iid, label, owner, role = _tmpl_item(tup)
            if iid in done:
                item = {"id": iid, "label": label, "owner": owner, "status": "done",
                        "done_at": "2026-06-12T12:00:00+00:00", "due": "",
                        "updated_at": "2026-06-12T12:00:00+00:00"}
            elif iid in blocked:
                item = {"id": iid, "label": label, "owner": owner, "status": "blocked",
                        "done_at": None, "due": "", "updated_at": "2026-06-13T09:40:00+00:00",
                        "reason": "Import failing on Direct Cert rows — see notes.",
                        "blocked_since": "2026-06-13T09:40:00+00:00"}
            else:
                item = {"id": iid, "label": label, "owner": owner, "status": "todo",
                        "done_at": None, "due": "", "updated_at": None}
            if role:
                item["role"] = role
            items.append(item)
        sections.append({"key": m["key"], "label": m["label"],
                         "auto": bool(m.get("auto")), "weight": m.get("weight", 1),
                         "items": items})

    activity = [{"id": _new_id(), "type": "seed", "label": "Onboarding project created",
                 "actor": "System", "at": "2026-06-10T08:00:00+00:00"}]
    notes = [{"id": _new_id(), "subject_type": "district", "subject_id": district_id,
              "body": n["body"], "author": "Sam Rivera", "created_at": n["at"]}
             for n in _SEED_NOTES.get(district_id, [])]
    tasks = [{"id": _new_id(), "title": t["title"], "owner": t["owner"], "due": t["due"],
              "status": "open", "created_at": "2026-06-12T12:00:00+00:00"}
             for t in _SEED_TASKS.get(district_id, [])]

    return {"district_id": district_id, "template": "schoolcafe-onboarding",
            "sections": sections, "tasks": tasks, "notes": notes, "activity": activity}


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


# ── Read payload (computed from sections) ──────────────────────────────────────

def _compute(raw: dict) -> dict:
    _ensure_sections(raw)
    milestones, current = [], None
    weighted_num, weighted_den = 0.0, 0.0
    any_blocked = False
    for sec in raw["sections"]:
        items_out, m_done = [], 0
        for it in sec.get("items", []):
            status = it.get("status", "todo")
            if status == "done":
                m_done += 1
            if status == "blocked":
                any_blocked = True
            items_out.append({"id": it["id"], "label": it["label"],
                              "owner": it.get("owner", "Shared"), "status": status,
                              "done_at": it.get("done_at"), "updated_at": it.get("updated_at"),
                              "due": it.get("due", ""), "reason": it.get("reason"),
                              "blocked_since": it.get("blocked_since"),
                              "nudged_at": it.get("nudged_at"), "role": it.get("role"),
                              "source": "auto" if sec.get("auto") else "manual"})
        n = len(items_out)
        pct = round(100 * m_done / n) if n else 0
        weight = sec.get("weight", 1)
        if n:
            weighted_num += weight * (m_done / n)
            weighted_den += weight
        if current is None and m_done < n:
            current = sec["key"]
        milestones.append({"key": sec["key"], "label": sec["label"],
                           "auto": sec.get("auto", False), "weight": weight,
                           "pct": pct, "done": m_done, "total": n, "items": items_out})
    last_key = raw["sections"][-1]["key"] if raw["sections"] else "uat"
    # Critical-path weighted readiness, NOT flat item count.
    overall = round(100 * weighted_num / weighted_den) if weighted_den else 0
    status = "blocked" if any_blocked else ("at_risk" if overall < 60 else "on_track")
    return {
        "district_id": raw.get("district_id"),
        "template": raw.get("template"),
        "milestones": milestones,
        "overall_pct": overall,
        "status": status,
        "current_milestone": current or last_key,
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


def _touch(it: dict) -> None:
    """Stamp last-updated. Called by every item mutation."""
    it["updated_at"] = _now()


def toggle_item(district_id: str, item_id: str, actor: str = "") -> dict:
    raw = _read_raw(district_id)
    _ensure_sections(raw)
    _, it = _find_item(raw, item_id)
    if it is None:
        raise KeyError(item_id)
    cur = it.get("status", "todo")
    new = "todo" if cur == "done" else "done"
    it["status"] = new
    it["done_at"] = _now() if new == "done" else None
    it.pop("blocked_since", None)
    _touch(it)
    _log(raw, "item_toggle", f"{'Checked' if new == 'done' else 'Unchecked'} “{it['label']}”", actor)
    _write_raw(district_id, raw)
    return _compute(raw)


def rename_item(district_id: str, item_id: str, new_label: str, actor: str = "") -> dict:
    new_label = (new_label or "").strip()
    if not new_label:
        raise ValueError("label required")
    raw = _read_raw(district_id)
    _ensure_sections(raw)
    _, it = _find_item(raw, item_id)
    if it is None:
        raise KeyError(item_id)
    old = it["label"]
    it["label"] = new_label
    _touch(it)
    _log(raw, "item_rename", f"Renamed “{old}” → “{new_label}”", actor)
    _write_raw(district_id, raw)
    return _compute(raw)


def set_item_status(district_id: str, item_id: str, status: str,
                    reason: str = "", actor: str = "") -> dict:
    if status not in ("todo", "done", "blocked"):
        raise ValueError(f"invalid status: {status}")
    raw = _read_raw(district_id)
    _ensure_sections(raw)
    _, it = _find_item(raw, item_id)
    if it is None:
        raise KeyError(item_id)
    was_blocked = it.get("status") == "blocked"
    it["status"] = status
    it["done_at"] = _now() if status == "done" else None
    if status == "blocked":
        it["reason"] = reason or ""
        if not was_blocked:
            it["blocked_since"] = _now()
        it.pop("nudged_at", None)
    else:
        it.pop("reason", None)
        it.pop("blocked_since", None)
        it.pop("nudged_at", None)
    _touch(it)
    _log(raw, "item_status", f"Marked “{it['label']}” as {status}", actor)
    _write_raw(district_id, raw)
    return _compute(raw)


def set_item_owner(district_id: str, item_id: str, owner: str, actor: str = "") -> dict:
    if owner not in ("Cybersoft", "District", "Shared"):
        raise ValueError(f"invalid owner: {owner}")
    raw = _read_raw(district_id)
    _ensure_sections(raw)
    _, it = _find_item(raw, item_id)
    if it is None:
        raise KeyError(item_id)
    old = it.get("owner", "Shared")
    it["owner"] = owner
    _touch(it)
    _log(raw, "item_reassign", f"Reassigned “{it['label']}” from {old} to {owner}", actor)
    _write_raw(district_id, raw)
    return _compute(raw)


def set_item_due(district_id: str, item_id: str, due: str, actor: str = "") -> dict:
    """Set or clear an item's due date (YYYY-MM-DD, or '' to clear)."""
    due = (due or "").strip()
    raw = _read_raw(district_id)
    _ensure_sections(raw)
    _, it = _find_item(raw, item_id)
    if it is None:
        raise KeyError(item_id)
    it["due"] = due
    _touch(it)
    _log(raw, "item_due", (f"Set due date on “{it['label']}” to {due}" if due
                           else f"Cleared due date on “{it['label']}”"), actor)
    _write_raw(district_id, raw)
    return _compute(raw)


def nudge_blocker(district_id: str, item_id: str, actor: str = "") -> dict:
    """Record an internal nudge to the blocked item's owner. This is an internal
    activity record — NOT an external notification (no channel to a customer/team
    exists yet). The caller surfaces honest copy ('nudge logged')."""
    raw = _read_raw(district_id)
    _ensure_sections(raw)
    _, it = _find_item(raw, item_id)
    if it is None:
        raise KeyError(item_id)
    if it.get("status") != "blocked":
        raise ValueError("item is not blocked")
    owner = it.get("owner", "Shared")
    it["nudged_at"] = _now()
    _touch(it)
    _log(raw, "blocker_nudge", f"Nudged {owner} about blocker “{it['label']}”", actor)
    _write_raw(district_id, raw)
    return _compute(raw)


def resolve_block(district_id: str, item_id: str, actor: str = "") -> dict:
    """Resolve a blocker: clear the blocked state and mark the item done."""
    raw = _read_raw(district_id)
    _ensure_sections(raw)
    _, it = _find_item(raw, item_id)
    if it is None:
        raise KeyError(item_id)
    if it.get("status") != "blocked":
        raise ValueError("item is not blocked")
    label = it["label"]
    it["status"] = "done"
    it["done_at"] = _now()
    it.pop("reason", None)
    it.pop("blocked_since", None)
    it.pop("nudged_at", None)
    _touch(it)
    _log(raw, "blocker_resolved", f"Resolved blocker — marked “{label}” done", actor)
    _write_raw(district_id, raw)
    return _compute(raw)


def add_item(district_id: str, section_key: str, label: str, owner: str = "Shared",
             due: str = "", actor: str = "") -> tuple[dict, dict]:
    label = (label or "").strip()
    if not label:
        raise ValueError("label required")
    raw = _read_raw(district_id)
    _ensure_sections(raw)
    sec = next((s for s in raw["sections"] if s["key"] == section_key), None)
    if sec is None:
        raise KeyError(section_key)
    item: dict = {"id": _new_id(), "label": label, "owner": owner or "Shared",
                  "status": "todo", "done_at": None, "due": (due or "").strip(),
                  "updated_at": _now()}
    sec["items"].append(item)
    _log(raw, "item_add", f"Added “{label}” to {sec['label']}", actor)
    _write_raw(district_id, raw)
    return item, _compute(raw)


def delete_item(district_id: str, item_id: str, actor: str = "") -> dict:
    raw = _read_raw(district_id)
    _ensure_sections(raw)
    sec, it = _find_item(raw, item_id)
    if it is None:
        raise KeyError(item_id)
    sec["items"] = [x for x in sec["items"] if x["id"] != item_id]
    _log(raw, "item_delete", f"Removed “{it['label']}”", actor)
    _write_raw(district_id, raw)
    return _compute(raw)


def reorder_item(district_id: str, item_id: str, section_key: str = "",
                 before_item_id: str = "", actor: str = "") -> dict:
    """Move an item to a new position. It is inserted immediately BEFORE
    `before_item_id`; if that is empty/unknown, it goes to the end of
    `section_key` (or its current section when section_key is empty)."""
    raw = _read_raw(district_id)
    _ensure_sections(raw)
    src_sec, it = _find_item(raw, item_id)
    if it is None:
        raise KeyError(item_id)
    dst_sec = next((s for s in raw["sections"] if s["key"] == section_key), None) or src_sec
    if dst_sec.get("auto"):
        raise ValueError("cannot reorder into an auto section")
    # Remove from its current section
    src_sec["items"] = [x for x in src_sec["items"] if x["id"] != item_id]
    # Insert before the target (recompute index after removal)
    dst_items = dst_sec["items"]
    idx = next((i for i, x in enumerate(dst_items) if x["id"] == before_item_id), len(dst_items))
    dst_items.insert(idx, it)
    _log(raw, "item_reorder", f"Reordered “{it['label']}”", actor)
    _write_raw(district_id, raw)
    return _compute(raw)


def add_section(district_id: str, label: str, actor: str = "") -> tuple[dict, dict]:
    label = (label or "").strip()
    if not label:
        raise ValueError("label required")
    raw = _read_raw(district_id)
    _ensure_sections(raw)
    sec: dict = {"key": _new_id(), "label": label, "auto": False, "items": []}
    raw["sections"].append(sec)
    _log(raw, "section_add", f"Added section “{label}”", actor)
    _write_raw(district_id, raw)
    return sec, _compute(raw)


def delete_section(district_id: str, section_key: str, actor: str = "") -> dict:
    raw = _read_raw(district_id)
    _ensure_sections(raw)
    sec = next((s for s in raw["sections"] if s["key"] == section_key), None)
    if sec is None:
        raise KeyError(section_key)
    raw["sections"] = [s for s in raw["sections"] if s["key"] != section_key]
    _log(raw, "section_delete", f"Removed section “{sec['label']}”", actor)
    _write_raw(district_id, raw)
    return _compute(raw)


def rename_section(district_id: str, section_key: str, new_label: str, actor: str = "") -> dict:
    new_label = (new_label or "").strip()
    if not new_label:
        raise ValueError("label required")
    raw = _read_raw(district_id)
    _ensure_sections(raw)
    sec = next((s for s in raw["sections"] if s["key"] == section_key), None)
    if sec is None:
        raise KeyError(section_key)
    old = sec["label"]
    sec["label"] = new_label
    _log(raw, "section_rename", f"Renamed section “{old}” → “{new_label}”", actor)
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
            _log(raw, "task_toggle",
                 f"{'Reopened' if t['status'] == 'open' else 'Completed'} task “{t['title']}”", actor)
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
