"""Generate workflow.jpg — a clean workflow diagram for the Jira→guide POC.

Visual style mirrors the reference Query Agent diagram: dashed group boundaries,
rounded filled tiles, numbered arrows with white-pill labels.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

OUT = Path(__file__).resolve().parents[1] / "workflow.jpg"

# Palette
INK = "#1f2933"
MUTED = "#5b6470"
ORANGE_FILL = "#fbe4cf"
ORANGE_EDGE = "#d27c3a"
ORANGE_INK = "#9a4a14"
GREEN_FILL = "#d2efd6"
GREEN_EDGE = "#5da06a"
BEIGE_FILL = "#e9e1d3"
BEIGE_EDGE = "#a09786"
SCRATCH_FILL = "#f5efe4"
GROUP_EDGE = "#b9c0c9"

# Canvas (wider than tall, matches reference aspect)
W, H = 100.0, 75.0
fig, ax = plt.subplots(figsize=(16, 12))
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor("#ffffff")


def group_box(x, y, w, h, title, subtitle):
    rect = mpatches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.6,rounding_size=1.2",
        linewidth=1.4, edgecolor=GROUP_EDGE, facecolor="none", linestyle=(0, (5, 4)),
    )
    ax.add_patch(rect)
    ax.text(x + 1.8, y + h - 1.5, title, fontsize=15, fontweight="bold", color=INK, va="top", ha="left")
    ax.text(x + 1.8, y + h - 4.0, subtitle, fontsize=10, color=MUTED, va="top", ha="left", style="italic")


def tile(x, y, w, h, label, sublabel, fill, edge, text_color=INK, title_size=12, sub_size=9, weight="bold"):
    rect = mpatches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.3,rounding_size=1.0",
        linewidth=1.8, edgecolor=edge, facecolor=fill,
    )
    ax.add_patch(rect)
    if sublabel:
        ax.text(x + w / 2, y + h / 2 + 1.3, label, fontsize=title_size, fontweight=weight,
                color=text_color, ha="center", va="center")
        ax.text(x + w / 2, y + h / 2 - 1.6, sublabel, fontsize=sub_size, color=text_color, ha="center", va="center")
    else:
        ax.text(x + w / 2, y + h / 2, label, fontsize=title_size, fontweight=weight,
                color=text_color, ha="center", va="center")


def arrow(x1, y1, x2, y2, label=None, dx=0, dy=0, curve=0.0):
    style = "arc3,rad=" + str(curve) if curve else "arc3"
    a = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>", mutation_scale=18, linewidth=1.6, color=MUTED,
        connectionstyle=style, shrinkA=4, shrinkB=4,
    )
    ax.add_patch(a)
    if label:
        # Place label near midpoint (offset for curved arrows so it sits in clear space)
        mx, my = (x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy
        ax.text(
            mx, my, label, fontsize=10.5, color=INK, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor="none"),
        )


# ──────────────────── TOP: Sources ────────────────────
group_box(4, 56, W - 8, 17, "Sources", "What the system reads in")
tile(15, 60, 28, 9, "Jira CSV", "Module · RN · AC · Resolution", GREEN_FILL, GREEN_EDGE,
     title_size=12.5, sub_size=9.5)
tile(57, 60, 28, 9, "Source guide PDF", "User-uploaded, one at a time", GREEN_FILL, GREEN_EDGE,
     title_size=12.5, sub_size=9.5)

# ──────────────────── MIDDLE: User · Backend · Output ────────────────────
# Sized so arrows between them are short and clear.
user_x, user_y, user_w, user_h = 4, 31, 16, 14
out_x, out_y, out_w, out_h = 80, 31, 16, 14
backend_x, backend_y, backend_w, backend_h = 30, 27, 44, 22

# Backend tile (central workhorse)
rect = mpatches.FancyBboxPatch(
    (backend_x, backend_y), backend_w, backend_h,
    boxstyle="round,pad=0.4,rounding_size=1.2",
    linewidth=2.2, edgecolor=ORANGE_EDGE, facecolor=ORANGE_FILL,
)
ax.add_patch(rect)
ax.text(backend_x + backend_w / 2, backend_y + backend_h - 2.4, "Flask backend + Haiku",
        fontsize=14, fontweight="bold", color=ORANGE_INK, ha="center", va="top")
ax.text(backend_x + backend_w / 2, backend_y + backend_h - 4.7, "(claude -p --model haiku)",
        fontsize=9, color=ORANGE_INK, ha="center", va="top", style="italic")
steps = [
    "extract PDF → markdown (pypdf)",
    "filter CSV by module",
    "keyword pre-filter vs guide tokens",
    "prompt LLM → structured JSON edits",
    "apply approved edits → render PDF",
]
for i, s in enumerate(steps):
    ax.text(backend_x + 2.2, backend_y + backend_h - 7.4 - i * 2.4, "·  " + s,
            fontsize=10.5, color=ORANGE_INK, va="top", ha="left")

# User tile (left)
tile(user_x, user_y, user_w, user_h, "User", "drops PDF\npicks module\nreviews edits",
     BEIGE_FILL, BEIGE_EDGE, title_size=13, sub_size=9.5)

# Output tile (right)
tile(out_x, out_y, out_w, out_h, "Output", "modified PDF\nready to download",
     BEIGE_FILL, BEIGE_EDGE, title_size=13, sub_size=9.5)

# ──────────────────── BOTTOM: Per-job scratch ────────────────────
group_box(4, 3, W - 8, 18, "Per-job scratch (app/jobs/<id>/)",
          "Inputs, intermediates, and outputs persisted on disk for debug + reuse")
artifacts = ["in.pdf", "in.md", "tickets.json", "prompt.txt", "llm_response.txt",
             "proposals.json", "decisions.json", "out.md", "out.pdf"]
tw, th, gap = 9.4, 4.2, 0.9
row_y = [11.8, 6.4]
for i, name in enumerate(artifacts):
    col = i % 5
    row = i // 5
    x = 8 + col * (tw + gap)
    y = row_y[row]
    tile(x, y, tw, th, name, "", SCRATCH_FILL, BEIGE_EDGE, title_size=10.5, weight="bold")

# ──────────────────── ARROWS ────────────────────

# 1. User → Backend (drops PDF, picks module) — top edge of user, top edge of backend
arrow(user_x + user_w, user_y + user_h - 3,
      backend_x, backend_y + backend_h - 4,
      "1. drops PDF + module", dx=0.5, dy=2.6, curve=-0.18)

# 2. PDF source → Backend
arrow(71, 60, 60, 49, "2. PDF in", dx=3.5, dy=2)

# 3. CSV source → Backend
arrow(29, 60, 41, 49, "3. CSV in", dx=-3.5, dy=2)

# 4. Backend → User (proposed edits)
arrow(backend_x, backend_y + 8,
      user_x + user_w, user_y + 8,
      "4. proposed edits", dx=0, dy=2.8, curve=0.18)

# 5. User → Backend (decisions / approve / reject)
arrow(user_x + user_w, user_y + 3,
      backend_x, backend_y + 3,
      "5. approve / reject", dx=0, dy=-2.8, curve=-0.18)

# 6. Backend → Output (rendered PDF)
arrow(backend_x + backend_w, backend_y + backend_h / 2,
      out_x, out_y + out_h / 2,
      "6. rendered PDF", dx=0, dy=2.4)

# Backend → scratch (writes artifacts) — vertical down
arrow(backend_x + backend_w / 2, backend_y,
      backend_x + backend_w / 2, 21,
      "writes artifacts", dx=8.5, dy=0)


# Save
plt.savefig(str(OUT), dpi=130, bbox_inches="tight", facecolor="white", format="jpg")
print(f"wrote {OUT}  ({OUT.stat().st_size} bytes)")
print(f"file:// URL: {OUT.as_uri()}")
