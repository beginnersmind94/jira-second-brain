"""
roster_sync.py — Roster import + completion writeback interface for Learning Studio.

Production path : calls SchoolCafé / PrimeroEdge HTTP API.
Demo / stub path: reads the seeded _roster_for() data already present in demo_app.py
                  and writes writeback calls to logs/writeback-stub.jsonl.

Config (read from .env or environment):
    SCHOOLCAFE_API_URL  — base URL for the SchoolCafé API (e.g. https://api.schoolcafe.com)
    SCHOOLCAFE_API_KEY  — bearer token / API key for SchoolCafé requests

If either variable is absent or empty, ``is_stub`` is True and all calls use the
demo paths.  No real network is touched in demo mode.

Usage (in demo_app.py):
    roster_sync = RosterSyncClient()

    # GET /api/roster
    learners = await roster_sync.get_district_roster("houston-isd")

    # POST /api/tracks/{id}/progress  — non-fatal fire-and-forget
    ok = await roster_sync.sync_completion("houston-isd", learner_id, track_id, pct, certified=False)

    # POST /api/certificates         — certified=True
    ok = await roster_sync.sync_completion("houston-isd", learner_id, track_id, 100, certified=True)

    # Operator status endpoint
    status = roster_sync.status()
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ── Constants for the seeded demo universe ────────────────────────────────────
_DISTRICTS = [
    {"id": "houston-isd",  "name": "Houston ISD",             "domain": "houstonisd"},
    {"id": "dallas-isd",   "name": "Dallas ISD",               "domain": "dallasisd"},
    {"id": "austin-isd",   "name": "Austin ISD",               "domain": "austinisd"},
    {"id": "cy-fair-isd",  "name": "Cypress-Fairbanks ISD",    "domain": "cfisd"},
]
_ROSTER_FIRST = [
    "Maria", "James", "Aisha", "Carlos", "Linda", "Wei", "Diego", "Sarah",
    "Robert", "Priya", "Kenji", "Grace", "Marcus", "Elena", "Tyler", "Fatima",
    "Rosa", "Andre", "Nia", "Hector", "Joy", "Sam", "Lucia", "Omar",
    "Beth", "Trang", "Carl", "Imani",
]
_ROSTER_LAST = [
    "Garcia", "Johnson", "Patel", "Nguyen", "Smith", "Williams", "Brown", "Lee",
    "Martinez", "Davis", "Khan", "Lopez", "Wilson", "Thomas", "Reyes", "Okafor",
    "Cohen", "Tran", "Flores", "Bell", "Ramirez", "Young", "Diaz", "Foster",
]
_ROSTER_ROLES = [
    "POS Cashier", "Cafeteria Manager", "Frontline Cafeteria Staff",
    "District Nutrition Director",
]
_ROSTER_PATHS = [
    "POS Cashier Basics", "Cafeteria Manager: Food Safety Refresher",
    "Frontline Staff: Food Safety Skills", "Menu Planning Foundations",
]
_ROSTER_STATUSES = ["Not started", "In progress", "Completed"]

# Log file for stub writeback records (append-only JSONL).
_WRITEBACK_LOG = Path(__file__).resolve().parent / "logs" / "writeback-stub.jsonl"


def _seeded_roster(district_id: str) -> list[dict]:
    """Deterministic per-district roster generation — same seed → same list."""
    seed = int(hashlib.md5(district_id.encode()).hexdigest(), 16) % (2 ** 32)
    rnd = random.Random(seed)
    domain = next((d["domain"] for d in _DISTRICTS if d["id"] == district_id), district_id)
    out = []
    for _ in range(rnd.randint(18, 32)):
        fn = rnd.choice(_ROSTER_FIRST)
        ln = rnd.choice(_ROSTER_LAST)
        status = rnd.choices(_ROSTER_STATUSES, weights=[3, 4, 3])[0]
        prog = 100 if status == "Completed" else (
            0 if status == "Not started" else rnd.randint(10, 90)
        )
        learner_id = f"{fn[0].lower()}{ln.lower()}_{rnd.randint(100, 999)}"
        out.append({
            "id": learner_id,
            "name": f"{fn} {ln}",
            "role": rnd.choice(_ROSTER_ROLES),
            "site": f"Site {rnd.randint(1, 12):02d}",
            "email": f"{fn[0].lower()}{ln.lower()}@{domain}.org",
            "assigned": rnd.choice(_ROSTER_PATHS),
            "progress": prog,
            "status": status,
            "last_active": rnd.choice([
                "Today", "Yesterday", "3 days ago", "Last week", "2 weeks ago", "—",
            ]),
        })
    out.sort(key=lambda x: x["name"])
    return out


class RosterSyncClient:
    """Integration interface between Learning Studio and SchoolCafé / PrimeroEdge.

    In stub (demo) mode:
      - ``get_district_roster`` returns deterministic seeded data.
      - ``sync_completion`` appends a JSONL record to logs/writeback-stub.jsonl
        and returns True (fire-and-forget, always succeeds).

    In production mode (both env vars configured):
      - ``get_district_roster`` calls GET {SCHOOLCAFE_API_URL}/api/districts/{id}/staff.
      - ``sync_completion`` calls POST {SCHOOLCAFE_API_URL}/api/completions with a JSON body.
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        self._api_url = (api_url or os.getenv("SCHOOLCAFE_API_URL", "")).rstrip("/")
        self._api_key = api_key or os.getenv("SCHOOLCAFE_API_KEY", "")
        self._last_sync: Optional[str] = None

    # ── Public properties ─────────────────────────────────────────────────────

    @property
    def is_stub(self) -> bool:
        """True when running in demo mode (no real credentials configured)."""
        return not (self._api_url and self._api_key)

    def status(self) -> dict:
        """Return operator-facing status dict for GET /api/sync/status."""
        return {
            "stub": self.is_stub,
            "last_sync": self._last_sync,
            "env_configured": not self.is_stub,
        }

    # ── Core interface ────────────────────────────────────────────────────────

    async def get_district_roster(self, district_id: str) -> list[dict]:
        """Return [{id, name, role, site, email, ...}, ...] for the district.

        Production: GET {SCHOOLCAFE_API_URL}/api/districts/{district_id}/staff
        Demo:        returns deterministic seeded data (same as _district_stats).
        """
        if self.is_stub:
            return _seeded_roster(district_id)

        # Production path — requires httpx (already in many FastAPI installs).
        try:
            import httpx
        except ImportError as exc:
            logger.warning(
                "httpx not installed — falling back to stub roster for district %s: %s",
                district_id, exc,
            )
            return _seeded_roster(district_id)

        url = f"{self._api_url}/api/districts/{district_id}/staff"
        headers = {"Authorization": f"Bearer {self._api_key}", "Accept": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                self._last_sync = datetime.now().isoformat(timespec="seconds")
                # Normalise to our field contract if the API returns a list directly.
                return data if isinstance(data, list) else data.get("staff", [])
        except Exception as exc:
            logger.error("SchoolCafé roster fetch failed for %s: %s", district_id, exc)
            raise

    async def sync_completion(
        self,
        district_id: str,
        learner_id: str,
        track_id: str,
        completion_pct: int,
        certified: bool,
    ) -> bool:
        """Write a completion record back to SchoolCafé / PrimeroEdge.

        Production: POST {SCHOOLCAFE_API_URL}/api/completions
        Demo:        appends a JSONL line to logs/writeback-stub.jsonl, returns True.

        Returns True on success.  Raises on production network/HTTP errors
        (callers should catch and continue — the learner's progress must not block).
        """
        record = {
            "at": datetime.now().isoformat(timespec="seconds"),
            "district_id": district_id,
            "learner_id": learner_id,
            "track_id": track_id,
            "completion_pct": int(completion_pct),
            "certified": bool(certified),
        }

        if self.is_stub:
            self._write_stub_log(record)
            self._last_sync = record["at"]
            return True

        # Production path
        try:
            import httpx
        except ImportError as exc:
            logger.warning(
                "httpx not installed — logging writeback stub for learner %s: %s",
                learner_id, exc,
            )
            self._write_stub_log(record)
            return True

        url = f"{self._api_url}/api/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, headers=headers, json=record)
                resp.raise_for_status()
                self._last_sync = record["at"]
                return True
        except Exception as exc:
            logger.error(
                "SchoolCafé completion writeback failed for learner %s / track %s: %s",
                learner_id, track_id, exc,
            )
            raise

    # ── Internal helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _write_stub_log(record: dict) -> None:
        """Append one writeback record to the durable stub log (JSONL)."""
        try:
            _WRITEBACK_LOG.parent.mkdir(parents=True, exist_ok=True)
            with _WRITEBACK_LOG.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError as exc:
            logger.warning("Could not write writeback-stub.jsonl: %s", exc)
