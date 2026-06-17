"""
auth.py — Single identity interface for Learning Studio.

All identity reads go through here. No other file is allowed to hardcode
user identity (district, name, role).

Production path: read from session cookie / JWT set by SchoolCafé / PrimeroEdge SSO.
Demo/dev path:  read from X-Demo-User request header (or ?demo_user= query param).
Fallback:       "john-cashier" (keeps existing demo behaviour unchanged).

Persona map
-----------
  john-cashier   →  John Doe · Cashier · Houston ISD · learner
  dana-director  →  Dana Reyes · CN Director · Houston ISD · learner
  sam-trainer    →  Sam Rivera · Trainer · [Houston, Aldine, Klein] · trainer

When the production SSO hook is wired (SchoolCafé JWT), _get_sso_user() will
return a real CurrentUser and the demo bypass is ignored automatically.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from fastapi import Request

# ── Data model ────────────────────────────────────────────────────────────────


@dataclass
class CurrentUser:
    id: str                         # stable unique id (UUID or product login id)
    name: str                       # display name shown in the UI
    role: str                       # "Cashier" | "Site Manager" | "CN Director" | "Trainer"
    district_id: Optional[str]      # learner's home district (None for Trainers)
    districts: list[str] = field(default_factory=list)  # Trainer's book of business
    is_trainer: bool = False


# ── Canonical role vocabulary ──────────────────────────────────────────────────
# These are the EXACT strings used in current_user.role for learner personas.
# Role filtering on modules/tracks/courses does exact-string matching against
# this list, so tags entered elsewhere MUST use these strings verbatim.
#
# "Trainer" is excluded deliberately: Trainers are staff/authors, not learners.
# Content role_tags control which learner audience a guide is for; a Trainer
# can view all content regardless of tags.
#
# When adding new learner roles, extend this list AND update auth.py's
# _DEMO_PERSONAS with a matching demo persona.
ROLE_VOCAB: list[str] = ["Cashier", "Site Manager", "CN Director"]


# ── Demo personas ─────────────────────────────────────────────────────────────
# Keyed by the X-Demo-User header value (lower-cased).

_DEMO_PERSONAS: dict[str, CurrentUser] = {
    "john-cashier": CurrentUser(
        id="demo-user-001",
        name="John Doe",
        role="Cashier",
        district_id="houston-isd",
        districts=[],
        is_trainer=False,
    ),
    "dana-director": CurrentUser(
        id="demo-user-002",
        name="Dana Reyes",
        role="CN Director",
        district_id="houston-isd",
        districts=[],
        is_trainer=False,
    ),
    "sam-trainer": CurrentUser(
        id="demo-user-003",
        name="Sam Rivera",
        role="Trainer",
        district_id=None,
        districts=["houston-isd", "aldine-isd", "klein-isd"],
        is_trainer=True,
    ),
}

_DEFAULT_PERSONA_KEY = "john-cashier"


# ── Production hook (stub) ────────────────────────────────────────────────────


def _get_sso_user(request: Request) -> CurrentUser | None:
    """Read JWT/session from SchoolCafé / PrimeroEdge SSO.

    Returns a CurrentUser when a valid session is found; None otherwise.
    Returning None causes get_current_user() to fall through to the demo bypass.

    TODO: implement when SSO endpoint is available (ADR-001 §Auth).
          Expected: validate the JWT from the 'Authorization: Bearer <token>'
          header or the 'session' cookie, then map the claims to CurrentUser fields.
    """
    return None


# ── Main identity entry point ─────────────────────────────────────────────────


def get_current_user(request: Request) -> CurrentUser:
    """Return the identity for this request.

    Resolution order:
    1. Production SSO (SchoolCafé JWT / session cookie) — when the hook is wired.
    2. X-Demo-User header  (e.g. 'X-Demo-User: sam-trainer').
    3. ?demo_user= query param (fallback for tools that can't set headers).
    4. Default demo persona ("john-cashier") — preserves existing demo behaviour.
    """
    # 1. Try production SSO first — always takes priority over the demo bypass.
    sso_user = _get_sso_user(request)
    if sso_user is not None:
        return sso_user

    # 2. Demo bypass: X-Demo-User header.
    persona_key = (request.headers.get("X-Demo-User") or "").strip().lower()

    # 3. Fall back to ?demo_user= query param.
    if not persona_key:
        persona_key = (request.query_params.get("demo_user") or "").strip().lower()

    # 4. Unknown / missing key → use the default persona (keeps current demo unchanged).
    return _DEMO_PERSONAS.get(persona_key, _DEMO_PERSONAS[_DEFAULT_PERSONA_KEY])
