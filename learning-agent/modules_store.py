"""Track persistence and Module aggregation for the Learning Studio Module/Track layer.

Tracks are stored as JSON files in data/tracks/<id>.json.
Modules are aggregated on-the-fly from three sources:
  - AI_TRANSCRIPT : approved AI-generated guides in drafts/ (method != imported_guide)
  - HUMAN_GUIDE   : imported Cybersoft guides in drafts/ (origin == internal)
  - ICN_DOC       : ICN/USDA catalog entries (embed_only or download_allowed)
"""
import json
import re
import uuid
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
TRACKS_DIR = BASE / "data" / "tracks"
TRACKS_DIR.mkdir(parents=True, exist_ok=True)

DRAFTS = BASE / "drafts"
PUB_META = BASE / "published" / "metadata"
PUBLISHED = BASE / "published"

# ── ID helpers ─────────────────────────────────────────────────────────────────

def _new_track_id() -> str:
    return "track-" + datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]


# ── Track CRUD ─────────────────────────────────────────────────────────────────

def _track_path(tid: str) -> Path:
    return TRACKS_DIR / f"{tid}.json"


def list_tracks() -> list[dict]:
    out = []
    for p in sorted(TRACKS_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return out


def load_track(tid: str) -> dict | None:
    p = _track_path(tid)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_track(track: dict) -> dict:
    _track_path(track["id"]).write_text(json.dumps(track, indent=2, ensure_ascii=False), encoding="utf-8")
    return track


def create_track(title: str, description: str = "", product: str = "SchoolCafé",
                 role_tags: list | None = None) -> dict:
    track = {
        "id": _new_track_id(),
        "title": title,
        "description": description,
        "product": product or "SchoolCafé",
        "role_tags": role_tags or [],
        "module_ids": [],
        "quiz_id": None,
        "status": "draft",
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    return save_track(track)


def delete_track(tid: str) -> bool:
    p = _track_path(tid)
    if p.exists():
        p.unlink()
        return True
    return False


# ── Module aggregation ─────────────────────────────────────────────────────────

def _read_meta(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _in_library(m: dict) -> bool:
    return m.get("approved") is True or m.get("status") in ("approved", "published")


def _module_source(meta: dict) -> str:
    if meta.get("origin") == "internal" or meta.get("method") == "imported_guide":
        return "HUMAN_GUIDE"
    return "AI_TRANSCRIPT"


def _resource_to_module(meta: dict) -> dict | None:
    if not _in_library(meta):
        return None
    return {
        "id": meta.get("id") or "",
        "title": meta.get("title") or (
            f"{meta.get('module', '')} — {meta.get('template', '')}".strip(" —")
        ),
        "module": meta.get("module") or "",
        "product": meta.get("platform_label") or meta.get("platform") or "SchoolCafé",
        "source": _module_source(meta),
        "template": meta.get("template"),
        "role_tags": list(meta.get("role_tags") or []),
        "duration_min": meta.get("duration_min"),
        "status": "approved",
        "created_at": meta.get("created_at") or "",
    }


def _load_resource_modules() -> list[dict]:
    """Aggregate AI_TRANSCRIPT + HUMAN_GUIDE modules from drafts/ and published/."""
    seen: set[str] = set()
    out: list[dict] = []
    for html in sorted(PUBLISHED.glob("*.html")):
        rid = html.stem
        meta = _read_meta(PUB_META / f"{rid}.json") or {}
        meta.setdefault("id", rid)
        meta.setdefault("status", "published")
        mod = _resource_to_module(meta)
        if mod and rid not in seen:
            seen.add(rid)
            out.append(mod)
    for html in sorted(DRAFTS.glob("*.html")):
        rid = html.stem
        meta = _read_meta(DRAFTS / f"{rid}.json") or {}
        meta.setdefault("id", rid)
        meta.setdefault("status", "draft")
        mod = _resource_to_module(meta)
        if mod and rid not in seen:
            seen.add(rid)
            out.append(mod)
    return out


def _load_icn_modules(icn_dir: Path) -> list[dict]:
    """Build ICN_DOC module entries from the ICN asset manifest + LMS content cards."""
    lms_path = icn_dir / "data" / "lms_mockup_content.json"
    manifest_path = icn_dir / "data" / "asset_manifest.json"
    if not lms_path.exists():
        return []
    try:
        lms = json.loads(lms_path.read_text(encoding="utf-8"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []
    except (json.JSONDecodeError, OSError):
        return []

    by_id = {a.get("asset_id"): a for a in manifest}
    out = []
    for c in lms.get("content_cards") or []:
        aid = c.get("asset_id")
        a = by_id.get(aid, {})
        lp = c.get("license_posture") or a.get("license_posture") or "link_only"
        if lp == "link_only":
            continue  # link-only assets can't be embedded as modules
        title = (c.get("title") or "").strip() or aid or ""
        out.append({
            "id": f"icn-{aid}",
            "title": title,
            "module": ", ".join(c.get("topic_tags") or []) or "ICN",
            "product": "All",
            "source": "ICN_DOC",
            "template": c.get("asset_type"),
            "role_tags": list(c.get("role_tags") or []),
            "duration_min": None,
            "status": "approved",
            "created_at": "",
            # source_url lets the learner open the credited ICN reference (link-out, never reproduced).
            "source_url": c.get("source_url") or a.get("source_url") or a.get("url") or "",
        })
    return out


def list_modules(source: str = "", product: str = "", role: str = "", q: str = "",
                 icn_dir: Path | None = None) -> dict:
    """Return filtered module list across all sources."""
    mods = _load_resource_modules()
    if icn_dir is not None:
        mods += _load_icn_modules(icn_dir)

    # count before filtering
    counts: dict[str, int] = {}
    for m in mods:
        counts[m["source"]] = counts.get(m["source"], 0) + 1

    # apply filters
    q_norm = q.strip().lower() if q else ""
    def _match(m: dict) -> bool:
        if source and m["source"] != source:
            return False
        if product and product.lower() not in (m.get("product") or "").lower():
            return False
        if role and role not in (m.get("role_tags") or []):
            return False
        if q_norm:
            hay = ((m.get("title") or "") + " " + (m.get("module") or "")).lower()
            if q_norm not in hay:
                return False
        return True

    filtered = [m for m in mods if _match(m)]
    return {"modules": filtered, "total": len(filtered), "sources": counts}


def expand_track(track: dict, icn_dir: Path | None = None) -> dict:
    """Return track with 'modules' key containing expanded module objects."""
    all_mods_resp = list_modules(icn_dir=icn_dir)
    by_id = {m["id"]: m for m in all_mods_resp["modules"]}
    expanded = [by_id[mid] for mid in (track.get("module_ids") or []) if mid in by_id]
    return {**track, "modules": expanded}
