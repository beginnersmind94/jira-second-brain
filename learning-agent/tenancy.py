"""tenancy.py — Multi-tenant district-access enforcement for Learning Studio.

All district-scoped API routes MUST call assert_district_access() before
returning any data. This module is the single enforcement point — "tenant
boundaries enforced at the API layer, not by seed data" (BRD NFR).

Roles and district scope
------------------------
- Trainer       : Cybersoft staff; ``is_trainer=True``.
                  Access: any district in ``user.districts`` (their book of business).
- Learner        : District staff; ``is_trainer=False``.
                  Access: only ``user.district_id`` (their home district).
- CN Director    : District-side admin; ``is_trainer=False``.
                  Access: only ``user.district_id`` (their single district).

Trainers share the ``districts`` list field; learners/directors use
``district_id`` and their ``districts`` list is always ``[district_id]``.

Usage in a route
----------------
    from fastapi import Depends, Request
    from auth import CurrentUser, get_current_user
    from tenancy import assert_district_access, get_user_districts

    @app.get("/api/roster")
    async def api_roster(
        request: Request,
        isd: str = "",
        current_user: CurrentUser = Depends(get_current_user),
    ):
        assert_district_access(current_user, isd)
        ...

Design note
-----------
The guard is intentionally simple — a list membership check, not a policy
engine. The auth.py CurrentUser object carries all the state needed; this
module only enforces the rule. When a real JWT/SSO lands (ADR-001 §Auth),
auth.py's get_current_user() is swapped; tenancy.py does not change.
"""
from __future__ import annotations

from fastapi import HTTPException

from auth import CurrentUser


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def assert_district_access(user: CurrentUser, requested_isd: str) -> None:
    """Raise HTTPException(403) if the user is not allowed to read ``requested_isd``.

    Empty / blank ``requested_isd`` is treated as "no district filter requested"
    and is allowed for all users (they will see their own data after the caller
    applies get_user_districts() to bound the result set).

    Enforcement rules
    -----------------
    - Trainers   : pass when ``requested_isd in user.districts``.
    - Learners   : pass when ``requested_isd == user.district_id``.
    - CN Director: same as Learner (is_trainer=False).

    The 403 body contains a machine-readable ``error`` code and a human-readable
    ``detail`` message for the UI to surface.
    """
    isd = (requested_isd or "").strip()
    if not isd:
        # No specific district requested — allow; caller scopes the result.
        return

    allowed = get_user_districts(user)
    if isd not in allowed:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "district_access_denied",
                "detail": (
                    f"You do not have access to district '{isd}'. "
                    f"Your access is limited to: {', '.join(sorted(allowed)) or 'none'}."
                ),
            },
        )


def filter_to_accessible_districts(user: CurrentUser, isds: list[str]) -> list[str]:
    """Return only the ISD ids from ``isds`` that ``user`` is allowed to access.

    Preserves the original order of ``isds``.

    Examples
    --------
    Trainer with districts=['houston-isd', 'dallas-isd']:
        filter_to_accessible_districts(user, ['houston-isd', 'austin-isd'])
        → ['houston-isd']

    Learner with district_id='dallas-isd':
        filter_to_accessible_districts(user, ['houston-isd', 'dallas-isd'])
        → ['dallas-isd']
    """
    allowed = set(get_user_districts(user))
    return [isd for isd in isds if isd in allowed]


def get_user_districts(user: CurrentUser) -> list[str]:
    """Return all ISD ids the user is permitted to access.

    - Trainers   : ``user.districts`` (their book of business).
    - All others : ``[user.district_id]`` when district_id is set, else ``[]``.

    This is the single source of truth for "what can this user see?" —
    never read user.districts or user.district_id directly in route handlers.
    """
    if user.is_trainer:
        return list(user.districts)
    if user.district_id:
        return [user.district_id]
    return []
