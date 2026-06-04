"""Apply ONE consistent used/rejected rule across all FAQs from the per-function
audit JSONs (faq-builder/build/audit/<fn>.json).

Reconciliation (deterministic):
- A ticket the agent marked REJECTED is stripped from a Q&A's `sources` ONLY if that
  Q&A still has >=1 USED source left (the thin/redundant secondary citation case).
- If stripping would leave a Q&A with NO source, keep all its sources (the answer is
  grounded on that ticket) and record it as 'kept-to-preserve-answer'.
- FINAL rejected = agent-rejected tickets that do not survive in any Q&A.
- No Q&A is deleted; no content rewritten — only `sources` lists change.

Writes: updated specs/standalone files, audit/_rejected_final.json, audit/_change_report.txt
Run AFTER all 7 audit JSONs exist. Does NOT build docx/pdf (do that next, sequentially).
"""
import os, re, json, glob, runpy

BUILD = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(BUILD)
SPECS = os.path.join(BUILD, "specs")
AUDIT = os.path.join(BUILD, "audit")
CONV = os.path.join(PROJ, "conversations")
_ORIG = (r"C:\Users\RAHUL~1.MEH\AppData\Local\Temp\claude"
         r"\C--Users-rahul-mehta-Downloads-Financials-Documentation-KT-jira-brain"
         r"\04099354-c2b0-4c62-a7b5-7aaf7fd8a62f\tasks\w50plvmmx.output")
try:
    ORIG_DETAIL = {r["ticket_id"]: r for r in json.load(open(_ORIG, encoding="utf-8"))["result"]["rows"]}
except Exception:
    ORIG_DETAIL = {}

# function name -> (kind, ref, filter jsonl, audit slug)
FUNCS = [
    ("Menu Cycles",         ("py", "make_menu_cycles_faq.py"), "conversations.jsonl",                       "menu_cycles"),
    ("Ingredients",         ("py", "make_ingredients_faq.py"), "conversations_ingredients.jsonl",           "ingredients"),
    ("Transfer Items",      ("spec", "transfer_items"),        "conversations_transfer_items.jsonl",        "transfer_items"),
    ("Assign Menus",        ("spec", "assign_menus"),          "conversations_assign_menus.jsonl",          "assign_menus"),
    ("Perpetual Inventory", ("spec", "perpetual_inventory"),   "conversations_perpetual_inventory.jsonl",   "perpetual_inventory"),
    ("Receipt w/o Order",   ("spec", "receipt_wo_order"),      "conversations_receipt_wo_order.jsonl",      "receipt_wo_order"),
    ("Production Orders",   ("spec", "production_orders"),     "conversations_production_orders.jsonl",     "production_orders"),
]


def dump_spec(ns):
    out = []
    for key in ("TITLE", "OUT_BASENAME", "INTRO", "NAV_NOTE"):
        out.append(f"{key} = {ns[key]!r}\n")
    out.append("SECTIONS = [\n")
    for sec, qas in ns["SECTIONS"]:
        out.append(f"    ({sec!r}, [\n")
        for q, a, src in qas:
            out.append(f"        ({q!r},\n         {a!r},\n         {src!r}),\n")
        out.append("    ]),\n")
    out.append("]\n")
    out.append(f"CLOSING = {ns['CLOSING']!r}\n")
    out.append(f"SOURCE_NOTE = {ns['SOURCE_NOTE']!r}\n")
    return "".join(out)


def load_sections(kind, ref):
    if kind == "spec":
        ns = runpy.run_path(os.path.join(SPECS, f"{ref}_spec.py"))
    else:
        ns = {"__name__": "x", "__file__": os.path.join(PROJ, ref)}
        exec(open(os.path.join(PROJ, ref), encoding="utf-8").read(), ns)
    return ns


def ids_in(src):
    return re.findall(r"\d{5,7}", src)


def rebuild_src(ordered_ids):
    pre = "Tickets " if len(ordered_ids) != 1 else "Ticket "
    return pre + ", ".join(ordered_ids)


report = []
final_rejected_rows = []
funnel = []

for name, (kind, ref), jl, slug in FUNCS:
    audit = json.load(open(os.path.join(AUDIT, f"{slug}.json"), encoding="utf-8"))
    rej_ids = {r["ticket_id"] for r in audit["rejected"]}
    rej_detail = {r["ticket_id"]: r for r in audit["rejected"]}
    filt = set(str(json.loads(l)["ticket_id"]) for l in open(os.path.join(CONV, jl), encoding="utf-8") if l.strip())

    ns = load_sections(kind, ref)
    sections = [(s, list(qas)) for s, qas in ns["SECTIONS"]]

    kept_used = set()       # rejected-by-agent but kept to preserve an answer
    stripped = set()        # rejected-by-agent and removed from a Q&A
    changes = []            # (question, old_src, new_src)

    for si, (sec, qas) in enumerate(sections):
        for qi, (q, a, src) in enumerate(qas):
            order = ids_in(src)
            rej_here = [t for t in order if t in rej_ids]
            if not rej_here:
                continue
            used_here = [t for t in order if t not in rej_ids]
            if used_here:                       # strip the rejected secondary cites
                new_order = used_here
                stripped.update(rej_here)
                changes.append((q, src, rebuild_src(new_order)))
                qas[qi] = (q, a, rebuild_src(new_order))
            else:                               # all sources rejected -> keep to preserve answer
                kept_used.update(rej_here)

    # a stripped ticket may still survive as a cite on another Q&A
    surviving = set()
    for sec, qas in sections:
        for q, a, src in qas:
            surviving.update(ids_in(src))
    final_rej = filt - surviving                # EVERY filter ticket not cited after the strip
    # = agent-rejected non-survivors + any agent-USED ticket never written into a Q&A

    # write file back if anything changed
    if changes:
        if kind == "spec":
            spec = {k: ns[k] for k in ("TITLE", "OUT_BASENAME", "INTRO", "NAV_NOTE", "SECTIONS", "CLOSING", "SOURCE_NOTE")}
            spec["SECTIONS"] = sections
            open(os.path.join(SPECS, f"{ref}_spec.py"), "w", encoding="utf-8").write(dump_spec(spec))
        else:
            path = os.path.join(PROJ, ref)
            t = open(path, encoding="utf-8").read()
            for q, old, new in changes:
                assert t.count(old) == 1, f"{ref}: source {old!r} not unique"
                t = t.replace(old, new)
            open(path, "w", encoding="utf-8").write(t)

    # rejected rows for register
    for tid in sorted(final_rej):
        d = rej_detail.get(tid) or ORIG_DETAIL.get(tid) or {
            "ticket_id": tid, "subject": "", "date": "",
            "category": "Reviewed (not authored into FAQ)",
            "reason": "Reviewed; no FAQ answer was authored for this ticket.", "citation": ""}
        final_rejected_rows.append({"document": name, **{k: d.get(k, "") for k in ("ticket_id", "subject", "date", "category", "reason", "citation")}})

    cited_after = surviving
    funnel.append((name, len(filt), len(filt) - len(final_rej), sum(len(qas) for _, qas in sections), len(final_rej)))
    report.append(f"\n=== {name} ===")
    report.append(f"  agent: used={len(audit['used'])} rejected={len(rej_ids)}")
    report.append(f"  stripped (rejected secondary cites removed from docs): {sorted(stripped & final_rej)}")
    report.append(f"  kept USED to preserve an answer (agent-rejected but sole source): {sorted(kept_used)}")
    anomaly = [t for t in audit['used'] if t not in surviving]
    if anomaly:
        report.append(f"  agent-USED but not cited in any Q&A -> moved to rejected register: {sorted(anomaly)}")
    miss = filt - surviving - final_rej
    if miss:
        report.append(f"  !! unaccounted: {sorted(miss)}")

json.dump(final_rejected_rows, open(os.path.join(AUDIT, "_rejected_final.json"), "w", encoding="utf-8"), indent=2)
open(os.path.join(AUDIT, "_change_report.txt"), "w", encoding="utf-8").write("\n".join(report))

print("FUNNEL (Document | total | used | questions | rejected)")
for n, tot, used, q, rej in funnel:
    print(f"  {n:22} {tot:3} {used:4} {q:4} {rej:4}")
print(f"\nTOTAL rejected rows: {len(final_rejected_rows)}")
print("\n".join(report))
