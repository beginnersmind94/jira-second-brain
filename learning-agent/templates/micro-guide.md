# Template: Micro guide (~3 pages)

You are writing the micro-guide for the `{{module}}` module, based on the training transcript at `{{transcript_path}}` and the verified Jira evidence collected in Tasks 1–3.

## Goal
A staff member can perform the top workflows after reading this. Task success, not comprehensive reference. Moderate depth — enough to execute without re-watching the training video.

## Selection
Top 3–5 workflows by priority. Lower-priority features get one-line mentions or are omitted with a reason. If the plan from Task 2 says more than 5 workflows belong here, the template is wrong — note in the trace that long-form would be more appropriate.

## Required sections (use these exact headings, in this order)

1. **Purpose** — One short paragraph: what this guide teaches you to do. Frame it as an outcome ("After reading this, you can…").
2. **Who this is for** — One or two sentences naming roles. Be specific (director / manager / cashier / dietitian / Cybersoft staff) — not generic "users".
3. **Before you start** — Prerequisites in 3–5 bullets. Each bullet cites where the prerequisite came from (a ticket, transcript timestamp, or KB page).
4. **Top workflows** — One subsection per workflow (3–5 max). Each subsection:
   - One-sentence purpose
   - Steps as a numbered list — terse, action-verb-first
   - One common pitfall, framed as `> [!warning] Watch out: …`
5. **Common mistakes** — 3–5 bullets aggregating recurring SME-observed mistakes from across the workflows. Cite the transcript timestamp where each was mentioned, or the ticket that documented the issue.
6. **Related content** — One line per related module with a `[[link placeholder]]`. Do not duplicate.
7. **Sources** — Tickets, transcript timestamps, and KB pages cited. Must match the inline `<!-- Source: -->` comments.

## Hard constraints

- **Target length:** 600–1,200 words. **HARD CEILING: 1,500 words.** If you cannot fit the planned content under 1,500 words, you have selected the wrong template — compress, do not overflow. Count your words mentally before emitting and trim aggressively if you are over.
- **A large source does not justify overflow.** If you are derived from a longer long-form guide, you must STILL compress to ≤1,500 words: select the top 3–5 workflows and DROP the rest. Do not try to preserve every section of the source — the ceiling beats completeness.
- **No more than 5 workflows with full steps.** If your plan exceeds 5, switch to long-form.
- **Every factual claim has an inline source comment:** `<!-- Source: NXT-1234 AC: "verbatim quote" -->` or `<!-- Source: transcript [MM:SS] -->`.
- **One pitfall per workflow.** Not two, not zero. The pitfall MUST come from the transcript (presenter said "watch out for…") or from a ticket explicitly documenting the issue — not invented to fill the slot.
- **Transcript is voice; Jira is truth.** When they conflict, flag both verbatim in a `> [!warning] Discrepancy` callout.
- **No invented specifics, no industry-standard filler, internal jargon translated** — same rules as long-form.

## Output format

Plain HTML, semantic tags. `<h2>` for top sections, `<h3>` for workflow subsections, `<ol>` for steps, `<ul>` for prerequisite/mistake bullets, `<blockquote>` for `> [!warning]` callouts, `<code>` for field names and UI labels. Inline source comments use HTML comment syntax `<!-- ... -->` and survive into the draft.
