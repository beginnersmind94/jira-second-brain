"""Step 5: compile concepts, workflows, entities from analyzed corpus."""
import json
import os
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
TICKETS = VAULT / "raw" / "tickets"
WIKI = VAULT / "wiki"
STATE_PATH = VAULT / ".brain-state.json"


def load_state():
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state):
    tmp = STATE_PATH.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_PATH)


def load_frontmatter(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return {}
    fm_text = m.group(1)
    meta = {}
    for line in fm_text.split("\n"):
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    return meta

def parse_list(v):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        parts = re.findall(r'"([^"]*)"', v[1:-1])
        return parts
    return []


def wikilink(key, summary):
    summary = summary.strip('"').replace("[", "(").replace("]", ")")
    return f"[[raw/tickets/{key}|{key} — {summary[:80]}]]"


def ticket_sort_key(t):
    # Newer NXT numbers = higher; bigger first for "recent behavior"
    m = re.match(r"NXT-(\d+)", t["key"])
    return -(int(m.group(1)) if m else 0)


def write_if_absent(path, content):
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(content)
    os.replace(tmp, path)
    return True


def load_all():
    """Load frontmatter for every ticket."""
    rows = []
    for p in TICKETS.glob("*.md"):
        meta = load_frontmatter(p)
        if not meta:
            continue
        rows.append({
            "key": meta.get("key", p.stem),
            "summary": meta.get("summary", "").strip('"'),
            "status": meta.get("status", "").strip('"'),
            "resolution": meta.get("resolution", "").strip('"'),
            "components": parse_list(meta.get("components", "[]")),
            "sprints": parse_list(meta.get("sprints", "[]")),
            "low_signal": meta.get("low_signal", "false") == "true",
        })
    return rows


def pick_examples(tickets, n=8):
    hi = [t for t in tickets if not t["low_signal"] and "Done" in t["status"]]
    hi.sort(key=ticket_sort_key)
    if len(hi) < n:
        # fallback include non-done
        rest = [t for t in tickets if t not in hi and not t["low_signal"]]
        rest.sort(key=ticket_sort_key)
        hi = hi + rest
    return hi[:n]


# ---------------- CONCEPTS (by component) ---------------- #

CONCEPT_BLURBS = {
    "Item Management": (
        "Item Management is the catalog of every purchasable and preparable item — foods, ingredients, "
        "recipes, and non-food goods — used across Inventory, Menu Planning, and Production. "
        "Pack sizes, units, nutrition facts, and allergens all live here."
    ),
    "Inventory": (
        "Inventory tracks physical stock at every site: orders from vendors, transfers between sites, "
        "physical counts, receipts, and reports. It feeds Production and reconciles against purchases."
    ),
    "Menu Planning": (
        "Menu Planning is how districts build menu cycles and serving plans that comply with USDA meal "
        "pattern requirements. Menus reference items, categories, and serving groups; changes are "
        "versioned and analyzed for nutrition."
    ),
    "Accountability": (
        "Accountability covers meal counting, reimbursable claims, and day-of-service transactions at "
        "the point of sale — the audit trail that the district uses to claim federal reimbursement."
    ),
    "Eligibility": (
        "Eligibility determines each student's meal benefit (free / reduced / paid) via household "
        "applications, direct certification matches, and state imports. It drives every POS transaction."
    ),
    "Production": (
        "Production is the kitchen's daily plan: forecasted servings, recipe scaling, production records, "
        "leftovers, and post-production analysis that feeds back into forecasts."
    ),
    "Insights": (
        "Insights is the reporting and KPI layer — dashboards, custom reports, and the DataQuery "
        "framework that lets users slice production, sales, claims, and inventory data."
    ),
    "PE Insights": (
        "PE Insights is the PrimeroEdge-classic reporting surface — a separate analytics layer from the "
        "modern Insights module, still maintained for customers on the classic product."
    ),
    "Platform - Data Exchange": (
        "Data Exchange is the integration layer that moves data in and out of the system: SIS student "
        "imports, direct-certification files, payroll exports, GL exports, and vendor catalog feeds."
    ),
    "Platform - System": (
        "Platform – System is the cross-module foundation: user accounts, roles and permissions, site "
        "and district setup, session/auth, and the shared UI chrome that every feature sits on."
    ),
    "Platform - Framework": (
        "Platform – Framework is the developer-facing scaffolding: shared UI components, reusable page "
        "templates, the DataQuery framework, and cross-cutting engineering work that isn't tied to one "
        "business module."
    ),
    "Platform": (
        "Platform is the generic/legacy bucket for cross-module platform work that predates the more "
        "specific Platform – System / Data Exchange / Framework splits."
    ),
    "System": (
        "System is a legacy component predating the Platform – System split. Modern tickets in this area "
        "are usually re-tagged; treat this page as historical context."
    ),
    "Account Management": (
        "Account Management is student and family financial accounts: balances, payments, refunds, "
        "low-balance alerts, and the Family Hub parent experience."
    ),
    "Inspections": (
        "Inspections captures food-safety and operational audits at each site — temperature logs, "
        "sanitation checks, corrective actions, and the reports that prove compliance."
    ),
    "Global Catalog": (
        "Global Catalog is the shared master item database that districts draw from when onboarding "
        "new items, including pack sizes, USDA nutrition, and vendor linkages."
    ),
    "Financials": (
        "Financials is the GL mapping, postings, trial balance, and export layer that turns operational "
        "events (sales, purchases, transfers) into accounting entries for the district's ERP."
    ),
    "Face/Food Detection": (
        "Face / Food Detection is the computer-vision workflow at POS and production lines — identifying "
        "students and served items via camera to speed service and reduce manual entry."
    ),
    "Mobile App": (
        "Mobile App is the native/mobile surface (parent, student, and staff views) that complements "
        "the web product."
    ),
    "Professional Standards": (
        "Professional Standards tracks staff training hours and continuing-education credits required "
        "by USDA for school nutrition employees."
    ),
    "Family Hub": (
        "Family Hub is the parent-facing portal — account balances, payments, meal applications, and "
        "notifications for their students."
    ),
    "SCTV": (
        "SCTV (School Cafe TV) is the digital-menu-board surface — in-cafeteria screens driven by the "
        "district's published menus."
    ),
    "Platform - Security": (
        "Platform – Security covers auth, data protection, and vulnerability remediation across the "
        "system."
    ),
    "UI Components": (
        "UI Components is the design-system library — reusable inputs, grids, and layout primitives "
        "consumed by every module."
    ),
    "Data - Migration": (
        "Data – Migration is tooling for moving customer data between versions of the product, "
        "especially PrimeroEdge Classic → NXT."
    ),
}

def write_concept_page(component, tickets):
    slug = re.sub(r"[^A-Za-z0-9]+", "-", component).strip("-")
    path = WIKI / "concepts" / f"{slug}.md"
    examples = pick_examples(tickets, n=8)
    blurb = CONCEPT_BLURBS.get(component, "")
    lines = [
        "---",
        f'title: "{component}"',
        "type: concept",
        f"source_component: \"{component}\"",
        f"ticket_count: {len(tickets)}",
        "---",
        "",
        f"# {component}",
        "",
    ]
    if blurb:
        lines += ["## What it is", "", blurb, ""]
    else:
        lines += ["## What it is", "", f"_{component}_ is a recurring module in the Perseus/NXT product. "
                  f"{len(tickets)} tickets have been filed against it.", ""]
    lines += [
        "## How it shows up in the product",
        "",
        f"Tickets tagged `{component}` span feature work, bugs, refinements, and platform integration. "
        f"The examples below are the most recent Done tickets that shaped current behavior.",
        "",
        "## Representative tickets",
        "",
    ]
    for t in examples:
        lines.append(f"- {wikilink(t['key'], t['summary'])}")
    lines += [
        "",
        "## Sprints where this work landed",
        "",
    ]
    # sprints across these tickets
    sp = defaultdict(int)
    for t in tickets:
        for s in t["sprints"]:
            sp[s] += 1
    top_sp = sorted(sp.items(), key=lambda kv: -kv[1])[:10]
    for s, c in top_sp:
        lines.append(f"- **{s}** — {c} ticket(s)")
    lines += [
        "",
        "## Open questions / edge cases",
        "",
        "- _Fill in as SMEs review._",
        "",
    ]
    if write_if_absent(path, "\n".join(lines)):
        return path
    return None


# ---------------- WORKFLOWS (phrase clusters) ---------------- #

WORKFLOWS = [
    {
        "slug": "physical-inventory",
        "title": "Physical Inventory Count",
        "match": [r"\bphysical inventory\b", r"\binv physical\b"],
        "blurb": (
            "Running a physical inventory is how a site reconciles its on-hand stock against what the "
            "system expects. The workflow runs through Inventory → Physical Inventory, freezes counts "
            "by location, captures variance, and posts adjustments that flow into Financials."
        ),
    },
    {
        "slug": "orders-purchasing",
        "title": "Create & Receive Orders",
        "match": [r"\binv orders\b", r"\binv vendors\b", r"\binv create orders\b", r"\border detail\b"],
        "blurb": (
            "Orders are placed against vendors, received on delivery, and reconciled to invoices. The "
            "flow covers creating the PO, editing lines, receiving partial shipments, and posting the "
            "receipt into inventory value."
        ),
    },
    {
        "slug": "menu-cycle-build",
        "title": "Build & Publish a Menu Cycle",
        "match": [r"\bmenu cycle\b", r"\bmp- menu\b", r"\bmenu planner-\b", r"\bmenus edit menu\b"],
        "blurb": (
            "Menu Planning cycles group menus by week/period and by serving group. Staff build cycles, "
            "attach menu items, run nutrition and compliance analysis, and publish cycles so sites can "
            "produce against them."
        ),
    },
    {
        "slug": "student-import-sis-sync",
        "title": "Student Import & SIS Auto-Sync",
        "match": [r"\bstudent import\b", r"\bsis auto sync\b", r"\bsis import\b"],
        "blurb": (
            "Districts push student rosters into the product either on a schedule (SIS Auto-Sync) or "
            "ad-hoc via Data Exchange file imports. Matches drive Eligibility, Accountability, and "
            "Family Hub account creation."
        ),
    },
    {
        "slug": "direct-certification",
        "title": "Direct Certification Matching",
        "match": [r"\bdirect certification\b"],
        "blurb": (
            "Direct Certification (DC) automatically qualifies students for free meals based on SNAP/TANF/"
            "foster/Medicaid matches from the state file. The workflow ingests the state DC file, "
            "fuzzy-matches against enrolled students, and applies free-meal eligibility with an audit trail."
        ),
    },
    {
        "slug": "post-production-analysis",
        "title": "Post-Production Analysis & Leftovers",
        "match": [r"\bpost production\b", r"\bproduction analysis-\b"],
        "blurb": (
            "After service, sites record what was actually served vs forecasted, log leftovers, and "
            "feed that data back so future forecasts tighten. This drives both the Production record "
            "and Insights reports."
        ),
    },
    {
        "slug": "data-exchange-file-import",
        "title": "Data Exchange File Import/Export",
        "match": [r"\bdata exchange\b", r"\bexchange file import\b", r"\bexchange sis import\b"],
        "blurb": (
            "Data Exchange is the generic file-based integration pattern: upload a file, map columns, "
            "validate, and commit. Used for students, eligibility, vendor catalogs, payroll, and more."
        ),
    },
    {
        "slug": "item-onboarding-pack-size",
        "title": "Item Onboarding & Pack-Size Changes",
        "match": [r"\bitem onboarding\b", r"\bpack size\b", r"\bbulk item\b", r"\bitems create item\b"],
        "blurb": (
            "Onboarding an item into Item Management captures its unit, pack size, allergens, and "
            "nutrition facts. Pack-size changes mid-year require careful handling so existing "
            "inventory, orders, and recipes don't lose value."
        ),
    },
]

def match_tickets(all_tickets, patterns):
    regs = [re.compile(p, re.IGNORECASE) for p in patterns]
    out = []
    for t in all_tickets:
        s = t["summary"]
        if any(r.search(s) for r in regs):
            out.append(t)
    return out

def write_workflow_page(wf, all_tickets):
    matched = match_tickets(all_tickets, wf["match"])
    examples = pick_examples(matched, n=8)
    if not examples:
        return None
    path = WIKI / "workflows" / f"{wf['slug']}.md"
    lines = [
        "---",
        f'title: "{wf["title"]}"',
        "type: workflow",
        f'ticket_count: {len(matched)}',
        "---",
        "",
        f"# {wf['title']}",
        "",
        "## Overview",
        "",
        wf["blurb"],
        "",
        "## Example tickets that shaped this flow",
        "",
    ]
    for t in examples:
        lines.append(f"- {wikilink(t['key'], t['summary'])}")
    lines += [
        "",
        "## Components involved",
        "",
    ]
    comp = defaultdict(int)
    for t in matched:
        for c in t["components"]:
            comp[c] += 1
    for c, n in sorted(comp.items(), key=lambda kv: -kv[1])[:8]:
        lines.append(f"- `{c}` — {n} ticket(s)")
    lines += [
        "",
        "## Open questions",
        "",
        "- _Fill in as SMEs review._",
        "",
    ]
    if write_if_absent(path, "\n".join(lines)):
        return path
    return None


# ---------------- ENTITIES (modules/teams) ---------------- #

ENTITY_GROUPS = {
    "platform-team": {
        "title": "Platform Team",
        "blurb": ("Platform Team owns cross-cutting engineering: auth, data exchange, the shared UI "
                  "framework, and all non-module infrastructure."),
        "components": ["Platform - System", "Platform - Data Exchange", "Platform - Framework",
                       "Platform", "System", "Platform - Security", "UI Components",
                       "Data - Migration", "Data Engineering", "Devops", "Automation"],
    },
    "nutrition-operations": {
        "title": "Nutrition Operations Modules",
        "blurb": ("The operational modules a district's nutrition staff use every day: Menu Planning, "
                  "Production, Inventory, Item Management, Inspections."),
        "components": ["Menu Planning", "Production", "Inventory", "Item Management",
                       "Inspections", "Global Catalog"],
    },
    "meal-service-accountability": {
        "title": "Meal Service & Accountability",
        "blurb": ("Everything downstream of serving a meal: Accountability (POS, claims), Eligibility "
                  "(free/reduced), Account Management (student wallets), Family Hub (parents)."),
        "components": ["Accountability", "Eligibility", "Account Management", "Family Hub",
                       "Professional Standards"],
    },
    "reporting-insights": {
        "title": "Reporting & Insights",
        "blurb": "Analytics surfaces: Insights (modern), PE Insights (classic), SCTV, Financials exports.",
        "components": ["Insights", "PE Insights", "SCTV", "Financials"],
    },
    "emerging-surfaces": {
        "title": "Emerging Surfaces",
        "blurb": "Newer or specialized product surfaces: Mobile App, Face/Food Detection.",
        "components": ["Mobile App", "Face/Food Detection"],
    },
}

def write_entity_page(slug, group, by_component, existing_concepts):
    path = WIKI / "entities" / f"{slug}.md"
    lines = [
        "---",
        f'title: "{group["title"]}"',
        "type: entity",
        "---",
        "",
        f"# {group['title']}",
        "",
        group["blurb"],
        "",
        "## Components in this group",
        "",
    ]
    total = 0
    for c in group["components"]:
        n = len(by_component.get(c, []))
        total += n
        slug_c = re.sub(r"[^A-Za-z0-9]+", "-", c).strip("-")
        if c in existing_concepts:
            lines.append(f"- [[concepts/{slug_c}|{c}]] — {n} ticket(s)")
        elif n > 0:
            lines.append(f"- {c} — {n} ticket(s) _(no dedicated concept page; too few tickets)_")
        else:
            lines.append(f"- {c} — 0 ticket(s)")
    lines += ["", f"_Total tickets across this group: {total}_", ""]
    # Sample tickets
    sample = []
    for c in group["components"]:
        sample.extend(by_component.get(c, [])[:2])
    sample = pick_examples(sample, n=6)
    if sample:
        lines += ["## Representative tickets", ""]
        for t in sample:
            lines.append(f"- {wikilink(t['key'], t['summary'])}")
        lines.append("")
    if write_if_absent(path, "\n".join(lines)):
        return path
    return None


# ---------------- INDEX + LOG ---------------- #

def write_index(concepts, workflows, entities):
    path = WIKI / "index.md"
    lines = [
        "# Perseus/NXT Second-Brain Index",
        "",
        "This wiki compiles institutional knowledge from Jira tickets (`raw/tickets/`).",
        "Every page links back to the tickets that shaped it.",
        "",
        "## Concepts (modules)",
        "",
    ]
    for slug, title in concepts:
        lines.append(f"- [[concepts/{slug}|{title}]]")
    lines += ["", "## Workflows", ""]
    for slug, title in workflows:
        lines.append(f"- [[workflows/{slug}|{title}]]")
    lines += ["", "## Entities (teams / module groups)", ""]
    for slug, title in entities:
        lines.append(f"- [[entities/{slug}|{title}]]")
    lines += ["", "## Sections not yet populated", "",
              "- `decisions/` — to be written from explicit architecture/product tickets",
              "- `onboarding/` — derived; write after SME review",
              "- `training/` — write on demand",
              ""]
    # overwrite index even if exists (it's an index)
    tmp = path.with_suffix(".md.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    os.replace(tmp, path)


def append_log(tickets_analyzed, concepts_written, workflows_written, entities_written):
    path = WIKI / "log.md"
    today = str(date.today())
    entry = [
        f"## {today} — First compilation pass",
        "",
        f"- Tickets analyzed: {tickets_analyzed}",
        f"- Concept pages written: {concepts_written}",
        f"- Workflow pages written: {workflows_written}",
        f"- Entity pages written: {entities_written}",
        "",
    ]
    prior = path.read_text(encoding="utf-8") if path.exists() else ""
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(entry) + prior)


# ---------------- MAIN ---------------- #

def main():
    state = load_state()
    step = state["steps"]["5"]
    if step["status"] == "done":
        print("Step 5 already done.")
        return
    step["status"] = "in_progress"
    save_state(state)

    tickets = load_all()
    high = [t for t in tickets if not t["low_signal"]]
    by_component = defaultdict(list)
    for t in high:
        for c in t["components"]:
            by_component[c].append(t)

    # Build concepts for components with >=25 tickets (keep the set focused)
    TOP_COMPONENTS = [c for c, _ in sorted(by_component.items(), key=lambda kv: -len(kv[1])) if len(by_component[c]) >= 25][:25]
    existing_concepts = set(TOP_COMPONENTS)

    concepts_written = 0
    concepts_index = []
    for c in TOP_COMPONENTS:
        slug = re.sub(r"[^A-Za-z0-9]+", "-", c).strip("-")
        if write_concept_page(c, by_component[c]):
            concepts_written += 1
        concepts_index.append((slug, c))
        step["concepts_written"] = concepts_written
        save_state(state)

    workflows_written = 0
    workflows_index = []
    for wf in WORKFLOWS:
        if write_workflow_page(wf, high):
            workflows_written += 1
        workflows_index.append((wf["slug"], wf["title"]))
        step["workflows_written"] = workflows_written
        save_state(state)

    entities_written = 0
    entities_index = []
    for slug, grp in ENTITY_GROUPS.items():
        if write_entity_page(slug, grp, by_component, existing_concepts):
            entities_written += 1
        entities_index.append((slug, grp["title"]))
        step["entities_written"] = entities_written
        save_state(state)

    write_index(concepts_index, workflows_index, entities_index)
    append_log(len(high), concepts_written, workflows_written, entities_written)

    step["tickets_analyzed"] = [t["key"] for t in high]
    step["status"] = "done"
    step["completed_at"] = str(date.today())
    state["current_step"] = 5
    save_state(state)

    print(f"DONE: concepts={concepts_written} workflows={workflows_written} entities={entities_written}")

if __name__ == "__main__":
    main()
