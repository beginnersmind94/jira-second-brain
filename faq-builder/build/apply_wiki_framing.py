"""One-shot patch: weave wiki product-framing into each FAQ intro and note the
wiki cross-check in each source line. Asserts every anchor matches exactly once."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPECS = os.path.join(HERE, "specs")

SRC_OLD = "ticket numbers are internal references only."
SRC_NEW = ("ticket numbers are internal references only. Product framing was "
           "cross-checked against the jira-brain wiki concepts; all behavioral "
           "guidance traces to the support cases.")

EDITS = {
    os.path.join(SPECS, "assign_menus_spec.py"): [
        ("or was an enhancement request, that is stated plainly.",
         "or was an enhancement request, that is stated plainly. In the bigger picture, "
         "Menu Planning is how districts build menu cycles and serving plans; assigning a "
         "menu is the step that places those plans on the calendar for specific sites, so "
         "production planning, analysis, and SchoolCafe/Family Hub display all follow from it."),
        (SRC_OLD, SRC_NEW),
    ],
    os.path.join(SPECS, "perpetual_inventory_spec.py"): [
        ("who need to understand why the numbers sometimes look wrong.",
         "who need to understand why the numbers sometimes look wrong. More broadly, "
         "perpetual inventory is the running, system-maintained on-hand balance; periodic "
         "physical counts reconcile it against the shelf, and the adjustments that fall out "
         "of that reconciliation roll forward into Financials."),
        (SRC_OLD, SRC_NEW),
    ],
    os.path.join(SPECS, "production_orders_spec.py"): [
        ("and how to fix the most common problems.",
         "and how to fix the most common problems. More broadly, Production is the kitchen's "
         "daily plan of forecasted servings and recipe scaling; the production order is where "
         "those forecasted needs become actual vendor orders, drawing on the vendor and item "
         "structure maintained in Inventory."),
        (SRC_OLD, SRC_NEW),
    ],
    os.path.join(SPECS, "receipt_wo_order_spec.py"): [
        ("want to understand how the function behaves and how to fix common problems.",
         "want to understand how the function behaves and how to fix common problems. Two "
         "product facts from the Inventory module explain much of the behavior below: a "
         "receipt is an accounting object that stays editable until the accounting period "
         "locks, and the central warehouse acts as an internal vendor rather than a "
         "commercial supplier."),
        (SRC_OLD, SRC_NEW),
    ],
    os.path.join(SPECS, "transfer_items_spec.py"): [
        ("want to understand how transfers behave and how to fix common problems.",
         "want to understand how transfers behave and how to fix common problems. More "
         "broadly, a transfer moves on-hand stock out of one site's perpetual inventory and "
         "into another's, and the central warehouse participates as an internal site rather "
         "than an outside vendor."),
        (SRC_OLD, SRC_NEW),
    ],
    os.path.join(ROOT, "make_ingredients_faq.py"): [
        ("and the people who train them.",
         "and the people who train them. In PrimeroEdge an ingredient is the building block a "
         "recipe consumes, and its Buying Guide tab is the bridge to the stock item that "
         "Inventory and ordering use."),
        ("numbers are internal references only.",
         "numbers are internal references only. Product framing was cross-checked against the "
         "jira-brain wiki concepts; all behavioral guidance traces to the support cases."),
    ],
}

for path, pairs in EDITS.items():
    txt = open(path, encoding="utf-8").read()
    for old, new in pairs:
        n = txt.count(old)
        assert n == 1, f"{os.path.basename(path)}: anchor matched {n}x (expected 1): {old[:50]!r}"
        txt = txt.replace(old, new)
    open(path, "w", encoding="utf-8").write(txt)
    print("patched", os.path.basename(path))

print("DONE")
