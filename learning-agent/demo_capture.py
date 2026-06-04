"""STEP 1 (run ONCE, ahead of the demo, with live Jira reachable).

Pulls every NXT ticket in a module straight from live Jira and writes a
fixture file. demo.py then generates against this fixture with NO Jira network,
so the live demo runs fast and can't fail on Jira/auth mid-show.

This is the "pre-cache content ahead of time" step for the DEMO only. It is
deliberately separate from the production path (tools_sdk.py is untouched);
real prod caching is a later, separate piece of work.

Usage (venv active, .env filled, live Jira reachable):
    python demo_capture.py --module "Item Management"

Output: data/demo/<module-slug>-fixture.json
"""
import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import httpx
from dotenv import load_dotenv

load_dotenv()

# Reuse the real auth, field IDs, and ADF flattener so the fixture's text
# matches what the live tools would have returned.
from tools_sdk import (
    JIRA_BASE,
    _adf_to_text,
    _basic_auth,
    AC_FIELD_ID,
    RN_FIELD_ID,
    RN_TITLE_FIELD_ID,
    RN_INTERNAL_FIELD_ID,
    RN_REQUIRED_FIELD_ID,
    MODULE_FIELD_ID,
)

APP_DIR = Path(__file__).parent
OUT_DIR = APP_DIR / "data" / "demo"

FIELDS = [
    "summary", "status", "issuetype", "components", "description", "priority",
    "parent", AC_FIELD_ID, RN_FIELD_ID, RN_TITLE_FIELD_ID,
    RN_INTERNAL_FIELD_ID, RN_REQUIRED_FIELD_ID, MODULE_FIELD_ID,
]


def _record(issue: dict) -> dict:
    f = issue.get("fields") or {}
    mod_val = f.get(MODULE_FIELD_ID)
    rn_req = f.get(RN_REQUIRED_FIELD_ID)
    parent = f.get("parent") or {}
    return {
        "key": issue.get("key"),
        "summary": f.get("summary", ""),
        "status": (f.get("status") or {}).get("name", "?"),
        "issuetype": (f.get("issuetype") or {}).get("name", "?"),
        "priority": (f.get("priority") or {}).get("name", "-"),
        "components": [c.get("name", "") for c in (f.get("components") or [])],
        "module": mod_val.get("value") if isinstance(mod_val, dict) else (mod_val or "-"),
        "rn_required": rn_req.get("value") if isinstance(rn_req, dict) else (rn_req or "-"),
        "rn_title": f.get(RN_TITLE_FIELD_ID) or "",
        "ac": _adf_to_text(f.get(AC_FIELD_ID)).strip(),
        "rn": _adf_to_text(f.get(RN_FIELD_ID)).strip(),
        "rn_internal": _adf_to_text(f.get(RN_INTERNAL_FIELD_ID)).strip(),
        "desc": _adf_to_text(f.get("description")).strip(),
        "epic_key": parent.get("key", "-"),
        "epic_summary": (parent.get("fields") or {}).get("summary", ""),
    }


async def fetch_module(module: str) -> list[dict]:
    auth = _basic_auth()
    if auth is None:
        raise SystemExit("ERROR: Jira credentials not configured in .env")
    headers = {"Authorization": auth, "Accept": "application/json", "Content-Type": "application/json"}
    jql = f'project = NXT AND "Module" = "{module}" ORDER BY key ASC'
    url = f"{JIRA_BASE}/rest/api/3/search/jql"

    issues: list[dict] = []
    next_token = None
    async with httpx.AsyncClient(timeout=30) as client:
        while True:
            payload = {"jql": jql, "fields": FIELDS, "maxResults": 100}
            if next_token:
                payload["nextPageToken"] = next_token
            r = await client.post(url, headers=headers, json=payload)
            if r.status_code != 200:
                raise SystemExit(f"ERROR: Jira HTTP {r.status_code}: {r.text[:300]}")
            data = r.json()
            issues.extend(data.get("issues", []))
            next_token = data.get("nextPageToken")
            if not next_token or data.get("isLast"):
                break
    return issues


async def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--module", default="Item Management")
    args = ap.parse_args()

    print(f"Capturing module '{args.module}' from live Jira…")
    issues = await fetch_module(args.module)
    print(f"  pulled {len(issues)} issues")

    tickets: dict[str, dict] = {}
    epics: dict[str, dict] = {}
    for iss in issues:
        rec = _record(iss)
        if rec["issuetype"] == "Epic":
            epics[rec["key"]] = {**rec, "children": []}
        else:
            tickets[rec["key"]] = rec

    # Group children under their epic (derive relationships from the captured set).
    for k, t in tickets.items():
        ek = t.get("epic_key")
        if ek and ek != "-":
            epics.setdefault(ek, {
                "key": ek, "summary": t.get("epic_summary", ""), "status": "?",
                "issuetype": "Epic", "module": args.module, "ac": "", "rn": "",
                "rn_internal": "", "desc": "", "children": [],
            })
            epics[ek]["children"].append(k)

    fixture = {
        "module": args.module,
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "tickets": tickets,
        "epics": epics,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    slug = args.module.lower().replace(" ", "-")
    out = OUT_DIR / f"{slug}-fixture.json"
    out.write_text(json.dumps(fixture, indent=2), encoding="utf-8")
    print(f"  wrote {len(tickets)} tickets + {len(epics)} epics → {out}")
    print("Done. Now run:  python demo.py")


if __name__ == "__main__":
    asyncio.run(main())
