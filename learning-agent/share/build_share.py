"""Assemble the self-contained Cashier Training Studio share file.

Takes the REAL app (static/index.html), injects a localStorage-backed fetch shim
(Block A, top of the app script) seeded with REAL captured content, plus a UI layer
(Block B, bottom of the app script) that removes district management and adds
sequential gating. Output is one shareable HTML file with no server dependency.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # learning-agent/
SHARE = os.path.join(ROOT, "share")
CAP = os.path.join(SHARE, "_capture")
SHIM = os.path.join(SHARE, "_shim")
INDEX = os.path.join(ROOT, "static", "index.html")
OUT = os.path.join(SHARE, "cashier-training-studio.html")


def jload(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def cap_body(captures, key):
    return json.loads(captures[key]["body"])


# ---------------------------------------------------------------- webinar cards
def webinar_html(part, url):
    return f"""<div style="max-width:680px;margin:0 auto;">
  <div style="display:inline-flex;align-items:center;gap:8px;font-size:12px;font-weight:800;color:#7A520A;background:#FEF3D0;border:1px solid #F0D79A;border-radius:999px;padding:4px 12px;margin-bottom:14px;">&#9733; MAIN CONTENT &mdash; START HERE</div>
  <div style="border:1px solid #E4E7E2;border-radius:14px;padding:28px;text-align:center;background:#F4F6F3;">
    <div style="font-size:46px;line-height:1;">&#9654;</div>
    <h3 style="font-family:Fraunces,Georgia,serif;font-size:20px;margin:10px 0 4px;color:#14201A;">POS Training, Part {part}</h3>
    <div style="font-size:13px;color:#50665A;margin-bottom:18px;">GoToWebinar recording &middot; Cybersoft &middot; ~60 min</div>
    <a href="{url}" target="_blank" rel="noopener" style="display:inline-block;background:#22573E;color:#fff;font-weight:700;font-size:15px;padding:12px 22px;border-radius:10px;text-decoration:none;">Watch the recording &#8599;</a>
    <p style="font-size:13px;color:#50665A;margin:18px auto 0;max-width:48ch;line-height:1.6;">The webinar opens in a new tab. When you&rsquo;ve finished watching, return here and choose <b>&ldquo;Mark as read&rdquo;</b> below so the next step unlocks. The quizzes that follow are supplemental &mdash; they confirm what the webinar taught.</p>
  </div>
</div>"""


def build_seed():
    captures = jload(os.path.join(CAP, "captures.json"))
    config = cap_body(captures, "config")
    whats_next = cap_body(captures, "whats_next")
    whats_new = cap_body(captures, "whats_new")
    stats = cap_body(captures, "stats_content")
    assessment = cap_body(captures, "assessment_assessment-demo-cashier-onboard")

    quiz_cashier = jload(os.path.join(CAP, "quiz_cashier.json"))
    quiz_food = jload(os.path.join(CAP, "quiz_foodsafety.json"))
    icn_asset = jload(os.path.join(CAP, "icn_video.json"))

    WEB1 = "https://register.gotowebinar.com/recording/6807993921182028034"
    WEB2 = "https://register.gotowebinar.com/recording/3571326358152159748"
    ICN_ID = "icn-food-safety-youtube-hand-hygiene-demo"

    # ---- curated chapters (courses) ----
    ch1 = {
        "id": "cts-ch-pos", "title": "Chapter 1 · Point of Sale — Core Skills",
        "description": "Start with the POS webinar, then prove the core register workflows.",
        "product": "SchoolCafé", "role_tags": ["Cashier"], "status": "published",
        "lessons": [
            {"type": "guide", "ref": "webinar-pos-1", "title": "Webinar — POS Training, Part 1",
             "duration_est": 60, "origin_badge": "outside_vendor", "source_name": "GoToWebinar · Cybersoft"},
            {"type": "quiz", "ref": "quiz-seed-cashier-demo", "title": "Knowledge Check — Point of Sale",
             "duration_est": 10, "origin_badge": "ai_grounded"},
        ],
    }
    ch2 = {
        "id": "cts-ch-foodsafety", "title": "Chapter 2 · Food Safety at the Register",
        "description": "Watch the ICN hand-hygiene video, then take the food-safety check.",
        "product": "SchoolCafé", "role_tags": ["Cashier"], "status": "published",
        "lessons": [
            {"type": "video", "ref": ICN_ID, "title": "Food Safety: Hand Hygiene in School Nutrition",
             "duration_est": 4, "origin_badge": "outside_vendor", "source_name": "Institute of Child Nutrition / USDA"},
            {"type": "quiz", "ref": "quiz-seed-food-safety-3q", "title": "Knowledge Check — Food Safety",
             "duration_est": 5, "origin_badge": "ai_grounded"},
        ],
    }
    ch3 = {
        "id": "cts-ch-wrap", "title": "Chapter 3 · Daily Operations & Certification",
        "description": "Finish with Part 2 of the POS webinar, then earn your certificate.",
        "product": "SchoolCafé", "role_tags": ["Cashier"], "status": "published",
        "lessons": [
            {"type": "guide", "ref": "webinar-pos-2", "title": "Webinar — POS Training, Part 2",
             "duration_est": 60, "origin_badge": "outside_vendor", "source_name": "GoToWebinar · Cybersoft"},
        ],
    }

    track = {
        "id": "track-cashier-share",
        "title": "Cashier Onboarding — Point of Sale & Food Safety",
        "description": "Everything a new SchoolCafé cashier needs on day one: point-of-sale workflows and food-safety basics. The webinars are the main event; the checks confirm you've got it. Finish each chapter to unlock the next.",
        "product": "SchoolCafé", "role_tags": ["Cashier"], "status": "published",
        "course_ids": ["cts-ch-pos", "cts-ch-foodsafety", "cts-ch-wrap"],
        "module_ids": [],
        "assessment_gate_id": "assessment-demo-cashier-onboard",
        "quiz_id": None, "sequential": True,
        "due_date": "2026-07-31",
        "assignments": [{"audience": "Cashier", "audience_type": "role", "audience_value": "Cashier",
                         "district": "houston-isd", "due_date": "2026-07-31",
                         "assigned_at": "2026-06-13T00:00:00", "assigned_by": "sam-trainer"}],
        "milestones": [], "prerequisites": [],
        "created_at": "2026-06-13T00:00:00", "updated_at": "2026-06-16T00:00:00",
    }

    # normalize quiz shape: ensure {id, title, questions}
    def norm_quiz(q):
        return {"id": q["id"], "title": q.get("title", "Quiz"), "status": "approved",
                "questions": q.get("questions", [])}

    icn_module = {"id": ICN_ID, "title": icn_asset.get("title"), "module": "Food Safety",
                  "product": "SchoolCafé", "source": "ICN_DOC", "template": "video",
                  "role_tags": ["Cashier"], "duration_min": icn_asset.get("duration_min", 4),
                  "status": "approved", "created_at": "2026-06-13T00:00:00"}

    icn_card = {"asset_id": ICN_ID, "title": icn_asset.get("title"),
                "asset_type": "YouTube Video", "license_posture": "embed_only",
                "duration_min": icn_asset.get("duration_min", 4),
                "source_org": "Institute of Child Nutrition"}

    seed = {
        "config": config,
        "me": {"signed_in": False},
        "track": track,
        "courses": [ch1, ch2, ch3],
        "quizzes": [norm_quiz(quiz_cashier), norm_quiz(quiz_food)],
        "assessments": [assessment],
        "icnCatalog": {"cards": [icn_card], "total": 1},
        "icnAssets": {ICN_ID: icn_asset},
        "resourcesHtml": {
            "webinar-pos-1": webinar_html(1, WEB1),
            "webinar-pos-2": webinar_html(2, WEB2),
        },
        "resourcesList": [],
        "modules": {"modules": [icn_module], "total": 1,
                    "sources": {"AI_TRANSCRIPT": 0, "HUMAN_GUIDE": 0, "ICN_DOC": 1}},
        "whatsNext": whats_next,
        "whatsNew": whats_new,
        "stats": stats,
        "flashcards": {"flashcards": []},
        "initialStore": {
            "progress": {"lessons_done": {}, "modules_done": [], "certified": False,
                         "assessment_passed": False, "assessment_score": None},
            "attempts": {}, "userTracks": [], "userCourses": [], "userQuizzes": [],
            "userAssessments": [], "certs": [],
        },
    }
    return seed


def main():
    seed = build_seed()
    seed_json = json.dumps(seed, ensure_ascii=False)
    # never let an embedded "</script>" terminate our injected <script> block
    seed_json = re.sub(r"</(script)", r"<\\/\1", seed_json, flags=re.I)

    with open(os.path.join(SHIM, "shim_head.js"), encoding="utf-8") as f:
        block_a = f.read().replace("__SEED__", seed_json)
    with open(os.path.join(SHIM, "shim_tail.js"), encoding="utf-8") as f:
        block_b = f.read()

    with open(INDEX, encoding="utf-8") as f:
        html = f.read()

    marker = "\n<script>\n"
    idx = html.find(marker)
    if idx < 0:
        raise SystemExit("could not find main <script> open marker")
    inject_at = idx + len(marker)
    banner_a = "\n/* ===== Cashier Training Studio: standalone backend shim (injected) ===== */\n"
    html = html[:inject_at] + banner_a + block_a + "\n" + html[inject_at:]

    close_idx = html.rfind("</script>")
    if close_idx < 0:
        raise SystemExit("could not find closing </script>")
    banner_b = "\n/* ===== Cashier Training Studio: standalone UI layer (injected) ===== */\n"
    html = html[:close_idx] + banner_b + block_b + "\n" + html[close_idx:]

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("Wrote", OUT)
    print("  size:", round(len(html) / 1024), "KB")
    print("  seed:", round(len(seed_json) / 1024), "KB")


if __name__ == "__main__":
    main()
