"""Capture real API responses from the running Learning Studio backend so the
self-contained share file can be seeded with the EXACT real data + shapes.
Run while demo_app is serving on :8001."""
import json, urllib.request, urllib.error, os

BASE = "http://localhost:8001"
OUT = os.path.dirname(os.path.abspath(__file__))

def get(path, persona=None):
    req = urllib.request.Request(BASE + path)
    if persona:
        req.add_header("X-Demo-User", persona)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8", "replace")
            ct = r.headers.get("Content-Type", "")
            return {"status": r.status, "ct": ct, "body": body}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "ct": "", "body": e.read().decode("utf-8", "replace")}
    except Exception as e:
        return {"status": -1, "ct": "", "body": str(e)}

cap = {}
def grab(key, path, persona=None):
    r = get(path, persona)
    cap[key] = {"path": path, "persona": persona, **r}
    j = None
    try: j = json.loads(r["body"])
    except Exception: pass
    n = (len(j) if isinstance(j, list) else
         (len(j.get("tracks", j.get("modules", j.get("items", j.get("courses", j.get("resources", [])))))) if isinstance(j, dict) else "?"))
    print(f"  [{r['status']}] {path}  ({persona or '-'})  ~{n} items, {len(r['body'])} bytes")
    return j

print("== identity / config ==")
grab("config", "/api/config")
grab("me_cashier", "/api/me", "john-cashier")
grab("me_trainer", "/api/me", "sam-trainer")

print("== learner (cashier) ==")
tracks_cashier = grab("tracks_cashier", "/api/tracks", "john-cashier")
grab("whats_next", "/api/whats-next", "john-cashier")
grab("whats_new", "/api/whats-new?role=Cashier", "john-cashier")
grab("certificates", "/api/certificates", "john-cashier")
grab("flashcards", "/api/flashcards?status=approved", "john-cashier")
grab("quizzes", "/api/quizzes?status=approved", "john-cashier")
grab("icn", "/api/icn", "john-cashier")

print("== trainer builder ==")
tracks_trainer = grab("tracks_trainer", "/api/tracks", "sam-trainer")
grab("courses", "/api/courses", "sam-trainer")
grab("modules", "/api/modules", "sam-trainer")
grab("assessments", "/api/assessments", "sam-trainer")
grab("stats_content", "/api/stats/content", "sam-trainer")
grab("resources", "/resources", "sam-trainer")

# expand each cashier track + collect referenced courses/assessments
ref_courses, ref_assessments = set(), set()
def expand_tracks(tracks, persona, tag):
    if not isinstance(tracks, dict): return
    for t in tracks.get("tracks", []):
        tid = t.get("id")
        j = grab(f"track_{tag}_{tid}", f"/api/tracks/{tid}", persona)
        if isinstance(j, dict):
            for cid in (j.get("course_ids") or []): ref_courses.add(cid)
            if j.get("assessment_gate_id"): ref_assessments.add(j["assessment_gate_id"])
            for c in (j.get("courses") or []):
                if c.get("id"): ref_courses.add(c["id"])

expand_tracks(tracks_cashier, "john-cashier", "c")
expand_tracks(tracks_trainer, "sam-trainer", "t")

print("== referenced courses ==")
for cid in sorted(ref_courses):
    j = grab(f"course_{cid}", f"/api/courses/{cid}", "john-cashier")
    if isinstance(j, dict):
        for l in (j.get("lessons") or []):
            if l.get("type") in ("quiz","assessment") and l.get("ref"): ref_assessments.add(l["ref"])

print("== referenced assessments ==")
for aid in sorted(ref_assessments):
    grab(f"assessment_{aid}", f"/api/assessments/{aid}", "john-cashier")

out_path = os.path.join(OUT, "captures.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(cap, f, indent=1)
print(f"\nSaved {len(cap)} captures -> {out_path}")
