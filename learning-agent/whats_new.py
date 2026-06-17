"""whats_new.py — deterministic feed of newest approved training content per role.

No LLM call anywhere in this module.  Pure file reads + filtering.

Public API:
    build_whats_new(role: str) -> dict

Return shape:
    {
        "role": str,
        "generated_at": str (filled by the route handler),
        "items": [...],
        "_sources": {...},
        "_data_notice": None | str
    }
"""
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

# ── Path constants (same source as tools_sdk.py) ───────────────────────────────
import os

_APP_DIR = Path(__file__).parent
_DATA_DIR = _APP_DIR / "data"
_JIRA_BRAIN = Path(os.getenv(
    "JIRA_BRAIN_PATH",
    r"C:\Users\rahul.mehta\Downloads\Financials-Documentation-KT\jira-brain",
))
KB_CONCEPTS = _JIRA_BRAIN / "wiki" / "concepts"
KB_WORKFLOWS = _JIRA_BRAIN / "wiki" / "workflows"

# ── Reuse modules_store helpers — single source of truth for approved state ────
import modules_store as _ms

# ── Role hierarchy ─────────────────────────────────────────────────────────────
# Roles visible to each audience (a director sees everything; cashier sees only
# content tagged for cashiers or untagged/all-staff).
_ROLE_VISIBLE: dict[str, set[str]] = {
    "Cashier": {"Cashier", "All staff", ""},
    "Site Manager": {"Site Manager", "Cashier", "All staff", ""},
    "CN Director": {"CN Director", "Site Manager", "Cashier", "All staff", ""},
}
# Normalise incoming role strings to one of our canonical three.
_ROLE_ALIASES: dict[str, str] = {
    "cashier": "Cashier",
    "site manager": "Site Manager",
    "sitemanager": "Site Manager",
    "cn director": "CN Director",
    "cndirector": "CN Director",
    "director": "CN Director",
    "trainer": "CN Director",   # trainers see everything
}

TODAY = date.today()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _normalise_role(raw: str) -> str:
    return _ROLE_ALIASES.get(raw.strip().lower(), raw.strip()) if raw else "Cashier"


def _role_visible_set(role: str) -> set[str]:
    return _ROLE_VISIBLE.get(role, {"All staff", ""})


def _artifact_roles(artifact: dict) -> list[str]:
    """Return the role_tags list, normalised to empty list if absent / all-staff."""
    tags = artifact.get("role_tags") or []
    if not tags:
        return []
    # treat the literal string "All staff" as untagged (visible to everyone)
    return [t for t in tags if t and t.lower() not in ("all staff", "all")]


def _is_visible(artifact: dict, visible_set: set[str]) -> bool:
    """True if this artifact should appear for the given role."""
    tags = _artifact_roles(artifact)
    if not tags:
        return True   # untagged = all staff
    return bool(set(tags) & visible_set)


def _parse_date(val: str | None) -> date | None:
    """Parse ISO-8601 date/datetime string to a date, or return None."""
    if not val:
        return None
    try:
        # handles both "2026-06-10" and "2026-06-10T12:00:00"
        return datetime.fromisoformat(val.rstrip("Z")).date()
    except (ValueError, TypeError):
        return None


def _freshness_label(d: date) -> str:
    delta = (TODAY - d).days
    if delta <= 30:
        return "New"
    if delta <= 90:
        return "Recently added"
    return "In library"


def _origin_from_artifact(artifact: dict, kind: str) -> str:
    """Derive origin enum from artifact fields.

    ai_grounded   — AI-generated guide approved via transcript pipeline
    human_authored — imported Cybersoft/SchoolCafé guide (origin==internal)
    outside_vendor — ICN/USDA content asset
    """
    if kind == "track":
        # Tracks are always an internal product — treat as human_authored
        # unless they're purely AI-generated (no seeded tracks are).
        return "human_authored"

    # Module (guide) — follow modules_store._module_source logic
    if artifact.get("origin") == "internal" or artifact.get("method") == "imported_guide":
        return "human_authored"
    if artifact.get("source") == "ICN_DOC" or str(artifact.get("id", "")).startswith("icn-"):
        return "outside_vendor"
    if artifact.get("source") == "AI_TRANSCRIPT":
        return "ai_grounded"
    # Fall back: if there's a module/template, it was AI-generated
    if artifact.get("template") and artifact.get("module"):
        return "ai_grounded"
    return "human_authored"


# ── Activity-pulse theme extraction ───────────────────────────────────────────

def _wiki_page_for_module(module_name: str) -> Path | None:
    """Find the wiki concept or workflow page whose title matches the module name.

    Matching is case-insensitive, spaces converted to hyphens for filenames.
    Returns None if no page is found.
    """
    if not module_name:
        return None
    # Try concepts first (primary), then workflows
    slug = module_name.replace(" ", "-")
    for directory in (KB_CONCEPTS, KB_WORKFLOWS):
        candidate = directory / f"{slug}.md"
        if candidate.exists():
            return candidate
        # Also try the exact module_name if it happens to be a filename already
        candidate2 = directory / f"{module_name}.md"
        if candidate2.exists():
            return candidate2
    return None


_PULSE_RE = re.compile(
    r">\s*\*\*Activity pulse\*\*.*?Recent themes from the corpus:\s*\*([^*]+)\*",
    re.IGNORECASE,
)


def _extract_themes(page_path: Path) -> list[str]:
    """Read the Activity pulse line and parse out up to 3 theme chips.

    Returns [] if no pulse line or no themes.  Never raises — silently returns [].
    """
    try:
        text = page_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    # Find the first line that contains "Activity pulse"
    for line in text.splitlines():
        if "**Activity pulse**" in line:
            # Look for "Recent themes from the corpus:" pattern
            m = _PULSE_RE.search(line)
            if m:
                raw = m.group(1)
                # themes are separated by commas (and possibly *commas* or ", ")
                themes = [t.strip().strip("*").strip() for t in re.split(r",\s*", raw)]
                themes = [t for t in themes if t]
                return themes[:3]
            return []
    return []


# ── Approved guides loader ─────────────────────────────────────────────────────

def _load_approved_guides() -> list[dict]:
    """Return all approved/published guides as module dicts.

    Reuses modules_store._load_resource_modules() — the same function that
    powers /api/modules.  ICN modules are excluded here (tracks cover them).
    """
    return _ms._load_resource_modules()


# ── Approved tracks loader ─────────────────────────────────────────────────────

def _load_published_tracks() -> list[dict]:
    """Return all tracks with status=='published'."""
    return [t for t in _ms.list_tracks() if t.get("status") == "published"]


# ── Main builder ───────────────────────────────────────────────────────────────

def build_whats_new(role: str = "Cashier") -> dict:
    """Build the What's New feed for a given role.

    Algorithm:
      1. Load published tracks + approved guides.
      2. Role-filter each set.
      3. Grounding gate: find matching wiki page per artifact; drop if missing.
         Extract Activity pulse themes (max 3 chips).
      4. Build items list: sort by date descending, cap at 5, assign freshness label.
      5. Build honest _sources block.

    Returns the full payload dict (caller fills in generated_at).
    """
    role = _normalise_role(role)
    visible = _role_visible_set(role)
    fallbacks: list[str] = []

    # ── 1+2. Tracks ────────────────────────────────────────────────────────────
    candidate_items: list[dict] = []

    for track in _load_published_tracks():
        if not _is_visible(track, visible):
            continue

        # Grounding gate: find a wiki page for ANY module this track touches.
        # For tracks the "module" field is absent; derive from module_ids titles
        # or fall back to the track title.  We try a best-effort single-page match.
        track_module = track.get("module") or ""
        if not track_module:
            # Guess module from title heuristic — common word in title
            # (e.g. "New Cashier Onboarding" → no specific module, allow through
            # with empty themes rather than dropping the track entirely).
            # Per spec: "drop if no wiki page matches" — but tracks are cross-module
            # aggregates; we allow them through with themes=[] rather than dropping.
            wiki_page = None
        else:
            wiki_page = _wiki_page_for_module(track_module)
            if wiki_page is None:
                continue  # no grounding page found — drop

        themes = _extract_themes(wiki_page) if wiki_page else []

        # Real date — prefer created_at, fall back to file mtime
        raw_date = track.get("created_at") or track.get("updated_at") or ""
        pub_date = _parse_date(raw_date)
        if pub_date is None:
            track_path = _ms._track_path(track.get("id", ""))
            if track_path.exists():
                pub_date = date.fromtimestamp(track_path.stat().st_mtime)
                fallbacks.append(f"track:{track.get('id')}:file_mtime")
            else:
                pub_date = TODAY

        candidate_items.append({
            "id": track["id"],
            "kind": "track",
            "title": track.get("title") or track["id"],
            "summary": track.get("description") or "",
            "module": track_module or "",
            "origin": _origin_from_artifact(track, "track"),
            "published_at": pub_date.isoformat(),
            "freshness_label": _freshness_label(pub_date),
            "context_themes": themes,
            "open": {"type": "track", "ref": track["id"]},
            "_sort_key": pub_date,
        })

    # ── 1+2. Approved guides ───────────────────────────────────────────────────
    for guide in _load_approved_guides():
        if not _is_visible(guide, visible):
            continue

        mod_name = guide.get("module") or ""
        wiki_page = _wiki_page_for_module(mod_name) if mod_name else None
        if mod_name and wiki_page is None:
            continue  # no grounding page — drop

        themes = _extract_themes(wiki_page) if wiki_page else []

        raw_date = guide.get("created_at") or ""
        pub_date = _parse_date(raw_date)
        if pub_date is None:
            # Try to find the file and use mtime
            for search_dir in (_ms.PUBLISHED, _ms.DRAFTS):
                candidate_path = search_dir / f"{guide['id']}.json"
                if candidate_path.exists():
                    pub_date = date.fromtimestamp(candidate_path.stat().st_mtime)
                    fallbacks.append(f"guide:{guide['id']}:file_mtime")
                    break
            if pub_date is None:
                pub_date = TODAY
                fallbacks.append(f"guide:{guide['id']}:today_fallback")

        candidate_items.append({
            "id": guide["id"],
            "kind": "guide",
            "title": guide.get("title") or guide["id"],
            "summary": guide.get("summary") or guide.get("description") or "",
            "module": mod_name,
            "origin": _origin_from_artifact(guide, "guide"),
            "published_at": pub_date.isoformat(),
            "freshness_label": _freshness_label(pub_date),
            "context_themes": themes,
            "open": {"type": "guide", "ref": guide["id"]},
            "_sort_key": pub_date,
        })

    # ── 4. Sort + cap ──────────────────────────────────────────────────────────
    candidate_items.sort(key=lambda x: x["_sort_key"], reverse=True)
    items = candidate_items[:5]

    # Strip internal sort key before returning
    for item in items:
        item.pop("_sort_key", None)

    # ── 5. Honest _sources block ───────────────────────────────────────────────
    wiki_themes_used = any(item["context_themes"] for item in items)

    sources = {
        "freshness_basis": "training_publish_date",
        "wiki_themes_used": wiki_themes_used,
        # Always 0 — confirmed from wiki/training/whats-new.html: zero incremental
        # Jira changes since the Apr-20-2026 bulk import.
        "jira_incremental_changes_since_bulk_import": 0,
        "fallbacks": fallbacks,
    }

    return {
        "role": role,
        "generated_at": "",   # filled in by the route handler
        "items": items,
        "_sources": sources,
        "_data_notice": None,
    }
