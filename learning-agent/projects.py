"""Projects flow — Trainer creates a project, imports sites and users via CSV,
lands on a working project dashboard.

Storage matches the demo_app.py pattern (in-memory dicts). No ORM, no real auth.
A single cookie (`lc_trainer`) identifies the trainer; the SPA reads it for the
"Logged in as Trainer Bob" header pill. There is no enforcement — the cookie
is a demo signal, not a security boundary.

Wired from demo_app.py via:
    from projects import router as projects_router
    app.include_router(projects_router)

Routes (all JSON; the SPA renders):
    POST /api/auth/login                          mock login (sets cookie)
    POST /api/auth/logout                         clear cookie
    GET  /api/me                                  who am I?
    POST /api/projects                            create
    GET  /api/projects                            list
    GET  /api/projects/{pid}                      dashboard payload
    POST /api/projects/{pid}/sites/import         CSV (?mode=preview|commit)
    POST /api/projects/{pid}/users/import         CSV (?mode=preview|commit)
"""
from __future__ import annotations

import csv
import io
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Body, Cookie, File, HTTPException, Query, Response, UploadFile

router = APIRouter()

# ── Storage (in-memory, demo-façade pattern) ────────────────────────────────
_PROJECTS: dict[str, dict] = {}

# Canonical role enum — matches the app's existing role dropdown.
ROLES = ("Cashier", "Site Manager", "CN Director")

TRAINER_COOKIE = "lc_trainer"
TRAINER_NAME = "Trainer Bob"
TRAINER_TOKEN = "trainer-bob"

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _reset_for_tests():
    """Hook for pytest — wipes the in-memory store between tests."""
    _PROJECTS.clear()


# ── Mock auth ───────────────────────────────────────────────────────────────
@router.post("/api/auth/login")
def auth_login(response: Response, payload: dict = Body(default={})):
    """Mock login — sets a session cookie identifying Trainer Bob.

    The cookie is a demo signal (it powers the "Logged in as Trainer Bob" pill
    in the SPA). There is no real authentication. Any payload is accepted.
    """
    response.set_cookie(
        TRAINER_COOKIE, TRAINER_TOKEN,
        max_age=60 * 60 * 8, httponly=False, samesite="lax",
    )
    return {"ok": True, "user": {"name": TRAINER_NAME, "role": "Trainer"}}


@router.post("/api/auth/logout")
def auth_logout(response: Response):
    response.delete_cookie(TRAINER_COOKIE)
    return {"ok": True}


@router.get("/api/me")
def auth_me(lc_trainer: str | None = Cookie(default=None)):
    if lc_trainer == TRAINER_TOKEN:
        return {"signed_in": True, "user": {"name": TRAINER_NAME, "role": "Trainer"}}
    return {"signed_in": False}


# ── Project create + list ───────────────────────────────────────────────────
@router.post("/api/projects")
def create_project(payload: dict = Body(...)):
    name = (payload.get("name") or "").strip()
    product = (payload.get("product") or "").strip()
    go_live = (payload.get("go_live_date") or "").strip()

    errors: dict[str, str] = {}
    if not name:
        errors["name"] = "Project name is required."
    if not product:
        errors["product"] = "Product is required."
    if not go_live:
        errors["go_live_date"] = "Go-live date is required."
    else:
        try:
            datetime.strptime(go_live, "%Y-%m-%d")
        except ValueError:
            errors["go_live_date"] = "Go-live date must be in YYYY-MM-DD format."
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})

    pid = _new_id("p")
    proj = {
        "id": pid,
        "name": name,
        "product": product,
        "go_live_date": go_live,
        "created_at": _now_iso(),
        "sites_imported_at": None,
        "users_imported_at": None,
        "sites": {},   # site_id -> {id, name, address}
        "users": {},   # user_id -> {id, employee_id, full_name, email, role, site_id}
    }
    _PROJECTS[pid] = proj
    return {"ok": True, "project": _project_summary(proj)}


@router.get("/api/projects")
def list_projects():
    return {"projects": [_project_summary(p) for p in _PROJECTS.values()]}


def _project_summary(proj: dict) -> dict:
    return {
        "id": proj["id"], "name": proj["name"], "product": proj["product"],
        "go_live_date": proj["go_live_date"], "created_at": proj["created_at"],
        "sites_imported_at": proj["sites_imported_at"],
        "users_imported_at": proj["users_imported_at"],
        "site_count": len(proj["sites"]), "user_count": len(proj["users"]),
    }


# ── Dashboard ───────────────────────────────────────────────────────────────
@router.get("/api/projects/{pid}")
def get_project(pid: str):
    proj = _PROJECTS.get(pid)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    # Counts by role (use canonical enum, include 0 for missing roles so the UI
    # can render a stable set of stat cards).
    by_role = {r: 0 for r in ROLES}
    for u in proj["users"].values():
        by_role[u["role"]] = by_role.get(u["role"], 0) + 1

    # Per-site user count + roles breakdown.
    by_site = []
    sites_sorted = sorted(proj["sites"].values(), key=lambda s: s["name"])
    for site in sites_sorted:
        site_users = [u for u in proj["users"].values() if u["site_id"] == site["id"]]
        role_breakdown = {r: 0 for r in ROLES}
        for u in site_users:
            role_breakdown[u["role"]] = role_breakdown.get(u["role"], 0) + 1
        by_site.append({
            "id": site["id"], "name": site["name"], "address": site["address"],
            "user_count": len(site_users), "by_role": role_breakdown,
        })

    return {
        "project": _project_summary(proj),
        "counts": {"by_role": by_role, "total_users": len(proj["users"]),
                   "total_sites": len(proj["sites"])},
        "sites": by_site,
        "tracks": [],   # Task 3 hook; intentionally empty.
    }


# ── CSV import — shared helpers ─────────────────────────────────────────────
SITES_REQUIRED = ("site_name", "address")
USERS_REQUIRED = ("employee_id", "full_name", "email", "role", "site_name")


async def _read_csv_rows(file: UploadFile) -> tuple[list[str], list[dict]]:
    """Read an uploaded CSV → (column_names, list-of-row-dicts). Robust to
    BOM, CRLF, blank trailing lines, and case-mixed headers (we lowercase
    keys so 'Site_Name' and 'site_name' both work)."""
    raw = await file.read()
    if not raw:
        return [], []
    text = raw.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    cols = [c.strip().lower() for c in (reader.fieldnames or [])]
    rows: list[dict] = []
    for r in reader:
        # skip wholly-blank rows
        if not any((v or "").strip() for v in r.values()):
            continue
        norm = {(k or "").strip().lower(): (v or "").strip() for k, v in r.items()}
        rows.append(norm)
    return cols, rows


def _required_col_errors(cols: list[str], required: tuple[str, ...]) -> list[str]:
    missing = [c for c in required if c not in cols]
    return [f"Missing required column: {c}" for c in missing]


def _validate_sites(rows: list[dict]) -> list[dict]:
    out: list[dict] = []
    seen_names: dict[str, int] = {}  # lower(name) -> row_num that defined it
    for i, r in enumerate(rows, start=2):  # row 1 = header, data starts at 2
        errors: list[str] = []
        name = (r.get("site_name") or "").strip()
        addr = (r.get("address") or "").strip()
        if not name:
            errors.append("site_name is required")
        if not addr:
            errors.append("address is required")
        key = name.lower()
        if name and key in seen_names:
            errors.append(f"duplicate site_name (also on row {seen_names[key]})")
        elif name:
            seen_names[key] = i
        out.append({"_row_num": i, "site_name": name, "address": addr, "_errors": errors})
    return out


def _validate_users(rows: list[dict], known_site_names: set[str]) -> list[dict]:
    """Validate user rows against an existing set of site_names (lower-cased).

    Unknown site_name → row blocked with an inline error (acceptance criterion 3).
    """
    out: list[dict] = []
    seen_eid: dict[str, int] = {}
    seen_email: dict[str, int] = {}
    for i, r in enumerate(rows, start=2):
        errors: list[str] = []
        eid = (r.get("employee_id") or "").strip()
        full_name = (r.get("full_name") or "").strip()
        email = (r.get("email") or "").strip()
        role = (r.get("role") or "").strip()
        site_name = (r.get("site_name") or "").strip()

        if not eid:
            errors.append("employee_id is required")
        elif eid in seen_eid:
            errors.append(f"duplicate employee_id (also on row {seen_eid[eid]})")
        else:
            seen_eid[eid] = i

        if not full_name:
            errors.append("full_name is required")

        if not email:
            errors.append("email is required")
        elif not EMAIL_RE.match(email):
            errors.append("email is not a valid address")
        elif email.lower() in seen_email:
            errors.append(f"duplicate email (also on row {seen_email[email.lower()]})")
        else:
            seen_email[email.lower()] = i

        if not role:
            errors.append("role is required")
        elif role not in ROLES:
            errors.append(f'role "{role}" is not in the canonical enum '
                          f'({", ".join(ROLES)})')

        if not site_name:
            errors.append("site_name is required")
        elif site_name.lower() not in known_site_names:
            errors.append(f'unknown site: "{site_name}" — import this site first')

        out.append({
            "_row_num": i, "employee_id": eid, "full_name": full_name, "email": email,
            "role": role, "site_name": site_name, "_errors": errors,
        })
    return out


def _commit_blocked(rows: list[dict]) -> bool:
    return any(r["_errors"] for r in rows)


# ── Sites import ────────────────────────────────────────────────────────────
@router.post("/api/projects/{pid}/sites/import")
async def import_sites(pid: str, file: UploadFile = File(...),
                       mode: str = Query(default="preview", pattern="^(preview|commit)$")):
    proj = _PROJECTS.get(pid)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    cols, rows = await _read_csv_rows(file)
    col_errors = _required_col_errors(cols, SITES_REQUIRED)
    if col_errors:
        return {"ok": False, "mode": mode, "columns_ok": False,
                "errors_summary": col_errors, "rows": [],
                "required_columns": list(SITES_REQUIRED), "columns_seen": cols}

    validated = _validate_sites(rows)
    has_errors = _commit_blocked(validated)
    summary = {"total_rows": len(validated),
               "rows_with_errors": sum(1 for r in validated if r["_errors"])}

    if mode == "preview" or has_errors:
        return {"ok": not has_errors, "mode": "preview", "columns_ok": True,
                "rows": validated, "summary": summary,
                "errors_summary": ([f"{summary['rows_with_errors']} row(s) have errors — "
                                    "fix and re-upload to commit."] if has_errors else []),
                "required_columns": list(SITES_REQUIRED)}

    # mode=commit, no errors → replace the project's sites with the new set,
    # preserving site_id for names that already existed so user→site links survive
    # a re-import.
    existing_by_name = {s["name"].lower(): s["id"] for s in proj["sites"].values()}
    new_sites: dict[str, dict] = {}
    for r in validated:
        key = r["site_name"].lower()
        sid = existing_by_name.get(key) or _new_id("s")
        new_sites[sid] = {"id": sid, "name": r["site_name"], "address": r["address"]}
    proj["sites"] = new_sites

    # Drop any users whose site is gone after the re-import (defensive — the demo
    # imports sites first, then users, so this rarely fires).
    valid_site_ids = set(new_sites.keys())
    proj["users"] = {uid: u for uid, u in proj["users"].items() if u["site_id"] in valid_site_ids}

    proj["sites_imported_at"] = _now_iso()
    return {"ok": True, "mode": "commit", "summary": summary,
            "project": _project_summary(proj), "rows": validated}


# ── Users import ────────────────────────────────────────────────────────────
@router.post("/api/projects/{pid}/users/import")
async def import_users(pid: str, file: UploadFile = File(...),
                       mode: str = Query(default="preview", pattern="^(preview|commit)$")):
    proj = _PROJECTS.get(pid)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    cols, rows = await _read_csv_rows(file)
    col_errors = _required_col_errors(cols, USERS_REQUIRED)
    if col_errors:
        return {"ok": False, "mode": mode, "columns_ok": False,
                "errors_summary": col_errors, "rows": [],
                "required_columns": list(USERS_REQUIRED), "columns_seen": cols}

    known_sites = {s["name"].lower() for s in proj["sites"].values()}
    if not known_sites:
        return {"ok": False, "mode": mode, "columns_ok": True,
                "errors_summary": ["No sites in this project yet — import sites first."],
                "rows": [], "required_columns": list(USERS_REQUIRED)}

    validated = _validate_users(rows, known_sites)
    has_errors = _commit_blocked(validated)
    summary = {"total_rows": len(validated),
               "rows_with_errors": sum(1 for r in validated if r["_errors"])}

    if mode == "preview" or has_errors:
        return {"ok": not has_errors, "mode": "preview", "columns_ok": True,
                "rows": validated, "summary": summary,
                "errors_summary": ([f"{summary['rows_with_errors']} row(s) have errors — "
                                    "fix and re-upload to commit."] if has_errors else []),
                "required_columns": list(USERS_REQUIRED)}

    # mode=commit — resolve site_name → site_id by case-insensitive match.
    by_site_name = {s["name"].lower(): s["id"] for s in proj["sites"].values()}
    new_users: dict[str, dict] = {}
    for r in validated:
        uid = _new_id("u")
        new_users[uid] = {
            "id": uid, "employee_id": r["employee_id"], "full_name": r["full_name"],
            "email": r["email"], "role": r["role"],
            "site_id": by_site_name[r["site_name"].lower()],
        }
    proj["users"] = new_users
    proj["users_imported_at"] = _now_iso()
    return {"ok": True, "mode": "commit", "summary": summary,
            "project": _project_summary(proj), "rows": validated}
