#!/usr/bin/env python3
"""
render_changelog.py — Generates wiki/training/whats-new.html from sync state.

Read order (preferred -> fallback):
  1. .brain-state.json -> prior_runs[]   (authoritative when populated by ingest.py)
  2. runs.log.json     -> rolling snapshot log managed by this script
  3. raw/tickets/ mtimes (direct filesystem fallback when neither above is available)

Writes:
  wiki/training/whats-new.html   — single self-contained HTML, atomic write
  runs.log.json                   — rolling snapshot log; appended only when fingerprint changes

Schema of runs.log.json (v2):
  {
    "version": 2,
    "snapshot": { "<KEY>": "<sha1 of file contents>", ... },
    "runs": [
      {
        "ts":           ISO8601 UTC,
        "fingerprint":  sha1 hex of sorted (key, content-hash) pairs,
        "counts": {
          "today":      int,
          "week":       int,
          "month":      int,
          "fortnight":  int
        }
      }, ...
    ]
  }

NEW/UPDATED detection: content-hash comparison against the prior snapshot.
A ticket is flagged only when its bytes actually differ from the previous
run's stored hash. Manual saves, IDE rewrites, and other non-Jira touches
that move file mtime without changing bytes are filtered out.

First run after schema upgrade: builds the baseline snapshot; surfaces no
incremental changes (we have no prior state to diff against). Subsequent
runs surface only real content deltas.

Idempotent: re-running on unchanged content does not append a new entry.
The HTML itself is regenerated every run (rendered "now" timestamp moves).

Conventions: no third-party dependencies; standard library only; atomic writes
via tempfile + os.replace; .brain-state.json is read-only.
"""

import datetime as dt
import hashlib
import html as html_lib
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

# ----------------------------------------------------------------------------
# Paths and constants
# ----------------------------------------------------------------------------

REPO       = Path(__file__).resolve().parent.parent
STATE_FILE = REPO / '.brain-state.json'
RUNS_FILE  = REPO / 'runs.log.json'
RAW_DIR    = REPO / 'raw' / 'tickets'
OUT_HTML   = REPO / 'wiki' / 'training' / 'whats-new.html'

SYNC_INTERVAL_DAYS  = 1     # daily sync per ingest.py routine
BULK_DAY_THRESHOLD  = 500   # a calendar day with >= N modifications is treated as a bulk import
THEME_TOP_N         = 3
QUIET_FOOTER_MAX    = 2

NOW = dt.datetime.now(dt.timezone.utc)


# ----------------------------------------------------------------------------
# Frontmatter parsing
# ----------------------------------------------------------------------------

def parse_frontmatter(text):
    if not text.startswith('---'):
        return {}
    end = text.find('\n---', 3)
    if end < 0:
        return {}
    fm = {}
    for line in text[3:end].splitlines():
        m = re.match(r'^([a-zA-Z_]+):\s*(.*)$', line.strip())
        if not m:
            continue
        k, v = m.group(1), m.group(2).strip()
        if v.startswith('"') and v.endswith('"'):
            v = v[1:-1]
        elif v.startswith('[') and v.endswith(']'):
            try:
                v = json.loads(v.replace("'", '"'))
            except Exception:
                v = []
        elif v.lower() in ('true', 'false'):
            v = (v.lower() == 'true')
        elif v.isdigit():
            v = int(v)
        fm[k] = v
    return fm


# ----------------------------------------------------------------------------
# State + log readers / writers
# ----------------------------------------------------------------------------

def read_state():
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding='utf-8'))
    except Exception:
        return {}


def read_runs_log():
    """Read runs.log.json. Always returns v2-shaped dict with `snapshot` and `runs`.
    Auto-upgrades v1 logs (which had no snapshot) by returning an empty snapshot —
    forcing a clean baseline build on the next run."""
    empty = {'version': 2, 'snapshot': {}, 'runs': []}
    if not RUNS_FILE.exists():
        return empty
    try:
        data = json.loads(RUNS_FILE.read_text(encoding='utf-8'))
        if not isinstance(data, dict) or 'runs' not in data:
            return empty
        if 'snapshot' not in data or not isinstance(data['snapshot'], dict):
            data['snapshot'] = {}
        data['version'] = 2
        return data
    except Exception:
        return empty


def atomic_write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + '.', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except Exception:
            pass
        raise


# ----------------------------------------------------------------------------
# Ticket gathering (filesystem fallback)
# ----------------------------------------------------------------------------

def gather_tickets():
    rows = []
    for p in sorted(RAW_DIR.glob('*.md')):
        try:
            text = p.read_text(encoding='utf-8', errors='replace')
        except Exception:
            continue
        fm = parse_frontmatter(text)
        if not fm:
            continue
        st = p.stat()
        comps = fm.get('components', [])
        if not isinstance(comps, list):
            comps = []
        rows.append({
            'key':        fm.get('key', p.stem),
            'mtime':      dt.datetime.fromtimestamp(st.st_mtime, dt.timezone.utc),
            'ctime':      dt.datetime.fromtimestamp(st.st_ctime, dt.timezone.utc),
            'hash':       hashlib.sha1(text.encode('utf-8')).hexdigest(),
            'summary':    fm.get('summary', ''),
            'status':     fm.get('status', ''),
            'components': comps,
            'low_signal': bool(fm.get('low_signal', False)),
        })
    return rows


def build_snapshot(rows):
    """{key: content_hash} for the current corpus state."""
    return {r['key']: r['hash'] for r in rows}


# ----------------------------------------------------------------------------
# Bucketing
# ----------------------------------------------------------------------------

def bucket_rows(rows, prior_snapshot, baseline_mode):
    """Bucket tickets by mtime window, filtered by content-hash change.

    A row enters today/week/month buckets only when its content hash actually
    differs from the prior snapshot — otherwise it's a noisy mtime touch and we
    skip it. all30 and fortnight retain every row in the window (used for
    bulk-day detection and corpus-wide stats that don't depend on real change).

    baseline_mode: True on the first run after a schema upgrade, when we have no
    prior snapshot. We then surface no incremental changes — the run exists
    purely to record the baseline. Subsequent runs detect real deltas.
    """
    buckets = {
        'today': [], 'week': [], 'month': [],
        'fortnight': [], 'all30': []
    }
    for r in rows:
        delta = NOW - r['mtime']
        if delta <= dt.timedelta(days=14):
            buckets['fortnight'].append(r)
        if delta <= dt.timedelta(days=30):
            buckets['all30'].append(r)

        if baseline_mode:
            continue
        prior_hash = prior_snapshot.get(r['key'])
        if prior_hash == r['hash']:
            continue
        # Real change: either NEW (key absent from snapshot) or content differs.
        r['_kind'] = 'NEW' if prior_hash is None else 'UPDATED'
        if delta.total_seconds() < 86400:
            buckets['today'].append(r)
        elif delta <= dt.timedelta(days=7):
            buckets['week'].append(r)
        elif delta <= dt.timedelta(days=30):
            buckets['month'].append(r)
    return buckets


def detect_bulk_days(rows, threshold=BULK_DAY_THRESHOLD):
    counts = Counter(r['mtime'].date().isoformat() for r in rows)
    return {d for d, c in counts.items() if c >= threshold}


def status_to_kind(r, bulk_days):
    """Return the kind already attached by bucket_rows when filtering by content
    hash. Falls back to bulk-day membership only for rows that bypassed the
    snapshot filter (e.g. the bulk-import callout's per-row count)."""
    if r.get('_kind'):
        return r['_kind']
    if r['mtime'].date().isoformat() in bulk_days:
        return 'NEW'
    return 'UPDATED'


def compute_themes(fortnight_rows, top_n=THEME_TOP_N):
    counter = Counter()
    for r in fortnight_rows:
        if r.get('low_signal'):
            continue
        for c in r['components']:
            counter[c] += 1
    return counter.most_common(top_n)


def compute_quiet(all_rows, month_rows):
    all_comps = set()
    for r in all_rows:
        for c in r['components']:
            if c:
                all_comps.add(c)
    moved = set()
    for r in month_rows:
        for c in r['components']:
            if c:
                moved.add(c)
    return sorted(all_comps - moved)


def count_corpus_sprints():
    """Count distinct sprint names across all ticket frontmatter. Used in the
    self-explanation footer; computed once per render."""
    sprints = set()
    for p in RAW_DIR.glob('*.md'):
        try:
            text = p.read_text(encoding='utf-8', errors='replace')
        except Exception:
            continue
        end = text.find('\n---', 3)
        if end < 0:
            continue
        m = re.search(r'sprints:\s*(\[[^\]]*\])', text[3:end])
        if not m:
            continue
        try:
            for s in json.loads(m.group(1).replace("'", '"')):
                if s:
                    sprints.add(s)
        except Exception:
            pass
    return len(sprints)


def fingerprint_from_snapshot(snapshot):
    """Content fingerprint over the full corpus state — sha1 of sorted
    (key, hash) pairs. Stable across mtime noise; only changes when ticket
    bytes actually move."""
    sig = sorted(snapshot.items())
    return hashlib.sha1(json.dumps(sig).encode()).hexdigest()


def append_run_if_changed(runs_log, current_snapshot, buckets):
    fp = fingerprint_from_snapshot(current_snapshot)
    last = runs_log['runs'][-1] if runs_log['runs'] else None
    if last and last.get('fingerprint') == fp:
        return False
    runs_log['runs'].append({
        'ts':          NOW.isoformat(),
        'fingerprint': fp,
        'counts': {
            'today':     len(buckets['today']),
            'week':      len(buckets['week']),
            'month':     len(buckets['month']),
            'fortnight': len(buckets['fortnight']),
        },
    })
    # Trim to last 90 entries to keep file bounded
    runs_log['runs'] = runs_log['runs'][-90:]
    return True


# ----------------------------------------------------------------------------
# Concept-page slug helpers (for theme links)
# ----------------------------------------------------------------------------

def component_to_slug(name):
    """Map a Jira component name to its concept-page slug. Falls back to None
    when no concept page exists."""
    # Match the slug convention used by compile_wiki.py: replace non-alphanumerics with '-'.
    slug = re.sub(r'[^A-Za-z0-9]+', '-', name).strip('-')
    # Title-case slug for concept files (per REPO_STRUCTURE.md).
    candidate = REPO / 'wiki' / 'concepts' / f'{slug}.md'
    if candidate.exists():
        return f'../concepts/{slug}.html'
    return None


# ----------------------------------------------------------------------------
# HTML rendering
# ----------------------------------------------------------------------------

CSS = r"""
:root {
  --bg: #0f1419;
  --bg-2: #161c24;
  --bg-3: #1e2631;
  --ink: #e8eef5;
  --ink-dim: #9aa7b5;
  --ink-muted: #6b7785;
  --accent: #7dd3c0;
  --accent-2: #ffb86b;
  --ok: #95e1a3;
  --danger: #ff7e7e;
  --border: #2a3441;
  --radius: 10px;
}
[data-theme="light"] {
  --bg: #fafbfc; --bg-2: #ffffff; --bg-3: #f1f4f8;
  --ink: #1a2129; --ink-dim: #5a6876; --ink-muted: #8a96a4;
  --accent: #2c8a74; --accent-2: #c2671a;
  --ok: #2a8b3f; --danger: #c02a2a;
  --border: #dfe3e8;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font: 16px/1.55 -apple-system, "Segoe UI", system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
}
.wrap { max-width: 920px; margin: 0 auto; padding: 28px 48px 48px; }
header.top {
  display: flex; justify-content: space-between; align-items: baseline;
  padding-bottom: 12px; border-bottom: 1px solid var(--border); margin-bottom: 22px;
}
header.top .brand {
  font-size: 13px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--ink-dim);
}
header.top .brand b { color: var(--accent); font-weight: 600; }
button.theme {
  background: var(--bg-3); border: 1px solid var(--border); color: var(--ink);
  padding: 5px 12px; border-radius: 20px; cursor: pointer; font-size: 12px;
}
button.theme:hover { background: var(--bg-2); }

h1.lede {
  font-size: 26px; line-height: 1.15; letter-spacing: -0.018em;
  margin: 0 0 6px; font-weight: 600;
}
h1.lede .grad {
  background: linear-gradient(90deg, var(--accent), var(--accent-2));
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}

.banner {
  display: flex; gap: 26px; flex-wrap: wrap;
  padding: 14px 18px; margin: 18px 0 26px;
  background: var(--bg-2); border: 1px solid var(--border); border-radius: var(--radius);
  font-size: 13.5px;
}
.banner .item { display: flex; flex-direction: column; gap: 2px; }
.banner .item .l {
  font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.12em;
  color: var(--ink-dim); font-weight: 600;
}
.banner .item .v { color: var(--ink); font-variant-numeric: tabular-nums; }
.banner .item .v.accent { color: var(--accent); }

.bulk-callout {
  display: flex; gap: 14px; align-items: flex-start;
  padding: 14px 18px; margin-bottom: 26px;
  background: linear-gradient(135deg, rgba(125,211,192,0.10), rgba(255,184,107,0.06));
  border: 1px solid var(--border); border-left: 3px solid var(--accent);
  border-radius: var(--radius); font-size: 13.5px;
}
.bulk-callout .label {
  font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.12em;
  color: var(--accent); font-weight: 700; padding-top: 1px;
}
.bulk-callout .body { color: var(--ink); }
.bulk-callout .body b { color: var(--ink); }
.bulk-callout .body .when { color: var(--ink-dim); }

.section-h {
  font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase;
  color: var(--accent); margin: 28px 0 10px; font-weight: 600;
  display: flex; align-items: baseline; justify-content: space-between;
}
.section-h .ct { color: var(--ink-muted); font-size: 11px; letter-spacing: 0.08em; }

.empty {
  font-size: 13px; color: var(--ink-dim); padding: 12px 16px;
  background: var(--bg-2); border: 1px dashed var(--border); border-radius: var(--radius);
}

.cards { display: flex; flex-direction: column; gap: 8px; }
.card {
  display: grid; grid-template-columns: auto 1fr auto;
  gap: 14px; align-items: baseline;
  padding: 12px 16px; background: var(--bg-2); border: 1px solid var(--border);
  border-radius: var(--radius); font-size: 14px;
  transition: border-color 0.15s;
}
.card:hover { border-color: var(--accent); }
.card .badge {
  font-family: "SF Mono", Menlo, Consolas, monospace;
  font-size: 10.5px; letter-spacing: 0.06em; padding: 2px 7px;
  border-radius: 4px; font-weight: 600;
}
.card .badge.NEW { background: rgba(149,225,163,0.14); color: var(--ok); }
.card .badge.UPDATED { background: rgba(255,184,107,0.14); color: var(--accent-2); }
.card .key {
  font-family: "SF Mono", Menlo, Consolas, monospace;
  font-size: 12.5px; color: var(--accent); text-decoration: none;
}
.card .key:hover { text-decoration: underline; }
.card .summary { color: var(--ink); line-height: 1.45; min-width: 0; word-break: break-word; }
.card .pills { display: flex; gap: 4px; flex-wrap: wrap; justify-content: flex-end; }
.pill {
  font-size: 11px; padding: 2px 8px; border-radius: 100px;
  background: var(--bg-3); color: var(--ink-dim); border: 1px solid var(--border);
  white-space: nowrap;
}

.day-rollup {
  display: grid; grid-template-columns: 130px 1fr;
  gap: 14px; padding: 8px 14px; align-items: baseline;
  border-bottom: 1px solid var(--border); font-size: 13.5px;
}
.day-rollup:last-child { border-bottom: none; }
.day-rollup .day { color: var(--ink); font-weight: 500; }
.day-rollup .day .date { color: var(--ink-dim); font-size: 12px; margin-left: 6px; font-variant-numeric: tabular-nums; }
.day-rollup .meta { display: flex; gap: 6px; flex-wrap: wrap; align-items: baseline; }
.day-rollup .counts { color: var(--ink); font-variant-numeric: tabular-nums; }
.day-rollup .counts .n { color: var(--ok); }
.day-rollup .counts .u { color: var(--accent-2); }
.day-rollup .ds { color: var(--ink-muted); margin: 0 4px; }

.rollup-block {
  background: var(--bg-2); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 4px 0; overflow: hidden;
}

.themes { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.theme {
  padding: 16px 18px; background: var(--bg-2); border: 1px solid var(--border);
  border-radius: var(--radius); transition: border-color 0.15s, transform 0.15s;
}
.theme:hover { border-color: var(--accent); transform: translateY(-1px); }
.theme .rank {
  font-family: "SF Mono", Menlo, Consolas, monospace;
  font-size: 11px; color: var(--accent); letter-spacing: 0.08em; font-weight: 600;
}
.theme .name { font-size: 15px; color: var(--ink); font-weight: 600; margin-top: 4px; }
.theme .name a { color: var(--ink); text-decoration: none; border-bottom: 1px dashed var(--border); }
.theme .name a:hover { color: var(--accent); border-color: var(--accent); }
.theme .ct {
  margin-top: 8px; font-size: 12.5px; color: var(--ink-dim); font-variant-numeric: tabular-nums;
}
.theme .ct b { color: var(--ink); font-weight: 600; }

.quiet-foot {
  margin-top: 32px; padding: 12px 16px;
  font-size: 12.5px; color: var(--ink-dim);
  border-top: 1px solid var(--border); padding-top: 18px;
}
.quiet-foot b {
  color: var(--ink); text-transform: uppercase; letter-spacing: 0.12em;
  font-size: 10.5px; font-weight: 600; display: block; margin-bottom: 4px;
}

@media (max-width: 760px) {
  .wrap { padding: 22px 18px; }
  .themes { grid-template-columns: 1fr; }
  .card { grid-template-columns: auto 1fr; }
  .card .pills { grid-column: 1 / -1; justify-content: flex-start; }
  .day-rollup { grid-template-columns: 1fr; gap: 4px; padding-bottom: 12px; }
}
"""

THEME_TOGGLE_JS = r"""
(function() {
  var KEY = 'whats-new-theme';
  var btn = document.getElementById('theme-btn');
  if (!btn) return;
  var saved = localStorage.getItem(KEY);
  if (saved) document.body.dataset.theme = saved;
  function setLabel() { btn.textContent = document.body.dataset.theme === 'dark' ? 'light' : 'dark'; }
  setLabel();
  btn.addEventListener('click', function() {
    document.body.dataset.theme = document.body.dataset.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem(KEY, document.body.dataset.theme);
    setLabel();
  });
})();
"""


def esc(s):
    return html_lib.escape(str(s))


def fmt_date(d):
    return d.strftime('%a %b %-d') if hasattr(d, 'strftime') and os.name != 'nt' else d.strftime('%a %b %d').replace(' 0', ' ')


def fmt_short(d):
    return d.strftime('%b %d').replace(' 0', ' ')


def fmt_iso(t):
    return t.strftime('%Y-%m-%d %H:%M UTC')


def render_card(r, bulk_days):
    kind = status_to_kind(r, bulk_days)
    pills_html = ''.join(f'<span class="pill">{esc(c)}</span>' for c in r['components'][:3] if c)
    summary = r['summary'] or '(no summary)'
    return (
        f'<div class="card">'
        f'<span class="badge {kind}">{kind}</span>'
        f'<div class="summary"><a class="key" href="../../raw/tickets/{esc(r["key"])}.html">{esc(r["key"])}</a> &nbsp; {esc(summary)}</div>'
        f'<div class="pills">{pills_html}</div>'
        f'</div>'
    )


def render_today(today_rows, bulk_days):
    today_iso = NOW.date().isoformat()
    if today_iso in bulk_days:
        return (
            '<div class="empty">Today is a bulk-import day; see the callout above. '
            f'{len(today_rows):,} tickets touched.</div>'
        )
    if not today_rows:
        return '<div class="empty">No tickets changed today.</div>'
    cards = ''.join(render_card(r, bulk_days) for r in sorted(today_rows, key=lambda r: r['mtime'], reverse=True))
    return f'<div class="cards">{cards}</div>'


def render_week_rollup(week_rows, bulk_days):
    by_day = defaultdict(list)
    for r in week_rows:
        by_day[r['mtime'].date().isoformat()].append(r)
    if not by_day:
        return '<div class="empty">No tickets changed in the last 7 days (excluding today).</div>'
    rows_html = []
    for day_iso in sorted(by_day.keys(), reverse=True):
        rows_for_day = by_day[day_iso]
        if day_iso in bulk_days:
            counts = f'<span class="counts"><b>{len(rows_for_day):,}</b> tickets · bulk import</span>'
            comps_html = ''
        else:
            new_ct = sum(1 for r in rows_for_day if status_to_kind(r, bulk_days) == 'NEW')
            upd_ct = sum(1 for r in rows_for_day if status_to_kind(r, bulk_days) == 'UPDATED')
            counts = f'<span class="counts"><span class="n">{new_ct} new</span><span class="ds">·</span><span class="u">{upd_ct} updated</span></span>'
            comp_counter = Counter()
            for r in rows_for_day:
                for c in r['components']:
                    if c:
                        comp_counter[c] += 1
            comps_html = ' '.join(f'<span class="pill">{esc(c)}</span>' for c, _ in comp_counter.most_common(4))
        day_dt = dt.date.fromisoformat(day_iso)
        weekday = day_dt.strftime('%A')
        date_str = fmt_short(day_dt)
        rows_html.append(
            f'<div class="day-rollup">'
            f'<div class="day">{weekday}<span class="date">{date_str}</span></div>'
            f'<div class="meta">{counts}{("&nbsp;" + comps_html) if comps_html else ""}</div>'
            f'</div>'
        )
    return f'<div class="rollup-block">{"".join(rows_html)}</div>'


def render_month_rollup(month_rows, bulk_days):
    by_week = defaultdict(list)
    for r in month_rows:
        d = r['mtime'].date()
        # ISO calendar week
        iso = d.isocalendar()
        wk_key = f'{iso.year}-W{iso.week:02d}'
        by_week[wk_key].append((d, r))
    if not by_week:
        return '<div class="empty">No tickets changed 7–30 days ago.</div>'
    rows_html = []
    for wk in sorted(by_week.keys(), reverse=True):
        items = by_week[wk]
        days = sorted({i[0].isoformat() for i in items})
        any_bulk = any(d in bulk_days for d in days)
        if any_bulk:
            label_counts = f'<span class="counts"><b>{len(items):,}</b> tickets · bulk import</span>'
        else:
            new_ct = sum(1 for _, r in items if status_to_kind(r, bulk_days) == 'NEW')
            upd_ct = sum(1 for _, r in items if status_to_kind(r, bulk_days) == 'UPDATED')
            label_counts = f'<span class="counts"><span class="n">{new_ct} new</span><span class="ds">·</span><span class="u">{upd_ct} updated</span></span>'
        first_day = dt.date.fromisoformat(days[0])
        last_day = dt.date.fromisoformat(days[-1])
        if first_day == last_day:
            label_day = fmt_short(first_day)
        else:
            label_day = f'{fmt_short(first_day)} – {fmt_short(last_day)}'
        rows_html.append(
            f'<div class="day-rollup">'
            f'<div class="day">Week {wk[-2:].lstrip("0") or "0"}<span class="date">{label_day}</span></div>'
            f'<div class="meta">{label_counts}</div>'
            f'</div>'
        )
    return f'<div class="rollup-block">{"".join(rows_html)}</div>'


def render_themes(themes, has_bulk):
    if not themes:
        return '<div class="empty">No theme data available.</div>'
    note = ''
    if has_bulk:
        note = '<div style="font-size:12.5px;color:var(--ink-dim);margin:0 0 10px;">Includes the bulk import — these are also the largest modules in the corpus. As incremental syncs accumulate, this section will reflect 14-day movement.</div>'
    cells = []
    for i, (comp, ct) in enumerate(themes, 1):
        slug_url = component_to_slug(comp)
        name_html = f'<a href="{slug_url}">{esc(comp)}</a>' if slug_url else esc(comp)
        cells.append(
            f'<div class="theme">'
            f'<div class="rank">#{i}</div>'
            f'<div class="name">{name_html}</div>'
            f'<div class="ct"><b>{ct:,}</b> ticket{"s" if ct != 1 else ""} touched in last 14 days</div>'
            f'</div>'
        )
    return note + f'<div class="themes">{"".join(cells)}</div>'


def render_quiet(quiet_components):
    if not quiet_components:
        return (
            '<div class="quiet-foot">'
            '<b>Quiet modules</b>'
            'Every module had at least one ticket modified in the last 30 days — typical of a freshly synced corpus.'
            '</div>'
        )
    listed = ', '.join(esc(c) for c in quiet_components[:QUIET_FOOTER_MAX])
    rest = len(quiet_components) - QUIET_FOOTER_MAX
    rest_html = f' (and {rest} more)' if rest > 0 else ''
    return (
        '<div class="quiet-foot">'
        '<b>Quiet modules</b>'
        f'No movement in the last 30 days: {listed}{rest_html}. Equally informative.'
        '</div>'
    )


def render_html(rows, buckets, bulk_days, themes, quiet, last_sync_label, baseline_mode=False):
    today_iso = NOW.date().isoformat()
    next_sync = (NOW + dt.timedelta(days=SYNC_INTERVAL_DAYS)).strftime('%Y-%m-%d')
    has_bulk = bool(bulk_days)
    bulk_html = ''
    if has_bulk:
        sorted_bulk_days = sorted(bulk_days, reverse=True)
        primary = sorted_bulk_days[0]
        primary_dt = dt.date.fromisoformat(primary)
        bulk_count = sum(1 for r in rows if r['mtime'].date().isoformat() == primary)
        bulk_html = (
            '<div class="bulk-callout">'
            '<div class="label">Bulk import</div>'
            f'<div class="body"><b>{bulk_count:,} tickets ingested</b> on <span class="when">{primary_dt.strftime("%A, %B %d, %Y")}</span>. '
            'This is the initial sync of the existing Jira corpus — every ticket got a markdown file. '
            'Subsequent syncs will show only what changed in Jira since then.</div>'
            '</div>'
        )
    if baseline_mode:
        baseline_note = (
            '<div class="empty">No prior content snapshot to compare against — '
            "this run records the baseline. From the next run forward, only tickets "
            'whose bytes actually change will surface here.</div>'
        )
        today_html = baseline_note
        week_html  = baseline_note
        month_html = baseline_note
    else:
        today_html  = render_today(buckets['today'], bulk_days)
        week_html   = render_week_rollup(buckets['week'], bulk_days)
        month_html  = render_month_rollup(buckets['month'], bulk_days)
    themes_html = render_themes(themes, has_bulk)
    quiet_html  = render_quiet(quiet)
    total30 = len(buckets['all30'])
    total_corpus = len(rows)
    sprint_count = count_corpus_sprints()
    today_human = NOW.strftime('%Y-%m-%d')

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>What's New — Perseus / NXT</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>{CSS}</style>
</head>
<body data-theme="dark">
<div class="wrap">
<header class="top">
  <div class="brand">Perseus / NXT · <b>What's New</b></div>
  <button class="theme" id="theme-btn">light</button>
</header>

<h1 class="lede">The wiki <span class="grad">refreshes</span> when Jira does.</h1>
<p style="margin:0;font-size:14.5px;color:var(--ink-dim);">Generated from <code style="font-family:'SF Mono',Menlo,Consolas,monospace;font-size:12.5px;background:var(--bg-3);padding:1px 6px;border-radius:4px;color:var(--ink);">.brain-state.json</code> and ticket-file mtimes. Re-run <code style="font-family:'SF Mono',Menlo,Consolas,monospace;font-size:12.5px;background:var(--bg-3);padding:1px 6px;border-radius:4px;color:var(--ink);">scripts/render_changelog.py</code> any time.</p>

<div class="banner">
  <div class="item"><span class="l">Last sync</span><span class="v accent">{esc(last_sync_label)}</span></div>
  <div class="item"><span class="l">Next sync</span><span class="v">{esc(next_sync)}</span></div>
  <div class="item"><span class="l">Tickets in last 30d</span><span class="v">{total30:,}</span></div>
  <div class="item"><span class="l">Tickets today</span><span class="v">{len(buckets['today']):,}</span></div>
  <div class="item"><span class="l">Generated</span><span class="v">{esc(fmt_iso(NOW))}</span></div>
</div>

{bulk_html}

<div class="section-h"><span>Today</span><span class="ct">last 24 hours</span></div>
{today_html}

<div class="section-h"><span>This week</span><span class="ct">last 7 days, by day</span></div>
{week_html}

<div class="section-h"><span>This month</span><span class="ct">8–30 days ago, by week</span></div>
{month_html}

<div class="section-h"><span>Themes this fortnight</span><span class="ct">top {THEME_TOP_N} components by ticket movement, last 14 days</span></div>
{themes_html}

{quiet_html}

<div style="margin-top:18px;padding-top:14px;border-top:1px solid var(--border);font-style:italic;color:var(--ink-muted);font-size:12px;line-height:1.55;">
  Compiled from {total_corpus:,} tickets across {sprint_count} sprints. Last refreshed {today_human}. Source tickets are listed in <a href="../../tickets.html" style="color:var(--accent);text-decoration:none;border-bottom:1px dashed var(--border);">the ticket index</a>.
</div>

</div>
<script>{THEME_TOGGLE_JS}</script>
</body>
</html>
"""


# ----------------------------------------------------------------------------
# Last-sync label resolver
# ----------------------------------------------------------------------------

def last_sync_label(state, runs_log, rows):
    # Prefer a real prior_runs entry timestamp when populated.
    pr = state.get('prior_runs') or []
    if pr and isinstance(pr[-1], dict) and pr[-1].get('ts'):
        try:
            t = dt.datetime.fromisoformat(pr[-1]['ts'].replace('Z', '+00:00'))
            return t.strftime('%Y-%m-%d %H:%M UTC')
        except Exception:
            pass
    # Otherwise prefer the most recent ticket mtime.
    if rows:
        latest = max(r['mtime'] for r in rows)
        return latest.strftime('%Y-%m-%d %H:%M UTC')
    # Otherwise the prior run we logged.
    if runs_log['runs']:
        try:
            t = dt.datetime.fromisoformat(runs_log['runs'][-1]['ts'].replace('Z', '+00:00'))
            return t.strftime('%Y-%m-%d %H:%M UTC')
        except Exception:
            pass
    return 'never'


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main():
    state    = read_state()
    runs_log = read_runs_log()

    rows = gather_tickets()
    current_snapshot = build_snapshot(rows)
    prior_snapshot = runs_log.get('snapshot') or {}
    baseline_mode = not prior_snapshot  # first run after schema upgrade has no baseline

    buckets = bucket_rows(rows, prior_snapshot, baseline_mode)
    bulk_days = detect_bulk_days(rows)
    themes = compute_themes(buckets['fortnight'])
    quiet  = compute_quiet(rows, buckets['all30'])

    appended = append_run_if_changed(runs_log, current_snapshot, buckets)
    runs_log['snapshot'] = current_snapshot   # always persist the freshest snapshot
    if appended:
        atomic_write(RUNS_FILE, json.dumps(runs_log, indent=2) + '\n')

    last_sync = last_sync_label(state, runs_log, rows)
    html_out = render_html(rows, buckets, bulk_days, themes, quiet, last_sync, baseline_mode)
    atomic_write(OUT_HTML, html_out)

    print(f'render_changelog: wrote {OUT_HTML} ({len(html_out):,} bytes)')
    print(f'  rows={len(rows):,}  baseline_mode={baseline_mode}')
    print(f'  today={len(buckets["today"])}  week={len(buckets["week"])}  '
          f'month={len(buckets["month"])}  fortnight={len(buckets["fortnight"])}')
    print(f'  bulk_days={sorted(bulk_days)}  themes={[c for c,_ in themes]}  quiet={len(quiet)}')
    print(f'  runs_log: appended={appended}, total_entries={len(runs_log["runs"])}, snapshot_size={len(current_snapshot)}')


if __name__ == '__main__':
    main()
