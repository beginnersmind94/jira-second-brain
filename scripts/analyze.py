"""Step 5 helper: analyze ticket corpus to find concepts/workflows/entities."""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
TICKETS = VAULT / "raw" / "tickets"

STOPWORDS = set("""
a an and are as at be by for from has have if in is it its of on or that the
this to was were will with not but all any can you your our we they them he
she i me my do does done new old add remove update fix bug issue error story
task epic feature please need needs should would could make made using use
user users when where which who how what why via such per into out over under
re:
""".split())

def frontmatter(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return {}, text
    fm_text = m.group(1)
    meta = {}
    for line in fm_text.split("\n"):
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    return meta, text[m.end():]

def parse_list(v):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1]
        if not inner.strip():
            return []
        parts = re.findall(r'"([^"]*)"', inner)
        return parts
    return []

def summary_tokens(s):
    s = s.lower()
    s = re.sub(r"[^\w\s/-]", " ", s)
    toks = [t for t in s.split() if t and t not in STOPWORDS and not t.isdigit() and len(t) > 2]
    return toks

def main():
    component_counts = Counter()
    component_tickets = defaultdict(list)
    sprint_counts = Counter()
    sprint_tickets = defaultdict(list)
    status_counts = Counter()
    unigrams = Counter()
    bigrams = Counter()
    trigrams = Counter()
    phrase_tickets = defaultdict(list)

    all_tickets = []
    for p in TICKETS.glob("*.md"):
        meta, _body = frontmatter(p)
        key = meta.get("key", p.stem)
        if meta.get("low_signal", "false") == "true":
            continue
        summary = meta.get("summary", "").strip('"')
        status = meta.get("status", "").strip('"')
        comps = parse_list(meta.get("components", "[]"))
        sprints = parse_list(meta.get("sprints", "[]"))

        status_counts[status] += 1
        for c in comps:
            component_counts[c] += 1
            component_tickets[c].append((key, summary))
        for s in sprints:
            sprint_counts[s] += 1
            sprint_tickets[s].append((key, summary))

        toks = summary_tokens(summary)
        for t in toks:
            unigrams[t] += 1
        for i in range(len(toks) - 1):
            bi = " ".join(toks[i:i+2])
            bigrams[bi] += 1
            phrase_tickets[bi].append((key, summary))
        for i in range(len(toks) - 2):
            tri = " ".join(toks[i:i+3])
            trigrams[tri] += 1
            phrase_tickets[tri].append((key, summary))

        all_tickets.append({"key": key, "summary": summary, "components": comps, "sprints": sprints})

    out = {
        "total_high_signal": len(all_tickets),
        "top_components": component_counts.most_common(40),
        "top_sprints": sprint_counts.most_common(40),
        "status_counts": status_counts.most_common(),
        "top_unigrams": unigrams.most_common(60),
        "top_bigrams": bigrams.most_common(80),
        "top_trigrams": trigrams.most_common(60),
    }

    # Save phrase->tickets and component->tickets for later use
    with open(VAULT / "scripts" / "analysis_summary.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, default=str)

    with open(VAULT / "scripts" / "component_tickets.json", "w", encoding="utf-8") as f:
        json.dump({c: v for c, v in component_tickets.items()}, f, indent=2, default=str)

    with open(VAULT / "scripts" / "phrase_tickets.json", "w", encoding="utf-8") as f:
        top_phrases = set([p for p, _ in bigrams.most_common(80)] + [p for p, _ in trigrams.most_common(60)])
        json.dump({p: phrase_tickets[p] for p in top_phrases}, f, indent=2, default=str)

    with open(VAULT / "scripts" / "sprint_tickets.json", "w", encoding="utf-8") as f:
        json.dump({s: v for s, v in sprint_tickets.items()}, f, indent=2, default=str)

    print(json.dumps(out, indent=2, default=str)[:4000])

if __name__ == "__main__":
    main()
