"""qr_store.py — QR code generation + stub scan analytics for PLT-2.

Provides:
  gen_qr_svg(url, size)   — deterministic stub SVG QR (not scannable; demo only)
  record_qr_scan(url)     — append a scan event to data/qr-analytics.jsonl
  get_analytics()         — aggregate scan counts from the JSONL log

[PLT-2-TTS] Production: replace gen_qr_svg with a real QR library (qrcode/segno)
and replace the JSONL stub with a proper scan-event pipeline.
"""
from __future__ import annotations

import base64
import json
import time
from pathlib import Path

_DATA_DIR    = Path(__file__).resolve().parent / "data"
_ANALYTICS   = _DATA_DIR / "qr-analytics.jsonl"


def gen_qr_svg(url: str, size: int = 120) -> str:
    """Return a stub SVG QR-code as a data:image/svg+xml;base64,... URI.

    The SVG pattern is deterministic for the same URL — same URL, same visual.
    Not scannable; for demo layout and print preview only.
    [PLT-2-TTS] Replace with a real QR encoder for production.
    """
    cells   = 10
    cell_px = max(1, size // cells)

    rects = []
    for row in range(cells):
        for col in range(cells):
            char_idx = (row * cells + col) % max(1, len(url))
            seed = ord(url[char_idx]) + row + col
            if seed % 3 != 0:
                x = col * cell_px
                y = row * cell_px
                rects.append(f'<rect x="{x}" y="{y}" width="{cell_px}" height="{cell_px}" fill="#111"/>')

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}">'
        f'<rect width="{size}" height="{size}" fill="#fff"/>'
        + "".join(rects)
        + "</svg>"
    )
    encoded = base64.b64encode(svg.encode()).decode()
    return f"data:image/svg+xml;base64,{encoded}"


def record_qr_scan(url: str) -> None:
    """Append a scan event to the analytics log (stub — write-only for now)."""
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    entry = json.dumps({"url": url, "scanned_at": time.strftime("%Y-%m-%dT%H:%M:%S")})
    with _ANALYTICS.open("a", encoding="utf-8") as fh:
        fh.write(entry + "\n")


def get_analytics() -> list[dict]:
    """Return [{url, count}] sorted by count descending.

    Returns an empty list if no scan data exists.
    """
    if not _ANALYTICS.exists():
        return []

    counts: dict[str, int] = {}
    try:
        for line in _ANALYTICS.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            u = entry.get("url", "")
            counts[u] = counts.get(u, 0) + 1
    except (json.JSONDecodeError, OSError):
        return []

    return sorted(
        [{"url": u, "count": c} for u, c in counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )
