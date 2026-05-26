"""Crawl the built wiki and report broken links, orphans, and connectivity gaps."""
from __future__ import annotations

import os
import re
import sys
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urldefrag

SITE_ROOT = Path(__file__).parent / "output" / "site"
SEEDS = [
    SITE_ROOT / "index.html",
    SITE_ROOT / "concepts.html",
    SITE_ROOT / "workflows.html",
    SITE_ROOT / "entities.html",
    SITE_ROOT / "tickets.html",
]


class LinkExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for k, v in attrs:
            if k == "href" and v:
                self.links.append(v)


def extract_links(html_path: Path) -> list[str]:
    parser = LinkExtractor()
    parser.feed(html_path.read_text(encoding="utf-8", errors="ignore"))
    return parser.links


def resolve(from_file: Path, href: str) -> Path | None:
    href = unquote(href)
    href, _ = urldefrag(href)
    if not href:
        return None
    if re.match(r"^(https?:|mailto:|javascript:|tel:)", href, re.I):
        return None
    return (from_file.parent / href).resolve()


def main() -> int:
    visited: set[Path] = set()
    queue: list[Path] = [p.resolve() for p in SEEDS]
    broken: list[tuple[Path, str, Path]] = []
    inbound: dict[Path, set[Path]] = defaultdict(set)
    outbound_count: dict[Path, int] = {}

    site_root_resolved = SITE_ROOT.resolve()

    while queue:
        page = queue.pop(0)
        if page in visited:
            continue
        if not page.exists():
            continue
        visited.add(page)

        links = extract_links(page)
        outbound_count[page] = 0
        for href in links:
            target = resolve(page, href)
            if target is None:
                continue
            try:
                target.relative_to(site_root_resolved)
            except ValueError:
                continue
            outbound_count[page] += 1
            if not target.exists():
                broken.append((page, href, target))
                continue
            inbound[target].add(page)
            if target.suffix.lower() == ".html" and target not in visited:
                queue.append(target)

    # All html files actually present under the site
    all_html = {p.resolve() for p in site_root_resolved.rglob("*.html")}
    # We'll focus orphan detection on wiki/ pages (excluding raw/tickets which is intentionally large)
    wiki_html = {p for p in all_html if "wiki" in p.parts and "raw" not in p.parts}
    orphans = sorted(p for p in wiki_html if p not in inbound and p not in {s.resolve() for s in SEEDS})

    rel = lambda p: str(p.relative_to(site_root_resolved)).replace("\\", "/")

    print(f"Crawled pages: {len(visited)}")
    print(f"Total HTML files under site/: {len(all_html)}")
    print(f"Wiki pages (excluding raw/tickets): {len(wiki_html)}")
    print()

    if broken:
        print(f"BROKEN LINKS ({len(broken)}):")
        for from_path, href, target in broken[:50]:
            print(f"  {rel(from_path)}  ->  {href}")
        if len(broken) > 50:
            print(f"  ... and {len(broken) - 50} more")
    else:
        print("BROKEN LINKS: none")
    print()

    if orphans:
        print(f"ORPHAN WIKI PAGES (no inbound link from crawl) ({len(orphans)}):")
        for o in orphans:
            print(f"  {rel(o)}")
    else:
        print("ORPHAN WIKI PAGES: none")
    print()

    # Connectivity per wiki page: inbound count
    print("INBOUND-LINK COUNT per wiki page (lowest first):")
    counts = sorted(
        ((p, len(inbound.get(p, set()))) for p in wiki_html),
        key=lambda x: (x[1], rel(x[0])),
    )
    for p, c in counts[:15]:
        print(f"  {c:3d}  {rel(p)}")
    print("  ...")
    for p, c in counts[-5:]:
        print(f"  {c:3d}  {rel(p)}")

    return 1 if broken or orphans else 0


if __name__ == "__main__":
    sys.exit(main())
