"""Assemble the self-contained District-Admin Studio share file.

Takes the REAL app (static/index.html) and injects a fetch shim (Block A) that
REPLAYS real API responses captured for the CN Director (dana-director) persona,
plus a UI layer (Block B) that boots the app as the CN Director and lands on
"My Team" (the district training-supervisor surface). Output is one shareable
HTML file with no server dependency — "what the admin would see", cached.

Rebuild:
    python demo_app.py                                  # :8001 (real backend)
    python share/_capture/capture_director.py           # capture dana-director data
    python share/build_share_director.py                # -> share/district-admin-studio.html
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # learning-agent/
SHARE = os.path.join(ROOT, "share")
CAP = os.path.join(SHARE, "_capture")
SHIM = os.path.join(SHARE, "_shim")
INDEX = os.path.join(ROOT, "static", "index.html")
OUT = os.path.join(SHARE, "district-admin-studio.html")


def build_seed():
    with open(os.path.join(CAP, "captures_director.json"), encoding="utf-8") as f:
        caps = json.load(f)

    by_path = {}
    for key, c in caps.items():
        if c.get("status") != 200 or not c.get("body"):
            continue
        path = (c.get("path") or "").split("?")[0]
        if not path:
            continue
        try:
            by_path[path] = json.loads(c["body"])
        except Exception:
            by_path[path] = c["body"]   # non-JSON (rare) — kept as raw string

    # essentials with safe fallbacks (so the app never hits an undefined read)
    by_path.setdefault("/api/me", {"signed_in": False})
    by_path.setdefault("/api/whats-new", {"items": []})
    by_path.setdefault("/api/regulatory-dates", {"deadlines": [], "total": 0})
    by_path.setdefault("/api/flashcards", {"flashcards": []})
    by_path.setdefault("/api/certificates", {"certificates": []})

    missing = [p for p in ("/api/config", "/api/tracks", "/api/roster") if p not in by_path]
    if missing:
        raise SystemExit("Missing required captures: %s — run capture_director.py against a live :8001" % missing)

    seed = {
        "byPath": by_path,
        "initialStore": {
            "progress": {"lessons_done": {}, "modules_done": [], "certified": False,
                         "assessment_passed": False, "assessment_score": None},
            "attempts": {}, "certs": [],
        },
    }
    return seed, by_path


def main():
    seed, by_path = build_seed()
    seed_json = json.dumps(seed, ensure_ascii=False)
    # never let an embedded "</script>" terminate our injected <script> block
    seed_json = re.sub(r"</(script)", r"<\\/\1", seed_json, flags=re.I)

    with open(os.path.join(SHIM, "shim_head_director.js"), encoding="utf-8") as f:
        block_a = f.read().replace("__SEED__", seed_json)
    with open(os.path.join(SHIM, "shim_tail_director.js"), encoding="utf-8") as f:
        block_b = f.read()

    with open(INDEX, encoding="utf-8") as f:
        html = f.read()

    marker = "\n<script>\n"
    idx = html.find(marker)
    if idx < 0:
        raise SystemExit("could not find main <script> open marker")
    inject_at = idx + len(marker)
    banner_a = "\n/* ===== District-Admin Studio: standalone backend shim (injected) ===== */\n"
    html = html[:inject_at] + banner_a + block_a + "\n" + html[inject_at:]

    close_idx = html.rfind("</script>")
    if close_idx < 0:
        raise SystemExit("could not find closing </script>")
    banner_b = "\n/* ===== District-Admin Studio: standalone UI layer (injected) ===== */\n"
    html = html[:close_idx] + banner_b + block_b + "\n" + html[close_idx:]

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("Wrote", OUT)
    print("  size:", round(len(html) / 1024), "KB")
    print("  seed:", round(len(seed_json) / 1024), "KB")
    print("  captured endpoints:", len(by_path))
    # quick inventory so the build log shows what's real
    roster = by_path.get("/api/roster", {})
    tracks = by_path.get("/api/tracks", {})
    print("  roster rows:", len(roster.get("roster", [])), "| districts:", len(roster.get("districts", [])),
          "| director tracks:", len(tracks.get("tracks", [])),
          "| modules:", by_path.get("/api/modules", {}).get("total", 0))


if __name__ == "__main__":
    main()
