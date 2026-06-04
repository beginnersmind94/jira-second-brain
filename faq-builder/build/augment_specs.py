"""Augment FAQ specs for full source coverage: fold previously-uncited tickets
into the Q&As they support, add new Q&As where there was genuinely new content,
and add an 'Additional source cases reviewed' entry for the rest. Re-serializes
each spec file deterministically.

Run with function names as args, e.g.:
    python faq_build/augment_specs.py transfer_items perpetual_inventory receipt_wo_order production_orders
"""
import os, runpy, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPECS = os.path.join(HERE, "specs")

REVIEWED_Q = "Which other support cases were reviewed for this guide?"
REVIEWED_A = ("These additional cases from the source filter were reviewed while building this "
              "guide. Each was resolved without distinct new guidance - for example a transient "
              "error cleared by refreshing, a question the requester resolved on their own, or a "
              "one-off configuration or data fix handled directly with the support team - and is "
              "listed here so the guide accounts for every case in the source filter.")

# Per-function reconciliation. APPEND keys are the EXACT existing `sources` strings.
CONFIG = {
    "transfer_items": {
        "APPEND": {"Tickets 306477, 318299": "311921"},
        "NEW": [],
        "REVIEWED": "",
    },
    "perpetual_inventory": {
        "APPEND": {"Tickets 302110": "302410"},
        "NEW": [],
        "REVIEWED": "290408 313652",
    },
    "receipt_wo_order": {
        "APPEND": {
            "Tickets 306626, 306728, 306725": "292991",
            "Tickets 306493, 312635": "311601",
        },
        "NEW": [
            ("Getting started",
             "Is there a Find and Replace in Inventory to swap one item for another (for example strawberries for peaches) across all sites?",
             ["No - there is no Find and Replace in the Inventory module. To swap one item for another, withdraw the old item and add the new item to inventory, or use a Receipt w/o Order if the new item is arriving separately from your regular orders."],
             "Tickets 304591"),
            ("Getting started",
             "We just started in PrimeroEdge and are only doing receipts w/o order - what is the monthly warehouse / commodity process?",
             ["A common end-to-end pattern for warehouse and commodity items is: use Receipt w/o Order for the items you pick up (for example commodity items from the state), enter Transfers to the sites for the week they are sent out, then run your monthly Physical Inventory. Before you close and reconcile the physical inventory, verify the on-hand looks right. A separate training site is available if you want to practice the steps without affecting your live data."],
             "Tickets 314508"),
        ],
        "REVIEWED": "305425 307466",
    },
    "production_orders": {
        "APPEND": {
            "Tickets 300306, 308645": "308767",
            "Tickets 319642, 303473": "302342",
            "Tickets 292372, 295097, 308645, 310056": "300957 304956",
            "Tickets 290901, 292475, 313846, 290811": "294421 298149 302528",
            "Tickets 313846, 292475": "306740",
        },
        "NEW": [],
        "REVIEWED": "",
    },
}


def dump_spec(ns):
    out = []
    for key in ("TITLE", "OUT_BASENAME", "INTRO", "NAV_NOTE"):
        out.append(f"{key} = {ns[key]!r}\n")
    out.append("SECTIONS = [\n")
    for sec, qas in ns["SECTIONS"]:
        out.append(f"    ({sec!r}, [\n")
        for q, a, src in qas:
            out.append(f"        ({q!r},\n")
            out.append(f"         {a!r},\n")
            out.append(f"         {src!r}),\n")
        out.append("    ]),\n")
    out.append("]\n")
    out.append(f"CLOSING = {ns['CLOSING']!r}\n")
    out.append(f"SOURCE_NOTE = {ns['SOURCE_NOTE']!r}\n")
    return "".join(out)


def augment(name, cfg):
    path = os.path.join(SPECS, f"{name}_spec.py")
    ns = runpy.run_path(path)
    spec = {k: ns[k] for k in ("TITLE", "OUT_BASENAME", "INTRO", "NAV_NOTE", "SECTIONS", "CLOSING", "SOURCE_NOTE")}
    sections = [(sec, list(qas)) for sec, qas in spec["SECTIONS"]]

    # 1) APPEND folded IDs into matching Q&As
    append = dict(cfg.get("APPEND", {}))
    applied = set()
    for sec, qas in sections:
        for i, (q, a, src) in enumerate(qas):
            if src in append:
                add = append[src].split()
                qas[i] = (q, a, src + ", " + ", ".join(add))
                applied.add(src)
    missing_keys = set(append) - applied
    assert not missing_keys, f"{name}: APPEND keys not found: {missing_keys}"

    # 2) NEW Q&As appended to named sections
    sec_index = {sec: i for i, (sec, _) in enumerate(sections)}
    for sec_title, q, a, src in cfg.get("NEW", []):
        assert sec_title in sec_index, f"{name}: NEW section not found: {sec_title!r}"
        sections[sec_index[sec_title]][1].append((q, a, src))

    # 3) REVIEWED appendix
    rev = cfg.get("REVIEWED", "").split()
    if rev:
        sections.append(("Additional source cases reviewed",
                         [(REVIEWED_Q, [REVIEWED_A], "Tickets " + ", ".join(rev))]))

    spec["SECTIONS"] = sections
    open(path, "w", encoding="utf-8").write(dump_spec(spec))
    nqa = sum(len(qas) for _, qas in sections)
    print(f"augmented {name}: sections={len(sections)} Q&As={nqa}")


def load_cfg(name):
    if name in CONFIG:
        return CONFIG[name]
    rec = os.path.join(SPECS, f"{name}_reconcile.py")
    if os.path.exists(rec):
        ns = runpy.run_path(rec)
        return {"APPEND": ns.get("APPEND", {}), "NEW": ns.get("NEW", []),
                "REVIEWED": ns.get("REVIEWED", "")}
    raise KeyError(f"no config or reconcile file for {name}")


if __name__ == "__main__":
    names = sys.argv[1:] or list(CONFIG)
    for n in names:
        augment(n, load_cfg(n))
    print("DONE")
