"""Capture real API responses for the CN DIRECTOR (dana-director) persona so the
self-contained District-Admin Studio share file is seeded with the EXACT real data
the admin would see (My Team roster, compliance, assigned tracks).

Run while demo_app is serving on :8001:
    python share/_capture/capture_director.py
Writes share/_capture/captures_director.json
"""
import json, urllib.request, urllib.error, os

BASE = "http://localhost:8001"
OUT = os.path.dirname(os.path.abspath(__file__))
PERSONA = "dana-director"


def get(path, persona=PERSONA):
    req = urllib.request.Request(BASE + path)
    if persona:
        req.add_header("X-Demo-User", persona)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return {"status": r.status, "ct": r.headers.get("Content-Type", ""),
                    "body": r.read().decode("utf-8", "replace")}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "ct": "", "body": e.read().decode("utf-8", "replace")}
    except Exception as e:
        return {"status": -1, "ct": "", "body": str(e)}


cap = {}


def grab(key, path, persona=PERSONA):
    r = get(path, persona)
    cap[key] = {"path": path, "persona": persona, **r}
    print(f"  [{r['status']}] {path}  ({persona})  {len(r['body'])} bytes")
    try:
        return json.loads(r["body"])
    except Exception:
        return None


print("== identity / config ==")
grab("config", "/api/config")
grab("me", "/api/me")

print("== director: assigned tracks ==")
tracks = grab("tracks", "/api/tracks")
track_ids = []
if isinstance(tracks, dict):
    for t in tracks.get("tracks", []):
        tid = t.get("id")
        if tid:
            track_ids.append(tid)
            grab(f"track_{tid}", f"/api/tracks/{tid}")

print("== director: My Team roster + compliance ==")
grab("roster", "/api/roster")
for tid in track_ids:
    grab(f"roster_track_{tid}", f"/api/roster/{tid}")
# also grab the E1 roster for the canonical cashier-onboarding track (My Team "Insights"
# default + the track most demo rosters key on)
for tid in ("track-g1-cashier-onboarding", "track-g1-manager-essentials"):
    if tid not in track_ids:
        grab(f"roster_track_{tid}", f"/api/roster/{tid}")
grab("regulatory_dates", "/api/regulatory-dates?upcoming=true")

print("== director: catalog / home rails ==")
grab("whats_next", "/api/whats-next")
grab("whats_new", "/api/whats-new?role=CN%20Director")
grab("certificates", "/api/certificates")
grab("modules", "/api/modules")
grab("icn", "/api/icn")
grab("stats_content", "/api/stats/content")
grab("flashcards", "/api/flashcards?status=approved")

out_path = os.path.join(OUT, "captures_director.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(cap, f, indent=1)
print(f"\nSaved {len(cap)} captures + {len(track_ids)} tracks -> {out_path}")
