"""
xapi_client.py — xAPI (Tin Can) statement emitter for Learning Studio.

Two modes:
  Stub (default) — statements are appended to logs/xapi-stub.jsonl.
                   Safe for development and the demo; no credentials required.
  Production     — statements are POSTed to an LRS endpoint with HTTP Basic auth.
                   Activated by setting LRS_ENDPOINT and LRS_KEY in the environment.

Configuration
-------------
  LRS_ENDPOINT  Full URL of the LRS statements endpoint,
                e.g. https://lrs.example.com/xapi/statements
  LRS_KEY       "username:password" string (HTTP Basic auth).
                Alternatively: a bearer token — prefix with "Bearer ".

Both emitter methods are async and non-fatal: a network error or a bad LRS response
is logged and returns False; it does NOT raise, so callers in the cert / progress
paths are never interrupted by an LRS outage.

Statement shape
---------------
Follows the ADL xAPI 1.0.3 spec:
  https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md

  {
    "id":        "<UUID v4>",
    "actor":     { "objectType": "Agent", "name": "...", "mbox": "..." },
    "verb":      { "id": "http://adlnet.gov/expapi/verbs/completed", "display": {...} },
    "object":    { "objectType": "Activity", "id": "...", "definition": {...} },
    "result":    { "score": {...}, "completion": true },
    "timestamp": "ISO 8601",
    "context":   { "platform": "Learning Studio", "language": "en-US" }
  }
"""
from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ── ADL verb URIs ────────────────────────────────────────────────────────────
_VERB_COMPLETED  = "http://adlnet.gov/expapi/verbs/completed"
_VERB_PROGRESSED = "http://adlnet.gov/expapi/verbs/progressed"
_VERB_PASSED     = "http://adlnet.gov/expapi/verbs/passed"

# Activity type for a learning module (ADL recipe).
_ACTIVITY_TYPE_MODULE = "http://adlnet.gov/expapi/activities/module"
_ACTIVITY_TYPE_COURSE = "http://adlnet.gov/expapi/activities/course"

# Platform identifier embedded in every statement's context.
_PLATFORM = "Learning Studio (Cybersoft)"

# Stub log path — relative to this file's directory.
_STUB_LOG: Path = Path(__file__).resolve().parent / "logs" / "xapi-stub.jsonl"


# ─────────────────────────────────────────────────────────────────────────────
# XAPIClient
# ─────────────────────────────────────────────────────────────────────────────


class XAPIClient:
    """
    Emits xAPI statements to a configured LRS endpoint.

    Stub mode (default): logs statements to logs/xapi-stub.jsonl.
    Production mode: POST to LRS_ENDPOINT with LRS_KEY auth.

    Instantiate once and reuse; the client is stateless between calls.
    """

    def __init__(
        self,
        lrs_endpoint: Optional[str] = None,
        lrs_key: Optional[str] = None,
    ) -> None:
        self._endpoint = (lrs_endpoint or os.getenv("LRS_ENDPOINT") or "").strip()
        self._key      = (lrs_key or os.getenv("LRS_KEY") or "").strip()
        self._stub     = not bool(self._endpoint)

    # ── Public properties ───────────────────────────────────────────────────

    @property
    def stub(self) -> bool:
        """True when operating in stub mode (no real LRS)."""
        return self._stub

    @property
    def lrs_configured(self) -> bool:
        """True when a real LRS endpoint is configured."""
        return bool(self._endpoint)

    # ── Public emitters ─────────────────────────────────────────────────────

    async def emit_completed(
        self,
        actor: dict,
        track: dict,
        score: float = 100.0,
    ) -> bool:
        """Emit an xAPI 'completed' statement for a full track.

        Parameters
        ----------
        actor  : Dict with at least {"name": str, "email": str} (or "mbox").
        track  : Track dict (id, title, product, …).
        score  : Raw score 0–100.  Defaults to 100 (full completion).

        Returns True if the statement was accepted (or stubbed); False on error.
        """
        stmt = _build_statement(
            actor=actor,
            verb_id=_VERB_COMPLETED,
            verb_display="completed",
            activity_id=_activity_id(track),
            activity_name=track.get("title") or track.get("id") or "Track",
            activity_type=_ACTIVITY_TYPE_COURSE,
            result={
                "score": {
                    "scaled": round(score / 100.0, 4),
                    "raw": score,
                    "min": 0.0,
                    "max": 100.0,
                },
                "completion": True,
                "success": score >= 80.0,
            },
        )
        return await self._emit(stmt)

    async def emit_progressed(
        self,
        actor: dict,
        track: dict,
        module_id: str,
    ) -> bool:
        """Emit an xAPI 'progressed' statement for a single module completion.

        Parameters
        ----------
        actor     : Dict with at least {"name": str, "email": str} (or "mbox").
        track     : Track dict.
        module_id : The id of the completed module.

        Returns True if the statement was accepted (or stubbed); False on error.
        """
        activity_name = module_id
        # Try to resolve a human title from the track's module list.
        for m in track.get("modules") or []:
            if m.get("id") == module_id:
                activity_name = m.get("title") or module_id
                break

        stmt = _build_statement(
            actor=actor,
            verb_id=_VERB_PROGRESSED,
            verb_display="progressed",
            activity_id=_module_activity_id(track, module_id),
            activity_name=activity_name,
            activity_type=_ACTIVITY_TYPE_MODULE,
            result={"completion": True},
            context_parent_id=_activity_id(track),
            context_parent_name=track.get("title") or track.get("id") or "Track",
        )
        return await self._emit(stmt)

    # ── Internal dispatch ────────────────────────────────────────────────────

    async def _emit(self, stmt: dict) -> bool:
        if self._stub:
            return _stub_emit(stmt)
        return await _live_emit(stmt, self._endpoint, self._key)


# ─────────────────────────────────────────────────────────────────────────────
# Statement builder
# ─────────────────────────────────────────────────────────────────────────────


def _actor_dict(actor: dict) -> dict:
    """Normalise the caller's actor dict to a valid xAPI Agent."""
    name  = actor.get("name") or "Unknown Learner"
    email = actor.get("email") or actor.get("mbox") or ""
    if email and not email.startswith("mailto:"):
        email = "mailto:" + email
    out: dict = {"objectType": "Agent", "name": name}
    if email:
        out["mbox"] = email
    else:
        # Use account IRI if no email (xAPI requires at least one IFI).
        uid = actor.get("id") or actor.get("user_id") or "anonymous"
        out["account"] = {
            "homePage": "https://learning.cybersoft.net",
            "name": uid,
        }
    return out


def _activity_id(track: dict) -> str:
    tid = track.get("id") or "unknown"
    return f"https://learning.cybersoft.net/tracks/{tid}"


def _module_activity_id(track: dict, module_id: str) -> str:
    tid = track.get("id") or "unknown"
    return f"https://learning.cybersoft.net/tracks/{tid}/modules/{module_id}"


def _build_statement(
    actor: dict,
    verb_id: str,
    verb_display: str,
    activity_id: str,
    activity_name: str,
    activity_type: str,
    result: Optional[dict] = None,
    context_parent_id: Optional[str] = None,
    context_parent_name: Optional[str] = None,
) -> dict:
    """Build a fully-formed xAPI 1.0.3 statement dict."""
    stmt: dict = {
        "id": str(uuid.uuid4()),
        "actor": _actor_dict(actor),
        "verb": {
            "id": verb_id,
            "display": {"en-US": verb_display},
        },
        "object": {
            "objectType": "Activity",
            "id": activity_id,
            "definition": {
                "type": activity_type,
                "name": {"en-US": activity_name},
            },
        },
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        "context": {
            "platform": _PLATFORM,
            "language": "en-US",
        },
    }

    if result:
        stmt["result"] = result

    if context_parent_id:
        stmt["context"]["contextActivities"] = {
            "parent": [
                {
                    "objectType": "Activity",
                    "id": context_parent_id,
                    "definition": {
                        "type": _ACTIVITY_TYPE_COURSE,
                        "name": {"en-US": context_parent_name or context_parent_id},
                    },
                }
            ]
        }

    return stmt


# ─────────────────────────────────────────────────────────────────────────────
# Stub emitter
# ─────────────────────────────────────────────────────────────────────────────


def _stub_emit(stmt: dict) -> bool:
    """Append the statement to logs/xapi-stub.jsonl and return True."""
    try:
        _STUB_LOG.parent.mkdir(parents=True, exist_ok=True)
        with _STUB_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(stmt, ensure_ascii=False) + "\n")
        logger.debug("[xapi_stub] logged statement %s verb=%s", stmt["id"], stmt["verb"]["id"])
        return True
    except OSError as exc:
        logger.warning("[xapi_stub] could not write stub log: %s", exc)
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Live emitter  (production — POST to LRS)
# ─────────────────────────────────────────────────────────────────────────────


async def _live_emit(stmt: dict, endpoint: str, key: str) -> bool:
    """POST a single statement to the LRS.  Non-fatal on any error."""
    try:
        import httpx  # optional dependency; import here so stub mode works without it
    except ImportError:
        logger.error(
            "[xapi] httpx is not installed — cannot POST to LRS. "
            "Install it with: pip install httpx"
        )
        return False

    headers = {
        "Content-Type": "application/json",
        "X-Experience-API-Version": "1.0.3",
    }

    # Auth: "Bearer <token>" or basic "user:password".
    if key.lower().startswith("bearer "):
        headers["Authorization"] = key
    elif ":" in key:
        encoded = base64.b64encode(key.encode()).decode()
        headers["Authorization"] = f"Basic {encoded}"
    elif key:
        # Treat a bare key as a bearer token.
        headers["Authorization"] = f"Bearer {key}"

    payload = json.dumps(stmt, ensure_ascii=False)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(endpoint, content=payload, headers=headers)
        if resp.status_code in (200, 204):
            logger.debug("[xapi] statement %s accepted by LRS (HTTP %s)", stmt["id"], resp.status_code)
            return True
        else:
            logger.warning(
                "[xapi] LRS rejected statement %s: HTTP %s — %s",
                stmt["id"], resp.status_code, resp.text[:200],
            )
            return False
    except Exception as exc:
        # Non-fatal — cert issuance / progress must not fail because the LRS is down.
        logger.warning("[xapi] failed to POST statement %s: %s", stmt["id"], exc)
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Module-level singleton (convenience for demo_app.py callers)
# ─────────────────────────────────────────────────────────────────────────────

#: Shared client instance.  Reads LRS_ENDPOINT / LRS_KEY from the environment.
#: Import this and call its methods; do not instantiate a new client per request.
client: XAPIClient = XAPIClient()
