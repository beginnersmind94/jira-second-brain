"""Finalize the faq-builder reorg:
1. Fix code paths in the moved builder scripts to match the README layout
   (build/specs for specs, deliverables/ for outputs).
2. Remove the 'Additional source cases reviewed' appendix sections (rejected
   tickets now live in the separate Excel register), keeping all substantive Q&As.
Run from anywhere: python faq-builder/build/finalize.py
"""
import os, re, runpy

BUILD = os.path.dirname(os.path.abspath(__file__))      # faq-builder/build
PROJ = os.path.dirname(BUILD)                            # faq-builder
SPECS = os.path.join(BUILD, "specs")
TITLE = "Additional source cases reviewed"


def patch(path, repls):
    t = open(path, encoding="utf-8").read()
    for old, new, n_expected in repls:
        n = t.count(old)
        assert n == n_expected, f"{os.path.basename(path)}: {old[:40]!r} matched {n} (want {n_expected})"
        t = t.replace(old, new)
    open(path, "w", encoding="utf-8").write(t)
    print("path-fixed", os.path.basename(path))


# ---- 1. fix paths ----
patch(os.path.join(PROJ, "make_all_faqs.py"), [
    ('os.path.join(HERE, "faq_build", "specs")', 'os.path.join(HERE, "build", "specs")', 1),
    ('os.path.join(HERE, base + ".docx")', 'os.path.join(HERE, "deliverables", base + ".docx")', 1),
    ('os.path.join(HERE, base + ".pdf")', 'os.path.join(HERE, "deliverables", base + ".pdf")', 1),
])
for fn in ("make_ingredients_faq.py", "make_menu_cycles_faq.py"):
    patch(os.path.join(PROJ, fn), [
        ('os.path.join(HERE, "PrimeroEdge-', 'os.path.join(HERE, "deliverables", "PrimeroEdge-', 2),
    ])


# ---- 2. remove reviewed appendix sections ----
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


for name in ("assign_menus", "perpetual_inventory", "receipt_wo_order"):
    path = os.path.join(SPECS, f"{name}_spec.py")
    ns = runpy.run_path(path)
    spec = {k: ns[k] for k in ("TITLE", "OUT_BASENAME", "INTRO", "NAV_NOTE", "SECTIONS", "CLOSING", "SOURCE_NOTE")}
    n0 = len(spec["SECTIONS"])
    spec["SECTIONS"] = [(s, q) for s, q in spec["SECTIONS"] if s != TITLE]
    if len(spec["SECTIONS"]) != n0:
        open(path, "w", encoding="utf-8").write(dump_spec(spec))
        print("removed reviewed section from", name + "_spec.py")

for fn in ("make_ingredients_faq.py", "make_menu_cycles_faq.py"):
    path = os.path.join(PROJ, fn)
    t = open(path, encoding="utf-8").read()
    new = re.sub(r"    \('Additional source cases reviewed', \[.*?\n    \]\),\n", "", t, count=1, flags=re.S)
    if new != t:
        open(path, "w", encoding="utf-8").write(new)
        print("removed reviewed section from", fn)

print("DONE")
