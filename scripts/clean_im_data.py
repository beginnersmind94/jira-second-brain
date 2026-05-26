"""IM Data Cleaning pipeline (v1).

Implements steps 0-8 from im_data_cleaning_instructions.md, plus the v0.7→v1 patches:
  Patch 1 — privacy hardening (split public/private outdirs; deterministic district
            hash labels; tightened NER heuristic; PII audit; loud --no-ner)
  Patch 2 — structured district + Freshdesk extraction
  Patch 3 — two text blobs (customer-problem vs. full-evidence)
  Patch 4 — configurable reference date + status mapping validation report
  Patch 5 — polish (deleted strikethrough regex, fail-loud thresholds, validation report)

Usage:
  python clean_im_data.py
      --input <raw.csv>
      --outdir-public <dir>
      [--outdir-private <dir>]
      [--reference-date YYYY-MM-DD]
      [--no-ner]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

DROP_TYPES = {"QA - Sub-Task"}
ANALYTIC_TYPES = {"Bug", "Story", "Enhancement", "Tech-Debt", "Improvement", "Task"}

STATUS_CLEAN_MAP = {
    "Done Done": "done",
    "Closed": "done",
    "Fixed": "done",
    "Deployed to QA": "done",
    "Ready For Merge": "done",
    "Release Merge": "done",
    "Rejected": "rejected",
    "Duplicate": "duplicate",
    "In Progress": "in_progress",
    "Story Refinement/Efforting": "in_progress",
    "UX in Progress": "in_progress",
    "Ready for Development": "in_progress",
    "Ready for UX": "in_progress",
    "On Hold": "in_progress",
    "New": "open",
    "Test Case Creation": "in_progress",
    "Release Testing": "in_progress",
    "Under Review by QA": "in_progress",
    "UAT Review": "in_progress",
}
SUSPECT_STATUSES = {"Deployed to QA", "Ready For Merge", "Release Merge", "Fixed"}


# ---------------------------------------------------------------------------
# Patch 1.5 — district patterns (re.I on all four; tightened prefix bounds)
# Patch 1.2 — deterministic hash labels via DistrictMapper
# Patch 2.1 — DistrictMapper records (issue_key, label, source_field) hits
# ---------------------------------------------------------------------------

DISTRICT_PATTERNS = [
    re.compile(r"\b([A-Z][\w\.\-&']*(?:\s+[A-Z\d][\w\.\-&']*){0,3})\s+(SD|ISD|USD|CSD|CUSD)\b", re.I),
    re.compile(r"\b([A-Z][\w\.\-&']*(?:\s+[A-Z\d][\w\.\-&']*){0,2})\s+School\s+District\b", re.I),
    re.compile(r"\b([A-Z][\w\.\-&']*(?:\s+[A-Z\d][\w\.\-&']*){0,2})\s+Public\s+Schools\b", re.I),
    re.compile(
        r"\b([A-Z][\w\.\-&']*(?:\s+[A-Z\d][\w\.\-&']*){0,2})\s+(Unified|Consolidated|Independent)\s+School\s+District\b",
        re.I,
    ),
]
DISTRICT_STOP_TOKENS = {
    "sc", "implementation", "implementations", "issue", "issues", "training",
    "rd", "r&d", "customer", "request", "regression", "support", "ticket",
    "production", "prod", "qa", "uat", "test", "testing", "demo", "feedback",
    "for", "from", "and", "the", "of", "at", "to", "by", "via", "re", "fwd", "fyi",
}
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+?1[\s.\-]?)?\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}")
FRESHDESK_URL_RE = re.compile(
    r"https?://primeroedge\.freshdesk\.com/a/tickets/(\d+)", re.IGNORECASE,
)


class DistrictMapper:
    """Deterministic hash-based district -> label mapping.

    Patch 1.2: stable across runs because the label is derived from a hash of the
    normalized name, not encounter order.
    Patch 2.1: records per-issue, per-field hits for downstream rediscovery.
    """

    def __init__(self) -> None:
        self._key_to_label: dict[str, str] = {}
        self._label_to_example: dict[str, str] = {}
        # issue_key -> list of (label, source_field)
        self.hits: dict[str, list[tuple[str, str]]] = defaultdict(list)

    @staticmethod
    def _normalize_key(raw: str) -> str:
        cleaned = re.sub(r"[^\w\s&-]", " ", raw)
        cleaned = re.sub(r"\s+", " ", cleaned).strip().lower()
        tokens = cleaned.split()
        while tokens and re.sub(r"[^a-z0-9&]", "", tokens[0]) in DISTRICT_STOP_TOKENS:
            tokens.pop(0)
        return " ".join(tokens) if tokens else cleaned

    def label_for(self, raw: str, issue_key: str | None = None, field: str | None = None) -> str:
        key = self._normalize_key(raw)
        label = self._key_to_label.get(key)
        if label is None:
            h = hashlib.sha1(key.encode("utf-8")).hexdigest()[:6].upper()
            label = f"District_{h}"
            self._key_to_label[key] = label
            self._label_to_example[label] = raw.strip()
        if issue_key:
            self.hits[issue_key].append((label, field or ""))
        return label

    def to_json(self) -> dict:
        return {
            "label_to_original_example": self._label_to_example,
            "normalized_key_to_label": self._key_to_label,
        }


def redact_districts(text: str, mapper: DistrictMapper, issue_key: str | None, field: str | None) -> str:
    if not text:
        return text
    out = text
    for pat in DISTRICT_PATTERNS:
        def _sub(m: re.Match) -> str:
            return mapper.label_for(m.group(0), issue_key=issue_key, field=field)
        out = pat.sub(_sub, out)
    return out


def redact_simple(text, mapper: DistrictMapper, issue_key: str | None = None, field: str | None = None) -> str:
    """Cheap regex redactions: districts, email, phone."""
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return text
    if not isinstance(text, str):
        text = str(text)
    text = redact_districts(text, mapper, issue_key, field)
    text = EMAIL_RE.sub("[email]", text)
    text = PHONE_RE.sub("[phone]", text)
    return text


# ---------------------------------------------------------------------------
# Patch 1.3 + 1.4 — NER allowlist (exact-match-only) + tight PERSON heuristic
# ---------------------------------------------------------------------------

DOMAIN_STOPLIST = {
    "Item", "Items", "Pack", "Packs", "Inventory", "User", "Users",
    "Workspace", "Report", "Reports", "Database", "Databases", "API", "APIs",
    "Multiple", "Single", "Module", "Modules", "Master", "Detail", "List",
    "Page", "Setup", "Config", "Vendor", "Vendors", "Recipe", "Recipes",
    "Menu", "Menus", "Allergen", "Allergens", "Nutrition", "Category",
    "Categories", "Ingredient", "Ingredients", "Customer", "Customers",
    "Description", "Summary", "Status", "Resolution", "Comment", "Comments",
    "Attachment", "Attachments", "Field", "Fields", "Column", "Columns",
    "Dashboard", "Build", "Release", "Sprint", "Bug", "Story", "Task",
    "Epic", "Feature", "Production", "Order", "Orders", "Receiving",
    "Distribution", "Counts", "Form", "Forms", "Document", "Documents",
    "Login", "Logout", "Logo", "Image", "Title", "Header", "Footer",
    "Section", "Subsection", "Row", "Rows", "Cell", "Cells", "Edit", "Add",
    "Delete", "Save", "Submit", "Cancel", "Update", "Create", "Read",
    "Replica", "View", "Views", "Version", "Versions", "Tab", "Tabs",
    "Tool", "Tools", "Group", "Groups", "Role", "Roles", "Site", "Sites",
    "Date", "Time", "Day", "Year", "Month", "Week", "Server", "Servers",
    "Client", "Clients", "Platform", "Platforms", "Region", "Regions",
    "Notification", "Notifications", "Alert", "Alerts", "Issue", "Project",
    "Workflow", "Workflows", "Search", "Filter", "Filters", "Sort",
    "Total", "Sum", "Average", "Mean", "Min", "Max", "Count", "Number",
    "Code", "Type", "Name", "ID", "Id",
}


def looks_like_person(span_text: str) -> bool:
    """Patch 1.4: gate before redacting any PERSON span."""
    tokens = span_text.split()
    if len(tokens) < 2:
        return False
    if any(t in DOMAIN_STOPLIST for t in tokens):
        return False
    for t in tokens:
        if not t[:1].isupper():
            return False
        # Allow apostrophes and hyphens inside tokens; otherwise must be alpha
        stripped = t.replace("'", "").replace("-", "").replace("'", "")
        if not stripped or not stripped.isalpha():
            return False
        if any(ch.isdigit() for ch in t):
            return False
    return True


def redact_persons_batch(texts: list[str], internal_staff: set[str], nlp) -> list[str]:
    out: list[str] = []
    staff_full = {s for s in internal_staff}  # exact-match only (Patch 1.3)
    for doc in nlp.pipe(texts, batch_size=64,
                        disable=["parser", "lemmatizer", "tagger", "attribute_ruler"]):
        text = doc.text
        spans = []
        for ent in doc.ents:
            if ent.label_ != "PERSON":
                continue
            ent_text = ent.text.strip()
            if ent_text in staff_full:
                continue
            if not looks_like_person(ent_text):
                continue
            spans.append((ent.start_char, ent.end_char))
        if not spans:
            out.append(text)
            continue
        spans.sort(reverse=True)
        buf = text
        for s, e in spans:
            buf = buf[:s] + "[person]" + buf[e:]
        out.append(buf)
    return out


# ---------------------------------------------------------------------------
# Step 1 — column collapse helpers
# ---------------------------------------------------------------------------


def family_columns(df: pd.DataFrame, base: str) -> list[str]:
    cols = []
    for c in df.columns:
        if c == base or c.startswith(base + "."):
            cols.append(c)
    return cols


def collect_list(row: pd.Series, cols: list[str]) -> list[str]:
    out: list[str] = []
    for c in cols:
        v = row.get(c)
        if v is None:
            continue
        if isinstance(v, float) and pd.isna(v):
            continue
        s = str(v).strip()
        if s:
            out.append(s)
    return out


def build_internal_staff_set(df: pd.DataFrame) -> set[str]:
    staff = set()
    for col in ("Reporter", "Assignee", "Creator"):
        if col in df.columns:
            for val in df[col].dropna().astype(str).unique():
                v = val.strip()
                if v and v.lower() not in {"automation for jira"}:
                    staff.add(v)
    return staff


# ---------------------------------------------------------------------------
# Step 4 — Markup cleanup (Patch 5.1: strikethrough regex deleted)
# ---------------------------------------------------------------------------

H_RE = re.compile(r"^h[1-6]\.\s*", re.MULTILINE)
COLOR_OPEN_RE = re.compile(r"\{color:#?[0-9A-Fa-f]+\}")
COLOR_CLOSE_RE = re.compile(r"\{color\}")
CODE_OPEN_RE = re.compile(r"\{code(?::[^}]*)?\}")
CODE_CLOSE_RE = re.compile(r"\{code\}")
NOFORMAT_RE = re.compile(r"\{noformat\}")
PANEL_RE = re.compile(r"\{panel(?::[^}]*)?\}")
ATTACHMENT_INLINE_RE = re.compile(r"\[\^([^\]]+)\]")
IMAGE_INLINE_RE = re.compile(r"!([^!\n|]+?)(?:\|[^!]*)?!")
BULLET_RE = re.compile(r"^\*\s+", re.MULTILINE)
BLANK_RUN_RE = re.compile(r"\n{3,}")
TRAILING_WS_RE = re.compile(r"[ \t]+$", re.MULTILINE)


def strip_markup(text) -> str:
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return ""
    s = str(text)
    s = H_RE.sub("", s)
    s = COLOR_OPEN_RE.sub("", s)
    s = COLOR_CLOSE_RE.sub("", s)
    s = CODE_OPEN_RE.sub("", s)
    s = CODE_CLOSE_RE.sub("", s)
    s = NOFORMAT_RE.sub("", s)
    s = PANEL_RE.sub("", s)
    s = ATTACHMENT_INLINE_RE.sub(lambda m: f"[attachment: {m.group(1)}]", s)
    s = IMAGE_INLINE_RE.sub(lambda m: f"[image: {m.group(1)}]", s)
    s = BULLET_RE.sub("- ", s)
    s = re.sub(r"(?<![\w*])\*([^*\n]{1,200}?)\*(?![\w*])", r"\1", s)
    s = re.sub(r"(?<![\w_])_([^_\n]{1,200}?)_(?![\w_])", r"\1", s)
    s = re.sub(r"(?<![\w+])\+([^+\n]{1,200}?)\+(?![\w+])", r"\1", s)
    # Patch 5.1: strikethrough regex removed (too broad; matched non-markup dashes)
    s = TRAILING_WS_RE.sub("", s)
    s = BLANK_RUN_RE.sub("\n\n", s)
    return s.strip()


# ---------------------------------------------------------------------------
# Patch 1.6 — PII audit on redacted public outputs
# ---------------------------------------------------------------------------

PII_AUDIT_PATTERNS = {
    "residual_email_at_sign": re.compile(r"@"),
    "residual_phone": re.compile(r"\d{3}[-.\s]\d{3}[-.\s]\d{4}"),
    "district_suffix": re.compile(r"\b(SD|ISD|USD|CSD|CUSD)\b"),
    "school_district_phrase": re.compile(r"School\s+District|Public\s+Schools", re.IGNORECASE),
    "two_word_capname": re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"),
}


def run_pii_audit(out_df: pd.DataFrame, comments_long: pd.DataFrame, internal_staff: set[str]) -> dict:
    audit: dict[str, dict] = {}
    text_columns = ["summary", "description", "acceptance_criteria",
                    "text_blob_customer_problem", "text_blob_full_evidence"]
    samples_by_pattern: dict[str, list[tuple[str, str]]] = defaultdict(list)
    counts: dict[str, int] = defaultdict(int)

    def scan(text: str, source: str) -> None:
        for name, pat in PII_AUDIT_PATTERNS.items():
            for m in pat.finditer(text):
                hit = m.group(0)
                if name == "two_word_capname" and hit in internal_staff:
                    continue
                counts[name] += 1
                if len(samples_by_pattern[name]) < 5:
                    snippet = text[max(0, m.start() - 30): m.end() + 30].replace("\n", " ")
                    samples_by_pattern[name].append((source, snippet))

    for col in text_columns:
        if col not in out_df.columns:
            continue
        for issue_key, val in zip(out_df["issue_key"].tolist(), out_df[col].tolist()):
            if isinstance(val, str) and val:
                scan(val, f"{issue_key}:{col}")

    if not comments_long.empty:
        for issue_key, ci, ctext in zip(
            comments_long["issue_key"].tolist(),
            comments_long["comment_index"].tolist(),
            comments_long["comment_text"].tolist(),
        ):
            if isinstance(ctext, str) and ctext:
                scan(ctext, f"{issue_key}:comment[{ci}]")

    for k in PII_AUDIT_PATTERNS:
        audit[k] = {"hits": int(counts.get(k, 0)), "samples": samples_by_pattern.get(k, [])}
    return audit


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--outdir-public", required=True, type=Path,
                        help="Where redacted, shareable artifacts are written.")
    parser.add_argument("--outdir-private", default=None, type=Path,
                        help="Optional. Where district_map.json and pii_audit_report.md are "
                             "written. If unset, no re-identification map is produced.")
    parser.add_argument("--reference-date", default=None,
                        help="YYYY-MM-DD used for unresolved_age_days. Default: max(Updated).")
    parser.add_argument("--no-ner", action="store_true",
                        help="Skip spaCy NER person redaction. Writes PII_INCOMPLETE.flag.")
    args = parser.parse_args()

    args.outdir_public.mkdir(parents=True, exist_ok=True)
    if args.outdir_private:
        args.outdir_private.mkdir(parents=True, exist_ok=True)
    else:
        print("[notice] --outdir-private not set; district_map.json and pii_audit_report.md "
              "will be SUPPRESSED. Re-run with --outdir-private <dir> to produce them.",
              flush=True)

    print(f"[load] reading {args.input}", flush=True)
    df = pd.read_csv(args.input, low_memory=False)
    print(f"[load] {len(df):,} rows × {len(df.columns)} cols", flush=True)

    # Pre-resolve reference date (Patch 4.1)
    if args.reference_date:
        reference_date = pd.Timestamp(args.reference_date, tz="UTC")
    else:
        updated = pd.to_datetime(df.get("Updated"), errors="coerce", utc=True)
        reference_date = updated.max()
        if pd.isna(reference_date):
            reference_date = pd.Timestamp.utcnow()
    print(f"[ref] reference_date = {reference_date.isoformat()}", flush=True)

    # ----- Internal staff allowlist (used for NER and PII audit) -----
    internal_staff = build_internal_staff_set(df)
    print(f"[step0] internal-staff allowlist: {len(internal_staff)} unique names", flush=True)

    # ----- Step 1 — identify column families -----
    print("[step1] identifying repeated column families", flush=True)
    sprint_cols = family_columns(df, "Sprint")
    component_cols = family_columns(df, "Components")
    label_cols = family_columns(df, "Labels")
    comment_cols = family_columns(df, "Comment")
    attachment_cols = family_columns(df, "Attachment")
    watcher_cols = family_columns(df, "Watchers")
    inward_relates_cols = family_columns(df, "Inward issue link (Relates)")
    outward_relates_cols = family_columns(df, "Outward issue link (Relates)")
    inward_blocks_cols = family_columns(df, "Inward issue link (Blocks)")
    outward_blocks_cols = family_columns(df, "Outward issue link (Blocks)")
    ac_cols = family_columns(df, "Custom field (Acceptance Criteria)")

    link_specs = []
    for base in [
        "Inward issue link (Action item)", "Outward issue link (Action item)",
        "Inward issue link (Blocks)", "Outward issue link (Blocks)",
        "Inward issue link (Cloners)", "Outward issue link (Cloners)",
        "Inward issue link (Duplicate)", "Outward issue link (Duplicate)",
        "Outward issue link (Polaris work item link)",
        "Inward issue link (Post-Incident Reviews)",
        "Inward issue link (Problem/Incident)", "Outward issue link (Problem/Incident)",
        "Inward issue link (Relates)", "Outward issue link (Relates)",
        "Inward issue link (Test Case)", "Outward issue link (Test Case)",
        "Inward issue link (Work item split)", "Outward issue link (Work item split)",
    ]:
        cols = family_columns(df, base)
        if not cols:
            continue
        m = re.match(r"(Inward|Outward) issue link \((.+)\)$", base)
        direction = m.group(1).lower()
        link_type = m.group(2)
        link_specs.append((cols, direction, link_type))

    # ----- Patch 2.2 — Freshdesk extraction (BEFORE redaction) -----
    print("[step0] extracting Freshdesk URLs (pre-redaction)", flush=True)
    freshdesk_per_issue: dict[str, set[str]] = defaultdict(set)
    fd_text_cols = ["Summary", "Description", "Parent summary"] + ac_cols + comment_cols + attachment_cols
    for col in fd_text_cols:
        if col not in df.columns:
            continue
        series = df[col]
        for idx, val in series.items():
            if val is None or (isinstance(val, float) and pd.isna(val)):
                continue
            for m in FRESHDESK_URL_RE.finditer(str(val)):
                freshdesk_per_issue[df.at[idx, "Issue key"]].add(m.group(1))
    print(f"[step0] Freshdesk IDs found across {len(freshdesk_per_issue)} issues", flush=True)

    # ----- Step 0 — regex redaction (districts, email, phone) -----
    print("[step0] regex redaction (districts, email, phone)", flush=True)
    mapper = DistrictMapper()

    redact_field_groups = [
        ("summary", ["Summary"]),
        ("description", ["Description"]),
        ("parent_summary", ["Parent summary"]),
        ("acceptance_criteria", ac_cols),
        ("comment", comment_cols),
        ("attachment", attachment_cols),
    ]

    issue_keys = df["Issue key"].tolist()
    for category, cols in redact_field_groups:
        for col in cols:
            if col not in df.columns:
                continue
            new_vals = []
            for issue_key, val in zip(issue_keys, df[col].tolist()):
                new_vals.append(redact_simple(val, mapper, issue_key=issue_key, field=category))
            df[col] = new_vals

    # ----- Step 0 — NER pass -----
    if args.no_ner:
        print("=" * 70, flush=True)
        print("WARNING — NER PERSON REDACTION SKIPPED", flush=True)
        print("WARNING — public output may contain unredacted personal names", flush=True)
        print("WARNING — DO NOT distribute outputs without re-running with NER", flush=True)
        print("WARNING — flag file PII_INCOMPLETE.flag will be written to public outdir", flush=True)
        print("=" * 70, flush=True)
        (args.outdir_public / "PII_INCOMPLETE.flag").write_text(
            "NER person redaction was skipped on this run.\n"
            f"Generated: {datetime.now(timezone.utc).isoformat()}\n"
            "Re-run clean_im_data.py without --no-ner before distributing artifacts.\n",
            encoding="utf-8",
        )
    else:
        print("[step0] loading spaCy en_core_web_sm", flush=True)
        import spacy
        nlp = spacy.load("en_core_web_sm")
        ner_cols = ["Summary", "Description", "Parent summary"] + ac_cols + comment_cols
        ner_cols = [c for c in ner_cols if c in df.columns]
        for col in ner_cols:
            series = df[col]
            non_null_idx = series.notna() & (series.astype(str).str.len() > 0)
            if non_null_idx.sum() == 0:
                continue
            print(f"[step0] NER {col}: {int(non_null_idx.sum())} cells", flush=True)
            texts = series[non_null_idx].astype(str).tolist()
            redacted = redact_persons_batch(texts, internal_staff, nlp)
            new_series = series.copy()
            new_series.loc[non_null_idx] = redacted
            df[col] = new_series

    # ----- Step 4a — markup cleanup -----
    print("[step4] stripping wiki markup from text fields", flush=True)
    for col in ["Summary", "Description", "Parent summary"] + ac_cols + comment_cols:
        if col in df.columns:
            df[col] = df[col].map(strip_markup)

    # ----- Step 1 — aggregate per-row -----
    print("[step1] aggregating per-row lists/counts", flush=True)
    sprints_all = df[sprint_cols].apply(lambda r: collect_list(r, sprint_cols), axis=1) if sprint_cols else pd.Series([[]] * len(df))
    components_all = df[component_cols].apply(lambda r: collect_list(r, component_cols), axis=1) if component_cols else pd.Series([[]] * len(df))
    labels_all = df[label_cols].apply(lambda r: collect_list(r, label_cols), axis=1) if label_cols else pd.Series([[]] * len(df))

    def first_or_none(lst):
        return lst[0] if lst else None

    def last_or_none(lst):
        return lst[-1] if lst else None

    sprint_first = sprints_all.map(first_or_none)
    sprint_latest = sprints_all.map(last_or_none)
    sprint_count = sprints_all.map(len)
    component_primary = components_all.map(first_or_none)
    label_count = labels_all.map(len)

    comments_per_row = df[comment_cols].apply(lambda r: collect_list(r, comment_cols), axis=1) if comment_cols else pd.Series([[]] * len(df))
    comment_count = comments_per_row.map(len)
    comments_concatenated = comments_per_row.map(lambda lst: "\n---\n".join(lst))
    attachment_count = df[attachment_cols].apply(lambda r: len(collect_list(r, attachment_cols)), axis=1) if attachment_cols else pd.Series([0] * len(df))
    watcher_count = df[watcher_cols].apply(lambda r: len(collect_list(r, watcher_cols)), axis=1) if watcher_cols else pd.Series([0] * len(df))

    relates_count = pd.Series([0] * len(df))
    if inward_relates_cols:
        relates_count = relates_count + df[inward_relates_cols].apply(lambda r: len(collect_list(r, inward_relates_cols)), axis=1)
    if outward_relates_cols:
        relates_count = relates_count + df[outward_relates_cols].apply(lambda r: len(collect_list(r, outward_relates_cols)), axis=1)

    blocks_count = pd.Series([0] * len(df))
    if inward_blocks_cols:
        blocks_count = blocks_count + df[inward_blocks_cols].apply(lambda r: len(collect_list(r, inward_blocks_cols)), axis=1)
    if outward_blocks_cols:
        blocks_count = blocks_count + df[outward_blocks_cols].apply(lambda r: len(collect_list(r, outward_blocks_cols)), axis=1)

    ac_combined = df[ac_cols].bfill(axis=1).iloc[:, 0] if ac_cols else pd.Series([None] * len(df))

    # ----- Step 2 — normalized table -----
    print("[step2] building normalized ticket table", flush=True)
    out = pd.DataFrame()
    out["issue_key"] = df["Issue key"]
    out["issue_id"] = pd.to_numeric(df["Issue id"], errors="coerce").astype("Int64")
    out["issue_type"] = df["Issue Type"]
    out["summary"] = df["Summary"]
    out["description"] = df["Description"]
    out["acceptance_criteria"] = ac_combined
    out["priority"] = df.get("Priority")

    # Patch 4.3 — strip whitespace before mapping (don't lowercase)
    status_norm = df.get("Status").astype("string").str.strip()
    out["status_raw"] = status_norm
    out["resolution_raw"] = df.get("Resolution")
    out["status_category"] = df.get("Status Category")
    out["status_category_changed"] = pd.to_datetime(df.get("Status Category Changed"), errors="coerce", utc=True)
    out["assignee"] = df.get("Assignee")
    out["reporter"] = df.get("Reporter")
    out["creator"] = df.get("Creator")
    out["created_at"] = pd.to_datetime(df.get("Created"), errors="coerce", utc=True)
    out["updated_at"] = pd.to_datetime(df.get("Updated"), errors="coerce", utc=True)
    out["resolved_at"] = pd.to_datetime(df.get("Resolved"), errors="coerce", utc=True)
    out["due_date"] = pd.to_datetime(df.get("Due date"), errors="coerce").dt.date
    out["story_points"] = pd.to_numeric(df.get("Custom field (Story Points)"), errors="coerce")
    out["parent_key"] = df.get("Parent key")
    out["parent_summary"] = df.get("Parent summary")
    out["components_all"] = components_all.map(lambda lst: "|".join(lst))
    out["component_primary"] = component_primary
    out["labels_all"] = labels_all.map(lambda lst: "|".join(lst))
    out["label_count"] = label_count
    out["sprints_all"] = sprints_all.map(lambda lst: "|".join(lst))
    out["sprint_first"] = sprint_first
    out["sprint_latest"] = sprint_latest
    out["sprint_count"] = sprint_count
    out["comment_count"] = comment_count
    out["attachment_count"] = attachment_count
    out["watcher_count"] = watcher_count
    out["relates_count"] = relates_count
    out["blocks_count"] = blocks_count

    keep_custom = [
        ("Custom field (Issue Category)", "issue_category"),
        ("Custom field (Root Cause)", "root_cause"),
        ("Custom field (Module)", "module"),
        ("Custom field (UAT Approved)", "uat_approved"),
        ("Custom field (Required For Regression)", "required_for_regression"),
        ("Custom field (Site Environment)", "site_environment"),
        ("Custom field (T-Shirt Sizing)", "t_shirt_sizing"),
    ]
    for src, dst in keep_custom:
        if src in df.columns:
            out[dst] = df[src]
    out["project_key"] = df.get("Project key")

    # ----- Patch 2.1 — structured district columns -----
    print("[step2] folding district hits into structured columns", flush=True)

    def per_issue_districts(issue_key):
        hits = mapper.hits.get(issue_key, [])
        labels = sorted({lab for lab, _ in hits})
        sources = sorted({src for _, src in hits if src})
        return "|".join(labels), len(labels), bool(labels), ",".join(sources)

    dist_data = out["issue_key"].map(per_issue_districts)
    out["districts_all"] = dist_data.map(lambda t: t[0])
    out["district_count"] = dist_data.map(lambda t: t[1])
    out["has_district_signal"] = dist_data.map(lambda t: t[2])
    out["district_source_fields"] = dist_data.map(lambda t: t[3])

    # ----- Patch 2.2 — structured Freshdesk columns -----
    out["freshdesk_ids_all"] = out["issue_key"].map(
        lambda k: "|".join(sorted(freshdesk_per_issue.get(k, set())))
    )
    out["freshdesk_id_count"] = out["issue_key"].map(lambda k: len(freshdesk_per_issue.get(k, set())))
    out["has_freshdesk_signal"] = out["freshdesk_id_count"] > 0

    # ----- Step 3 — lifecycle -----
    print("[step3] computing lifecycle and closure_confidence", flush=True)
    out["status_clean"] = out["status_raw"].map(STATUS_CLEAN_MAP)
    cat_fallback = {"Done": "done", "In Progress": "in_progress", "To Do": "open"}
    unmapped_mask = out["status_clean"].isna()
    out.loc[unmapped_mask, "status_clean"] = out.loc[unmapped_mask, "status_category"].map(cat_fallback)
    out["status_clean"] = out["status_clean"].fillna("unknown")

    def lifecycle_of(row):
        sc = row["status_clean"]
        resolved = pd.notna(row["resolved_at"])
        if sc == "rejected":
            return "rejected"
        if sc == "duplicate":
            return "duplicate"
        if sc == "done" and resolved:
            return "resolved"
        if sc == "done" and not resolved:
            return "done_no_timestamp"
        if sc == "in_progress":
            return "in_progress"
        if sc == "open":
            return "open"
        return "unknown"

    out["lifecycle"] = out.apply(lifecycle_of, axis=1)

    def closure_conf(row):
        if row["lifecycle"] in ("resolved", "rejected", "duplicate") and pd.notna(row["resolved_at"]):
            return "high"
        if row["lifecycle"] == "done_no_timestamp":
            return "medium"
        return "low"

    out["closure_confidence"] = out.apply(closure_conf, axis=1)

    # ----- Patch 3 — two text blobs -----
    print("[step4] building text_blob_customer_problem and text_blob_full_evidence", flush=True)

    def build_customer_problem(row):
        parts = []
        s = row["summary"]
        if isinstance(s, str) and s.strip():
            parts.append(f"TITLE: {s.strip()}")
        d = row["description"]
        if isinstance(d, str) and d.strip():
            parts.append(f"DESCRIPTION: {d.strip()}")
        ac = row["acceptance_criteria"]
        if isinstance(ac, str) and ac.strip():
            parts.append(f"ACCEPTANCE CRITERIA: {ac.strip()}")
        return "\n\n".join(parts)

    def build_full_evidence(row):
        base = row["text_blob_customer_problem"]
        cc = row["_comments_concat"]
        if isinstance(cc, str) and cc.strip():
            return base + ("\n\n" if base else "") + f"COMMENTS:\n{cc.strip()}"
        return base

    out["_comments_concat"] = comments_concatenated
    out["text_blob_customer_problem"] = out.apply(build_customer_problem, axis=1)
    out["text_blob_full_evidence"] = out.apply(build_full_evidence, axis=1)
    out["text_blob_customer_problem_length"] = out["text_blob_customer_problem"].str.len()
    out["text_blob_full_evidence_length"] = out["text_blob_full_evidence"].str.len()
    out.drop(columns=["_comments_concat"], inplace=True)

    # ----- Drop QA - Sub-Task -----
    pre_drop = len(out)
    keep_mask = ~out["issue_type"].isin(DROP_TYPES)
    out = out[keep_mask].reset_index(drop=True)
    df_filtered = df[keep_mask.values].reset_index(drop=True)
    comments_per_row_f = comments_per_row[keep_mask.values].reset_index(drop=True)
    print(f"[step2] dropped {pre_drop - len(out)} {DROP_TYPES} rows; {len(out):,} remain", flush=True)

    # ----- Step 5 — durations + thresholds -----
    print("[step5] computing per-type duration thresholds", flush=True)
    delta_days = (out["resolved_at"] - out["created_at"]).dt.total_seconds() / 86400.0
    out["duration_resolved_days"] = delta_days.where(out["closure_confidence"] == "high")

    open_like = out["lifecycle"].isin(["open", "in_progress"])
    age_days = (reference_date - out["created_at"]).dt.total_seconds() / 86400.0
    out["unresolved_age_days"] = age_days.where(open_like)

    thresholds: dict[str, dict] = {}
    high = out[out["closure_confidence"] == "high"]
    for itype, sub in high.groupby("issue_type"):
        if itype in {"Sub-task"}:
            continue
        if len(sub) < 10:
            continue
        thresholds[itype] = {
            "n": int(len(sub)),
            "p75": float(sub["duration_resolved_days"].quantile(0.75)),
            "p90": float(sub["duration_resolved_days"].quantile(0.90)),
            "p95": float(sub["duration_resolved_days"].quantile(0.95)),
        }

    out["linger_threshold_for_type"] = out["issue_type"].map(
        lambda t: thresholds.get(t, {}).get("p90")
    )
    out["is_linger"] = (
        (out["closure_confidence"] == "high")
        & out["duration_resolved_days"].notna()
        & out["linger_threshold_for_type"].notna()
        & (out["duration_resolved_days"] >= out["linger_threshold_for_type"])
    )
    out["is_passive_linger"] = open_like & (out["unresolved_age_days"] >= 365)
    excluded = out["issue_type"].isin({"Sub-task", "QA - Sub-Task"})
    out.loc[excluded, ["linger_threshold_for_type", "is_linger", "is_passive_linger"]] = [None, False, False]

    # ----- Step 6 — component inventory -----
    print("[step6] writing component inventory", flush=True)
    comp_counts: dict[str, int] = {}
    for lst in components_all[keep_mask.values]:
        for c in lst:
            comp_counts[c] = comp_counts.get(c, 0) + 1
    inventory_path = args.outdir_public / "component_inventory.txt"
    with inventory_path.open("w", encoding="utf-8") as f:
        f.write("# Component inventory (post Sub-Task/QA-Sub-Task drop)\n")
        f.write(f"# Generated: {datetime.now(timezone.utc).isoformat()}\n\n")
        for comp, n in sorted(comp_counts.items(), key=lambda kv: (-kv[1], kv[0])):
            f.write(f"{n:>5}  {comp}\n")
    print("[step6] top components:", flush=True)
    for comp, n in sorted(comp_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:15]:
        print(f"   {n:>5}  {comp}", flush=True)

    # ----- Step 7 — long tables -----
    print("[step7] building comments_long, links_long", flush=True)
    comments_rows = []
    for issue_key, lst in zip(out["issue_key"].tolist(), comments_per_row_f.tolist()):
        for i, c in enumerate(lst, start=1):
            comments_rows.append({
                "issue_key": issue_key, "comment_index": i,
                "comment_text": c, "comment_length": len(c),
            })
    comments_long = pd.DataFrame(comments_rows)

    link_rows = []
    for cols, direction, link_type in link_specs:
        cols_present = [c for c in cols if c in df_filtered.columns]
        if not cols_present:
            continue
        for col in cols_present:
            for issue_key, val in zip(df_filtered["Issue key"].tolist(), df_filtered[col].tolist()):
                if val is None or (isinstance(val, float) and pd.isna(val)):
                    continue
                s = str(val).strip()
                if not s:
                    continue
                link_rows.append({
                    "source_issue_key": issue_key, "link_type": link_type,
                    "direction": direction, "linked_issue_key": s,
                })
    links_long = pd.DataFrame(link_rows)

    # ----- Step 8 — candidate flags (length filter on customer-problem blob) -----
    print("[step8] computing candidate artifact flags", flush=True)
    pain_types = {"Bug", "Enhancement", "Improvement", "Tech-Debt"}
    cp_len = out["text_blob_customer_problem_length"]
    flags = pd.DataFrame()
    flags["issue_key"] = out["issue_key"]
    flags["pain_page_candidate"] = (
        out["issue_type"].isin(pain_types) & (cp_len >= 100) & out["component_primary"].notna()
    )
    flags["rediscovery_candidate"] = (
        (out["issue_type"] == "Bug") & (cp_len >= 100) & out["component_primary"].notna()
    )
    flags["dismissal_candidate"] = out["lifecycle"].isin(["rejected", "duplicate"])
    flags["linger_candidate"] = out["is_linger"].fillna(False).astype(bool)

    def reason(row):
        bits = []
        if row["pain_page_candidate"]:
            bits.append("pain w/ component")
        if row["rediscovery_candidate"]:
            bits.append("bug w/ component")
        if row["dismissal_candidate"]:
            bits.append("rejected/dup")
        if row["linger_candidate"]:
            bits.append("p90 linger")
        return "; ".join(bits) if bits else ""

    flags["candidate_reason"] = flags.apply(reason, axis=1)

    # ----- Public outputs -----
    print("[write] writing public artifacts", flush=True)
    tickets_path = args.outdir_public / "tickets_clean.csv"
    out.to_csv(tickets_path, index=False, encoding="utf-8")
    print(f"   {tickets_path}: {out.shape}", flush=True)

    comments_path = args.outdir_public / "ticket_comments_long.csv"
    comments_long.to_csv(comments_path, index=False, encoding="utf-8")
    print(f"   {comments_path}: {comments_long.shape}", flush=True)

    links_path = args.outdir_public / "ticket_links_long.csv"
    links_long.to_csv(links_path, index=False, encoding="utf-8")
    print(f"   {links_path}: {links_long.shape}", flush=True)

    flags_path = args.outdir_public / "candidate_artifact_flags.csv"
    flags.to_csv(flags_path, index=False, encoding="utf-8")
    print(f"   {flags_path}: {flags.shape}", flush=True)

    thresh_path = args.outdir_public / "type_thresholds.json"
    with thresh_path.open("w", encoding="utf-8") as f:
        json.dump(thresholds, f, indent=2)

    # ----- PII audit (Patch 1.6) -----
    print("[audit] running PII audit on redacted public outputs", flush=True)
    audit = run_pii_audit(out, comments_long, internal_staff)

    # ----- Definition-of-done checks (Patch 5.2 fail-loud) -----
    print("[verify] definition of done", flush=True)
    n_cols = len(out.columns)
    print(f"   tickets_clean.csv columns = {n_cols} (target 50–80)", flush=True)
    if not (50 <= n_cols <= 80):
        print(f"   WARNING: column count {n_cols} outside the 50–80 band", flush=True)

    analytic = out[out["issue_type"].isin(ANALYTIC_TYPES)]
    blob_cov = float((analytic["text_blob_customer_problem_length"] > 0).mean()) if len(analytic) else 0.0
    print(f"   text_blob_customer_problem coverage in analytic set: {blob_cov:.1%} (target >= 70%)", flush=True)
    if blob_cov < 0.70:
        print(f"   WARNING: customer-problem blob coverage {blob_cov:.1%} below 70% threshold; "
              f"text consolidation likely incomplete; revisit Step 4.", flush=True)

    n_pain = int(flags["pain_page_candidate"].sum())
    print(f"   pain_page_candidate count: {n_pain} (target >= 200)", flush=True)
    if n_pain < 200:
        print(f"   WARNING: pain_page_candidate count = {n_pain} (target >= 200). "
              f"Text consolidation likely incomplete; revisit Step 4.", flush=True)

    print(f"   district_map entries: {len(mapper._key_to_label)}", flush=True)
    print(f"   has_district_signal coverage: {float(out['has_district_signal'].mean()):.1%}", flush=True)
    print(f"   has_freshdesk_signal coverage: {float(out['has_freshdesk_signal'].mean()):.1%}", flush=True)

    # ----- Validation report (Patch 5.3 + 4.2) -----
    print("[write] cleaning_validation_report.md", flush=True)
    val_path = args.outdir_public / "cleaning_validation_report.md"
    raw_status_counts = df["Status"].astype("string").str.strip().value_counts(dropna=False)
    resolved_present_by_status = (
        df.assign(_resolved_present=pd.to_datetime(df["Resolved"], errors="coerce", utc=True).notna(),
                  _status=df["Status"].astype("string").str.strip())
          .groupby("_status")["_resolved_present"].sum()
    )
    unmapped_status_values = [s for s in raw_status_counts.index if s not in STATUS_CLEAN_MAP and pd.notna(s)]
    neg_dur = out[out["duration_resolved_days"].notna() & (out["duration_resolved_days"] < 0)]
    resolved_low_conf = out[out["resolved_at"].notna() & (out["closure_confidence"] != "high")]

    with val_path.open("w", encoding="utf-8") as f:
        f.write("# IM cleaning validation report\n\n")
        f.write(f"_Generated {datetime.now(timezone.utc).isoformat()}_\n\n")
        f.write(f"- Source: `{args.input.name}`\n")
        f.write(f"- Reference date: `{reference_date.isoformat()}`\n")
        f.write(f"- NER skipped: **{args.no_ner}**\n\n")

        f.write("## Row counts\n\n")
        f.write(f"- Pre-drop: {pre_drop}\n")
        f.write(f"- Post-drop (QA-Sub-Task): {len(out)}\n\n")

        f.write("## Per-issue-type counts (analytic set)\n\n")
        f.write("| issue_type | total | high_conf | mean cp_len | mean fe_len |\n")
        f.write("| --- | ---: | ---: | ---: | ---: |\n")
        for itype in sorted(out["issue_type"].dropna().unique()):
            sub = out[out["issue_type"] == itype]
            high_n = int((sub["closure_confidence"] == "high").sum())
            cp_mean = float(sub["text_blob_customer_problem_length"].mean()) if len(sub) else 0.0
            fe_mean = float(sub["text_blob_full_evidence_length"].mean()) if len(sub) else 0.0
            f.write(f"| {itype} | {len(sub)} | {high_n} | {cp_mean:.0f} | {fe_mean:.0f} |\n")

        f.write("\n## Lifecycle distribution\n\n")
        f.write("| lifecycle | count |\n| --- | ---: |\n")
        for k, v in out["lifecycle"].value_counts().items():
            f.write(f"| {k} | {int(v)} |\n")

        f.write("\n## Closure confidence distribution\n\n")
        f.write("| closure_confidence | count |\n| --- | ---: |\n")
        for k, v in out["closure_confidence"].value_counts().items():
            f.write(f"| {k} | {int(v)} |\n")

        f.write("\n## Status mapping\n\n")
        f.write("| status_raw | count | mapped to | rows w/ Resolved | suspect? |\n")
        f.write("| --- | ---: | --- | ---: | --- |\n")
        for status, n in raw_status_counts.items():
            mapped = STATUS_CLEAN_MAP.get(status, "(via Status Category fallback)")
            n_resolved = int(resolved_present_by_status.get(status, 0))
            suspect = "**YES**" if status in SUSPECT_STATUSES else ""
            f.write(f"| {status!r} | {int(n)} | {mapped} | {n_resolved} | {suspect} |\n")

        f.write("\n### Suspect statuses (need confirmation from Hussain)\n\n")
        f.write("Currently mapped to `done`. Confirm each is genuinely terminal for the workflows it appears in; if not, update `STATUS_CLEAN_MAP` in `clean_im_data.py` and re-run.\n\n")
        f.write("| status | count | rows w/ Resolved |\n| --- | ---: | ---: |\n")
        for status in SUSPECT_STATUSES:
            n = int(raw_status_counts.get(status, 0))
            n_resolved = int(resolved_present_by_status.get(status, 0))
            f.write(f"| {status} | {n} | {n_resolved} |\n")

        if unmapped_status_values:
            f.write("\n### Unmapped status values (auto-mapped via Status Category fallback)\n\n")
            f.write("| status | count |\n| --- | ---: |\n")
            for s in unmapped_status_values:
                f.write(f"| {s!r} | {int(raw_status_counts[s])} |\n")
        else:
            f.write("\n### Unmapped status values\n\nNone — every distinct status in this corpus has an explicit mapping.\n")

        f.write("\n## Data anomalies\n\n")
        f.write(f"- Negative durations (resolved_at < created_at): **{len(neg_dur)}** rows\n")
        f.write(f"- resolved_at present but closure_confidence != 'high': **{len(resolved_low_conf)}** rows\n\n")

        f.write("## Top 20 components\n\n")
        f.write("| component | count |\n| --- | ---: |\n")
        for comp, n in sorted(comp_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:20]:
            f.write(f"| {comp} | {n} |\n")

        f.write("\n## District signal\n\n")
        f.write(f"- Distinct district labels: {len(mapper._key_to_label)}\n")
        f.write(f"- Tickets with `has_district_signal == True`: {int(out['has_district_signal'].sum())} "
                f"({float(out['has_district_signal'].mean()):.1%})\n")
        bug_dist_cov = float(out[out['issue_type'] == 'Bug']['has_district_signal'].mean()) if (out['issue_type'] == 'Bug').any() else 0.0
        f.write(f"- Among Bugs: {bug_dist_cov:.1%}\n")
        f.write("\nSource-field breakdown (which fields contained district mentions):\n\n")
        src_counts: dict[str, int] = defaultdict(int)
        for hits in mapper.hits.values():
            for _, src in hits:
                if src:
                    src_counts[src] += 1
        f.write("| source_field | hits |\n| --- | ---: |\n")
        for k, v in sorted(src_counts.items(), key=lambda kv: -kv[1]):
            f.write(f"| {k} | {v} |\n")

        f.write("\n## Freshdesk signal\n\n")
        f.write(f"- Distinct Freshdesk IDs referenced: "
                f"{len({fid for ids in freshdesk_per_issue.values() for fid in ids})}\n")
        f.write(f"- Tickets with `has_freshdesk_signal == True`: {int(out['has_freshdesk_signal'].sum())} "
                f"({float(out['has_freshdesk_signal'].mean()):.1%})\n")
        bug_fd_cov = float(out[out['issue_type'] == 'Bug']['has_freshdesk_signal'].mean()) if (out['issue_type'] == 'Bug').any() else 0.0
        f.write(f"- Among Bugs: {bug_fd_cov:.1%}\n")

        f.write("\n## PII audit summary (counts only — samples are in private outdir)\n\n")
        f.write("| pattern | hits |\n| --- | ---: |\n")
        for k, v in audit.items():
            f.write(f"| {k} | {v['hits']} |\n")

        f.write("\n## Candidate flag counts\n\n")
        f.write("| flag | count |\n| --- | ---: |\n")
        for col in ["pain_page_candidate", "rediscovery_candidate", "dismissal_candidate", "linger_candidate"]:
            f.write(f"| {col} | {int(flags[col].sum())} |\n")

        f.write("\n## Definition-of-done checks\n\n")
        f.write(f"- Columns in 50–80 band: **{50 <= n_cols <= 80}** (n_cols={n_cols})\n")
        f.write(f"- Customer-problem blob coverage ≥70%: **{blob_cov >= 0.70}** ({blob_cov:.1%})\n")
        f.write(f"- pain_page_candidate ≥ 200: **{n_pain >= 200}** ({n_pain})\n")
        f.write(f"- NER ran (not skipped): **{not args.no_ner}**\n")

    # ----- Private outputs (only if --outdir-private set) -----
    if args.outdir_private:
        print(f"[write] writing private artifacts to {args.outdir_private}", flush=True)
        district_path = args.outdir_private / "district_map.json"
        with district_path.open("w", encoding="utf-8") as f:
            json.dump(mapper.to_json(), f, indent=2, ensure_ascii=False)

        audit_path = args.outdir_private / "pii_audit_report.md"
        with audit_path.open("w", encoding="utf-8") as f:
            f.write("# PII audit report\n\n")
            f.write(f"_Generated {datetime.now(timezone.utc).isoformat()}_\n\n")
            f.write("Patterns scanned across redacted public outputs (tickets_clean.csv text fields "
                    "and ticket_comments_long.csv comment_text).\n\n")
            for name, info in audit.items():
                f.write(f"## `{name}` — {info['hits']} hits\n\n")
                if not info["samples"]:
                    f.write("_No samples captured._\n\n")
                    continue
                for source, snippet in info["samples"]:
                    f.write(f"- **{source}**: `…{snippet}…`\n")
                f.write("\n")
    else:
        print("[notice] private outdir not set; skipping district_map.json and pii_audit_report.md", flush=True)

    # ----- Data dictionary -----
    print("[write] data_dictionary.md", flush=True)
    dd_path = args.outdir_public / "data_dictionary.md"
    sample_row = out.iloc[0]
    field_docs = [
        ("issue_key", "string", "Source: Issue key", "primary key"),
        ("issue_id", "int", "Source: Issue id", ""),
        ("issue_type", "enum", "Source: Issue Type", ""),
        ("summary", "string", "Source: Summary, post-redaction + markup-strip", ""),
        ("description", "string", "Source: Description, post-redaction + markup-strip", ""),
        ("acceptance_criteria", "string", "Coalesced AC columns (post-redaction)", ""),
        ("priority", "enum", "Source: Priority", ""),
        ("status_raw", "string", "Source: Status (whitespace-stripped)", ""),
        ("status_clean", "enum", "Mapped from status_raw", "done/rejected/duplicate/in_progress/open/unknown"),
        ("resolution_raw", "string", "Source: Resolution", "unreliable signal in this corpus"),
        ("status_category", "enum", "Source: Status Category", ""),
        ("status_category_changed", "datetime (UTC)", "Source: Status Category Changed", ""),
        ("lifecycle", "enum", "Derived (Step 3)", ""),
        ("closure_confidence", "enum", "Derived (Step 3)", ""),
        ("assignee", "string", "Source: Assignee (Cybersoft staff — not redacted)", ""),
        ("reporter", "string", "Source: Reporter (Cybersoft staff — not redacted)", ""),
        ("creator", "string", "Source: Creator", ""),
        ("created_at", "datetime (UTC)", "Source: Created", ""),
        ("updated_at", "datetime (UTC)", "Source: Updated", ""),
        ("resolved_at", "datetime (UTC), nullable", "Source: Resolved", ""),
        ("due_date", "date, nullable", "Source: Due date", ""),
        ("story_points", "float, nullable", "Source: Custom field (Story Points)", ""),
        ("parent_key", "string, nullable", "Source: Parent key", ""),
        ("parent_summary", "string, nullable", "Source: Parent summary (post-redaction)", ""),
        ("components_all", "string (pipe-joined)", "Step 1 collapse of Components × N", ""),
        ("component_primary", "string, nullable", "First non-empty Components value", ""),
        ("labels_all", "string (pipe-joined)", "Step 1 collapse of Labels × N", ""),
        ("label_count", "int", "Length of labels_all", ""),
        ("sprints_all", "string (pipe-joined)", "Step 1 collapse of Sprint × 23", ""),
        ("sprint_first", "string, nullable", "First non-empty Sprint value", ""),
        ("sprint_latest", "string, nullable", "Last non-empty Sprint value", ""),
        ("sprint_count", "int", "Length of sprints_all", ""),
        ("comment_count", "int", "Number of non-empty Comment cells", ""),
        ("attachment_count", "int", "Number of non-empty Attachment cells", ""),
        ("watcher_count", "int", "Number of non-empty Watcher cells", "names dropped"),
        ("relates_count", "int", "Inward + Outward Relates link counts", ""),
        ("blocks_count", "int", "Inward + Outward Blocks link counts", ""),
        ("issue_category", "string", "Source: Custom field (Issue Category)", ""),
        ("root_cause", "string", "Source: Custom field (Root Cause)", ""),
        ("module", "string", "Source: Custom field (Module)", ""),
        ("uat_approved", "string", "Source: Custom field (UAT Approved)", ""),
        ("required_for_regression", "string", "Source: Custom field (Required For Regression)", ""),
        ("site_environment", "string", "Source: Custom field (Site Environment)", ""),
        ("t_shirt_sizing", "string", "Source: Custom field (T-Shirt Sizing)", ""),
        ("project_key", "string", "Source: Project key", ""),
        ("districts_all", "string (pipe-joined)", "Patch 2.1 — unique District_<hash> labels found in this ticket's text", ""),
        ("district_count", "int", "len(districts_all)", ""),
        ("has_district_signal", "bool", "district_count > 0", ""),
        ("district_source_fields", "string (comma-joined)", "Which fields contained district mentions", "summary,description,acceptance_criteria,comment,attachment,parent_summary"),
        ("freshdesk_ids_all", "string (pipe-joined)", "Patch 2.2 — Freshdesk ticket IDs referenced in this ticket's text", ""),
        ("freshdesk_id_count", "int", "len(freshdesk_ids_all)", ""),
        ("has_freshdesk_signal", "bool", "freshdesk_id_count > 0", ""),
        ("text_blob_customer_problem", "string", "TITLE + DESCRIPTION + ACCEPTANCE CRITERIA", "use for clustering / pain pages"),
        ("text_blob_full_evidence", "string", "+ COMMENTS section", "use for citation / narrative drafting"),
        ("text_blob_customer_problem_length", "int", "len(text_blob_customer_problem)", ""),
        ("text_blob_full_evidence_length", "int", "len(text_blob_full_evidence)", ""),
        ("duration_resolved_days", "float, nullable", "(resolved_at − created_at) where closure_confidence=='high'", ""),
        ("unresolved_age_days", "float, nullable", f"(reference_date={reference_date.date()} − created_at) for open/in_progress", ""),
        ("linger_threshold_for_type", "float, nullable", "Per-type P90 of duration_resolved_days (closure_confidence=='high')", ""),
        ("is_linger", "bool", "duration_resolved_days >= linger_threshold_for_type", "resolved tickets only"),
        ("is_passive_linger", "bool", "unresolved_age_days >= 365", "open/in_progress tickets only"),
    ]

    with dd_path.open("w", encoding="utf-8") as f:
        f.write("# IM data dictionary (v1)\n\n")
        f.write(f"_Generated {datetime.now(timezone.utc).isoformat()} from `{args.input.name}`._\n\n")
        f.write(f"- Rows after QA-Sub-Task drop: **{len(out):,}**\n")
        f.write(f"- Columns: **{n_cols}**\n")
        f.write(f"- Reference date: `{reference_date.date()}`\n")
        f.write(f"- Distinct district labels: **{len(mapper._key_to_label)}**\n")
        f.write(f"- Distinct Freshdesk IDs referenced: "
                f"**{len({fid for ids in freshdesk_per_issue.values() for fid in ids})}**\n")
        f.write(f"- NER ran: **{not args.no_ner}**\n\n")

        f.write("## Per-type linger thresholds (days)\n\n")
        f.write("| Issue Type | n | P75 | P90 | P95 |\n| --- | ---: | ---: | ---: | ---: |\n")
        for itype in ["Bug", "Story", "Enhancement", "Tech-Debt", "Improvement", "Task"]:
            t = thresholds.get(itype)
            if t:
                f.write(f"| {itype} | {t['n']} | {t['p75']:.1f} | {t['p90']:.1f} | {t['p95']:.1f} |\n")
            else:
                f.write(f"| {itype} | — | — | — | — |\n")
        f.write("\n_Computed from rows where `closure_confidence == 'high'` and `n >= 10`. "
                "Sub-task and QA-Sub-Task excluded. Tech-Debt and Task have zero high-confidence "
                "rows in this corpus — no Resolved timestamp ever set on those types._\n\n")

        f.write("## Lifecycle distribution\n\n")
        f.write("| lifecycle | count |\n| --- | ---: |\n")
        for k, v in out["lifecycle"].value_counts().items():
            f.write(f"| {k} | {int(v)} |\n")

        f.write("\n## Field reference\n\n")
        f.write("| Field | Type | Source / formula | Notes |\n")
        f.write("| --- | --- | --- | --- |\n")
        for name, ttype, src, notes in field_docs:
            f.write(f"| `{name}` | {ttype} | {src} | {notes} |\n")

        f.write("\n## Companion files\n\n")
        f.write("- `ticket_comments_long.csv` — one row per comment (post-redaction)\n")
        f.write("- `ticket_links_long.csv` — one row per inward/outward link\n")
        f.write("- `candidate_artifact_flags.csv` — pre-tagged artifact candidacy per ticket\n")
        f.write("- `component_inventory.txt` — component values + ticket counts\n")
        f.write("- `type_thresholds.json` — per-type P75/P90/P95\n")
        f.write("- `cleaning_validation_report.md` — full validation surface (status mapping, anomalies, suspect statuses)\n")
        f.write("\n_(Private outdir, when set)_\n")
        f.write("- `district_map.json` — re-identification map. **Do not co-locate with the public outdir.**\n")
        f.write("- `pii_audit_report.md` — residual-pattern hits with sample snippets\n")

        f.write("\n## Known limitations (corpus surprises)\n\n")
        f.write("1. **Resolution field is effectively empty** as a structured signal — only 'Done' and one 'Duplicate' appear. Won't-Fix detection lives in `status_clean=='rejected'`, not Resolution.\n")
        f.write("2. **Description is ~50% populated.** `text_blob_full_evidence` salvages most of the rest via concatenated comments.\n")
        f.write("3. **Done-without-timestamp bucket exists** (`lifecycle=='done_no_timestamp'`) — excluded from linger thresholds.\n")
        f.write("4. **~41% of the raw corpus is Sub-task** (kept in tickets_clean.csv but excluded from linger calculations). QA-Sub-Task rows were dropped entirely.\n")
        f.write("5. **Median open-ticket age is large** — most of the open backlog is archaeological.\n")
        f.write("6. **Components is effectively a single-bucket axis on this corpus.** ~91% of analytic tickets carry only the catch-all `Item Management` component. Sub-module-shaped tags (`Inventory`, `Menu Planning`, `Automation`, `Data-Migration`) are tiny tails. Step 6's 'default to component-keyed buckets' assumption does not hold here. **Decision required:** Rahul + Justin should pick the bucketing axis before clustering. Candidates: `issue_category` (~10% coverage), `root_cause` (~16%), `parent_key`-derived epic names, or title-derived noun-phrase clustering on the catch-all 91%. The validation report has the counts.\n")
        f.write("7. **Tech-Debt and Task have zero high-confidence rows** — none have `Resolved` set, so per-type linger thresholds for these types cannot be computed.\n")
        f.write("8. **Suspect status mappings.** `Deployed to QA`, `Ready For Merge`, `Release Merge`, `Fixed` are mapped to `done`. Confirm with Hussain; counts are in the validation report.\n")
        if args.no_ner:
            f.write("9. **PERSON redaction was SKIPPED on this run.** `PII_INCOMPLETE.flag` is present in the public outdir. Do not distribute these outputs.\n")

    print("[done]", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
