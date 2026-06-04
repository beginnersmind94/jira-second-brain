"""
Assemble every function FAQ from its content spec (faq_build/specs/*_spec.py)
into a formatted .docx + .pdf via the shared faq_builder.

Each spec module defines: TITLE, OUT_BASENAME, INTRO, NAV_NOTE, SECTIONS,
CLOSING, SOURCE_NOTE. Content is grounded in the Freshdesk support
conversations; breadcrumbs/labels come from the PrimeroEdge quick-step guides.
"""
import os
import glob
import runpy
import sys

import faq_builder

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC_DIR = os.path.join(HERE, "faq_build", "specs")

REQUIRED = ["TITLE", "OUT_BASENAME", "INTRO", "NAV_NOTE", "SECTIONS", "CLOSING", "SOURCE_NOTE"]


def load_spec(path):
    ns = runpy.run_path(path)
    missing = [k for k in REQUIRED if k not in ns]
    if missing:
        raise KeyError(f"{os.path.basename(path)} missing keys: {missing}")
    base = ns["OUT_BASENAME"]
    return {
        "title": ns["TITLE"],
        "intro": ns["INTRO"],
        "nav_note": ns["NAV_NOTE"],
        "sections": ns["SECTIONS"],
        "closing": ns["CLOSING"],
        "source_note": ns["SOURCE_NOTE"],
        "docx_path": os.path.join(HERE, base + ".docx"),
        "pdf_path": os.path.join(HERE, base + ".pdf"),
    }


def main():
    only = set(sys.argv[1:])  # optional: spec basenames to limit to
    specs = sorted(glob.glob(os.path.join(SPEC_DIR, "*_spec.py")))
    results = []
    for path in specs:
        name = os.path.basename(path)
        if only and name not in only and name.replace("_spec.py", "") not in only:
            continue
        spec = load_spec(path)
        n_qa = sum(len(qas) for _, qas in spec["sections"])
        print(f"\n=== {spec['title']} ({len(spec['sections'])} sections, {n_qa} Q&As) ===")
        ok = faq_builder.build(spec, make_pdf=True)
        results.append((spec["title"], ok, spec["docx_path"], spec["pdf_path"]))

    print("\n==== SUMMARY ====")
    for title, ok, docx, pdf in results:
        print(f"{'OK ' if ok else 'DOCX-ONLY'} | {title}")
        print(f"     {docx}")
        print(f"     {pdf if ok else '(pdf not generated)'}")


if __name__ == "__main__":
    main()
