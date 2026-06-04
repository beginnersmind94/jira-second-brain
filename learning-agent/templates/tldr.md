# Template: TLDR one-pager

You are writing the TLDR one-pager for the `{{module}}` module, based on the training transcript at `{{transcript_path}}` and the verified Jira evidence collected in Tasks 1–3.

## Goal
A staff member can see every feature of the module at a glance. Scan speed, not comprehension. Completeness matters precisely *because* omission implies the feature doesn't exist — if it's a real module feature, it must appear here, even if only as a name.

## Selection
The **top 10–12 most important features by priority** — judged by Jira priority, Release Notes visibility (external-facing features matter more), and transcript emphasis. One sentence each. This is a one-glance scan card, **NOT an exhaustive ticket export**: a module may have hundreds of tickets, but you still pick only the most important ~12. Lower-priority features are omitted — their absence on a one-pager is acceptable and expected. If a feature is too complex for one sentence, compress, do not expand.

## Required sections (use these exact headings, in this order)

1. **What this module does** — One sentence. Active voice. Names the outcome and the primary user.
2. **Key features** — A 2-column table. Left column: feature name (the user-facing label, not the dev codename). Right column: what it does in one short sentence (≤15 words). One row per feature.
3. **Who uses it** — One short sentence naming the relevant roles.
4. **Common workflows** — Bulleted list, one line each. Verb-first ("Process incoming applications", "Reconcile daily transactions").
5. **Important gotchas** — Bulleted list of 3–5 cross-cutting things that trip people up. One line each. Each must cite a transcript timestamp or ticket.
6. **Where to go next** — Bulleted list of 2–4 related modules or longer guides with `[[link placeholders]]`.

## Hard constraints

- **The one-page ceiling WINS over completeness.** Target **≤500 words total**. If listing every feature would overflow one page, list *fewer* — drop the lowest-priority features. Never overflow the page to be exhaustive.
- **Key features table: ≤12 rows.** Pick the highest-priority features; do not enumerate every ticket in the module.
- **One page.** If rendered output exceeds one page, compress — do not overflow.
- **One sentence per feature** in the Key features table. Average row length should be 8–15 words.
- **Every gotcha cites a source** with an inline `<!-- Source: -->` comment. Gotchas without sources are cut.
- **No subsections.** Flat structure only — `<h2>` per section, no `<h3>` deeper. Hierarchy is the enemy of a one-pager.
- **No long prose blocks.** If you wrote a paragraph, you've already failed the format — convert to bullets or compress to one sentence.
- **Transcript is voice; Jira is truth.** Conflicts get flagged in a single line in the gotchas section: `Discrepancy: presenter said X [MM:SS], NXT-#### says Y`.
- **No invented specifics, no industry-standard filler, internal jargon translated** — same rules as long-form.

## Output format

Plain HTML, dense layout. `<h2>` for section headings (no `<h3>`). `<table>` with `<thead>` for the Key features grid. `<ul>` for bullets. `<code>` for field/label references. Inline `<!-- Source: NXT-#### AC: "..." -->` or `<!-- Source: transcript [MM:SS] -->` comments inline. Aim for visual density — short paragraphs, tight bullets, no whitespace padding.
