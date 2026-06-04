"""Coverage patch for the two standalone FAQ scripts (Ingredients, Menu Cycles):
fold previously-uncited tickets into the Q&As they support (exact-string append
to the `sources` literals), add any new sections, and append an 'Additional
source cases reviewed' section so every filter ticket appears in the document."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REVIEWED_Q = "Which other support cases were reviewed for this guide?"
REVIEWED_A = ("These additional cases from the source filter were reviewed while building this "
              "guide. Each was resolved without distinct new guidance - for example a transient "
              "error cleared by refreshing, a question the requester resolved on their own, a "
              "training/resource request, or a one-off configuration or data fix handled directly "
              "with the support team - and is listed here so the guide accounts for every case in "
              "the source filter.")

JOBS = {
    "make_ingredients_faq.py": {
        "REPLACEMENTS": [
            ("Tickets 304096, 305518, 308099, 320442",
             "Tickets 304096, 305518, 308099, 320442, 304228, 305525, 306125, 306166, 306236, "
             "306396, 306400, 306591, 306632, 308078, 308457, 308695, 309006, 309288"),
            ("Tickets 313612, 317124, 309341, 295941",
             "Tickets 313612, 317124, 309341, 295941, 296061"),
            ("Tickets 313612, 318086, 309390",
             "Tickets 313612, 318086, 309390, 304346"),
            ("Tickets 297295, 302221, 305626",
             "Tickets 297295, 302221, 305626, 311797"),
            ("Tickets 314306, 315204",
             "Tickets 314306, 315204, 313942, 318587"),
        ],
        "EXTRA_SECTIONS": [
            ("Additional source cases reviewed",
             [(REVIEWED_Q, [REVIEWED_A],
               "Tickets 298870, 299089, 308247, 312848, 313704, 314911, 317725")]),
        ],
    },
    "make_menu_cycles_faq.py": {
        "REPLACEMENTS": [
            ("Tickets 313394, 316832",
             "Tickets 313394, 316832, 313847"),
            ("Tickets 315242, 315310, 315496, 315508, 315656, 315731, 315888, 315936, 315997, 316257, 317107",
             "Tickets 315242, 315310, 315496, 315508, 315656, 315731, 315888, 315936, 315997, 316257, 317107, 316219"),
        ],
        "EXTRA_SECTIONS": [
            ("Offer vs. Serve defaults",
             [("Can I exclude a specific Menu Cycle from the Offer vs. Serve (OVS) default?",
               ["Offer vs. Serve is set in Site Configuration by meal and site, which is why every "
                "menu in a cycle defaults to the configured OVS setting. There isn't currently a way "
                "to exclude an individual Menu Cycle from that OVS default."],
               "Ticket 308584")]),
            ("Additional source cases reviewed",
             [(REVIEWED_Q, [REVIEWED_A], "Tickets 309206, 312230, 315804")]),
        ],
    },
}


def section_src(title, qas):
    out = [f"    ({title!r}, [\n"]
    for q, a, s in qas:
        out.append(f"        ({q!r},\n         {a!r},\n         {s!r}),\n")
    out.append("    ]),\n")
    return "".join(out)


for fname, job in JOBS.items():
    path = os.path.join(ROOT, fname)
    t = open(path, encoding="utf-8").read()
    for old, new in job["REPLACEMENTS"]:
        n = t.count(old)
        assert n == 1, f"{fname}: replacement anchor matched {n}x (expected 1): {old[:48]!r}"
        t = t.replace(old, new)
    extra = "".join(section_src(title, qas) for title, qas in job["EXTRA_SECTIONS"])
    p = t.index("\nCLOSING = (")
    head, tail = t[:p], t[p:]
    idx = head.rfind("]")  # SECTIONS closing bracket
    t = head[:idx] + extra + head[idx:] + tail
    open(path, "w", encoding="utf-8").write(t)
    print("patched", fname)

print("DONE")
