"""seed_demo_quizzes.py — seed known-good APPROVED quizzes for the demo track's guides.

WHY: live quiz generation goes through the Claude Agent SDK (the `claude` CLI as a
subprocess). In some launch environments that subprocess can't spawn, so a LIVE
"Take quiz" on a track module returns zero verified questions and the learner
dead-ends ("No verifiable questions"). Per the trust rule we do NOT lower the
grounding bar — instead we pre-build and APPROVE a quiz whose every question's
`source_quote` is a VERBATIM span of the published guide text. The deterministic
grounding gate (quiz_store.qa_gate) is the authority: this script refuses to
approve anything it can't ground, exactly like the live path.

Idempotent: re-running replaces prior seeded quizzes (marker: "seed_demo": True)
for the same source. Real/non-seed quizzes are never touched.

Run with the demo server's venv python:
    <venv>\\Scripts\\python.exe seed_demo_quizzes.py
"""
from __future__ import annotations

import sys
from datetime import datetime

import demo_app
import quiz_store

# rid -> list of authored questions. Every source_quote below is copied verbatim
# from the guide's published text (whitespace-insensitive, case-insensitive match
# is what the gate enforces). Sections marked [TO VERIFY] in the guide are avoided.
SEEDS = {
    "20260603-124709-item-management-long-form-68d6de": [
        {
            "q": "Before you can create or import items in Item Management, how many configuration records must already exist?",
            "options": ["Six", "Two", "Four", "Ten"],
            "answer": 0,
            "explanation": "Item setup validates each value against six existing configuration tables.",
            "source_quote": "six configuration records must already exist in the system",
            "excerpt_id": "Prerequisites",
        },
        {
            "q": "The Excel bulk import process is managed through the Import Dashboard in how many steps?",
            "options": ["Four", "Three", "Six", "Two"],
            "answer": 0,
            "explanation": "Pre-Upload, File Upload, Field Mapping, and Review & Activate.",
            "source_quote": "The process follows four steps managed through the Import Dashboard",
            "excerpt_id": "Excel Bulk Import",
        },
        {
            "q": "When you add the very first pack size to an item, what is true about the Sub-Qty field?",
            "options": [
                "It is not enabled for the first pack size",
                "It is mandatory on the first pack size",
                "It auto-fills from the Item card",
                "It must always equal 1",
            ],
            "answer": 0,
            "explanation": "Sub-Qty activates only when a second pack size is added.",
            "source_quote": "The first pack size you add does not have Sub-Qty enabled",
            "excerpt_id": "Units Card",
        },
        {
            "q": "How does the Inventory Readiness banner behave?",
            "options": [
                "As a persistent status that is always displayed",
                "As a one-time gate shown only at item creation",
                "It appears only when an error occurs",
                "It appears only after cost is entered",
            ],
            "answer": 0,
            "explanation": "It is a live status indicator, not a sequential gate.",
            "source_quote": "Inventory Readiness operates as a persistent status rather than a sequential gate",
            "excerpt_id": "Inventory Readiness",
        },
        {
            "q": "When defining a custom allergen, which data source is available?",
            "options": ["Local only", "Local or Cloud", "A USDA feed", "The vendor catalog"],
            "answer": 0,
            "explanation": "Only the Local data source is available, and exactly one must be chosen.",
            "source_quote": "only the Local data source is available",
            "excerpt_id": "Custom Allergen",
        },
        {
            "q": "What are the three standard HACCP process options when configuring recipe steps?",
            "options": [
                "No Cook, Same Day Service, and Complex Food",
                "Raw, Cooked, and Frozen",
                "Hot, Cold, and Ambient",
                "Prep, Cook, and Serve",
            ],
            "answer": 0,
            "explanation": "Selecting one of these HACCP processes is required.",
            "source_quote": "The three standard process options are No Cook, Same Day Service, and Complex Food",
            "excerpt_id": "HACCP Process",
        },
    ],
    "GUIDE-001": [
        {
            "q": "Where do you go to manage Site Configuration?",
            "options": [
                "System > Sites & Users > Site Configuration",
                "System > Management > Roles and Permissions",
                "System > Configuration > Settings",
                "System > Management > Periods",
            ],
            "answer": 0,
            "explanation": "Site Configuration lives under Sites & Users.",
            "source_quote": "go to System > Sites & Users > Site Configuration",
            "excerpt_id": "Site Configuration",
        },
        {
            "q": "What is true about Standard Roles in Roles and Permissions?",
            "options": [
                "They cannot be edited or deleted",
                "They can be deleted but not edited",
                "They are created per site",
                "They expire each academic year",
            ],
            "answer": 0,
            "explanation": "Only Custom Roles can be edited; standard ones are locked.",
            "source_quote": "Standard Roles cannot be edited or deleted",
            "excerpt_id": "Roles and Permissions",
        },
        {
            "q": "When must Program Configuration be set up?",
            "options": [
                "Before the start of each academic year",
                "After the first claim is filed",
                "Only when adding a new site",
                "Once per month",
            ],
            "answer": 0,
            "explanation": "It must precede the academic year and drives reimbursement claim calculations.",
            "source_quote": "Program Configuration must be set up before the start of each academic year",
            "excerpt_id": "Program Configuration",
        },
        {
            "q": "What is required when editing a System Setting?",
            "options": [
                "A comment explaining the change",
                "Manager approval",
                "A site selection",
                "A fiscal year",
            ],
            "answer": 0,
            "explanation": "A comment as to why the setting is being changed is mandatory.",
            "source_quote": "Comments are required when editing a System Setting",
            "excerpt_id": "Settings",
        },
        {
            "q": "Which programs does the Special Assistance Program function enable?",
            "options": [
                "Provision II and CEP",
                "NSLP and SBP only",
                "Summer Feeding and After-School",
                "Provision I and Provision III",
            ],
            "answer": 0,
            "explanation": "Program Type is CEP or Provision II.",
            "source_quote": "enables programs like Provision II and CEP for district reimbursement",
            "excerpt_id": "Special Assistance Program",
        },
        {
            "q": "The Periods function generates Periods for which two areas?",
            "options": ["POS and Inventory", "POS and Payroll", "Inventory and Menu Planning", "Claims and Eligibility"],
            "answer": 0,
            "explanation": "Period Type is POS or Inventory.",
            "source_quote": "generate Periods for POS and Inventory",
            "excerpt_id": "Periods",
        },
    ],
}


def main() -> int:
    now = datetime.now().isoformat(timespec="seconds")
    failures = 0
    for rid, questions in SEEDS.items():
        got = demo_app._resource_excerpts(rid)
        if not got:
            print(f"!! {rid}: resource not found — SKIP")
            failures += 1
            continue
        _excerpts, source_text, title, label = got

        # Idempotent: drop prior seeded quizzes for this source before re-creating.
        for row in quiz_store.list_quizzes():
            if row.get("source_id") == rid:
                q = quiz_store.load_quiz(row["id"]) or {}
                if q.get("seed_demo"):
                    quiz_store.delete_quiz(row["id"])
                    print(f"   (removed prior seed {row['id']})")

        quiz = quiz_store.build_quiz(
            source_type="resource", source_id=rid, source_label=label,
            title=f"Knowledge check — {title}",
            generated_questions=questions, source_text=source_text,
        )

        # The gate is the authority. Refuse to approve anything not fully grounded.
        report = quiz_store.qa_gate(quiz, source_text)
        ungrounded = [i + 1 for i, q in enumerate(quiz["questions"]) if not q.get("grounded")]
        print(f"== {rid}  ({title})")
        print(f"   questions={report['total']} grounded={report['grounded']} ok={report['ok']}")
        if ungrounded:
            print(f"   !! ungrounded questions: {ungrounded} — NOT approving")
        if report["blocking"]:
            print(f"   !! blocking: {report['blocking']}")
        if not report["ok"]:
            failures += 1
            # leave it as a draft so the bad span is inspectable, then continue
            quiz["seed_demo"] = True
            quiz_store.save_quiz(quiz)
            continue

        quiz["status"] = "approved"
        quiz["approved"] = True
        quiz["approved_at"] = now
        quiz["stale"] = False
        quiz["seed_demo"] = True
        quiz_store.save_quiz(quiz)
        print(f"   -> APPROVED  id={quiz['id']}")
    print("\nDONE" if not failures else f"\nDONE with {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
