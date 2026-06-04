# Template: Long-form guide (~20 pages)

You are writing the long-form learning guide for the `{{module}}` module, based on the training transcript at `{{transcript_path}}` and the verified Jira evidence collected in Tasks 1–3.

## Goal
A staff member who has never touched this module can learn it entirely from this one document. Comprehensive reference, not a tutorial. Full depth on every workflow.

## Selection
Cover the workflows and features the **presenter actually taught in the transcript** — typically 5–12 — at full depth. Jira tickets are for **truth and citations** on those features, **NOT a checklist to document exhaustively**: a module may have hundreds of tickets, but this guide documents what the training taught, not every ticket. Features that appear only in Jira (never mentioned by the presenter) get at most a one-line mention in the relevant section — do **not** write full subsections for them. Cross-module references are mentioned in one line with a link placeholder — do not deep-dive into another module's content. If a feature you'd expect to see is absent from BOTH the transcript and Jira, do not invent it; leave a `[TO VERIFY: feature X mentioned by presenter but no AC found]` marker for the human editor.

## Required sections (use these exact headings, in this order)

1. **Overview** — 4–6 sentences. What this module does in plain language. What's *in* scope and what's *not*. The one outcome a typical user is trying to reach.
2. **Roles and permissions** — Who uses this module. Map roles (director / manager / cashier / dietitian / Cybersoft staff) to the actions they can take. Cite the Jira tickets that defined the permission rules.
3. **Prerequisites** — Configuration, district setup, related modules that must be set up first. Be specific about what "set up" means.
4. **Full workflows** — One subsection per major workflow. Each subsection: purpose, step-by-step, screen-by-screen with real page names, what the user sees at each step. Use numbered steps when order matters.
5. **Key fields and statuses** — Field-by-field reference for every important data input. For each field: what it is, valid values, what it controls downstream. For statuses: the state machine (what triggers transitions, who can transition).
6. **Reports and outputs** — Every report, export, or downstream artifact the module produces. What's in each, who consumes it, when it's run.
7. **Exceptions** — Documented edge cases, error states, recovery procedures. Each item cites the ticket that surfaced the issue. If there is no ticket, the item doesn't belong here.
8. **Troubleshooting** — Symptom → likely cause → fix. Sourced from transcript Q&A and known-issue tickets.
9. **Related content** — One line per related module, with a `[[link placeholder]]`. Do not duplicate the related module's content here.
10. **Sources** — Full list of tickets, transcript timestamps, and KB pages cited in the guide. This must match the inline `<!-- Source: -->` comments.

## Hard constraints

- **Target length:** 2,500–4,000 words. **HARD CEILING: 4,500 words.** This is a learning guide, not a ticket dump — if you are exceeding the ceiling you are over-documenting Jira tickets the presenter never taught. The ceiling WINS over completeness: cover the taught workflows at depth, list everything else briefly, compress rather than overflow.
- **No major feature omitted without an explicit reason.** If you intentionally drop something, leave a one-line note in the Sources section explaining why (e.g., "Omitted: deprecated per NXT-XXXX, presenter mentioned at [12:34] as legacy").
- **Every factual claim has an inline source comment** in HTML format: `<!-- Source: NXT-1234 AC: "verbatim quote" -->` or `<!-- Source: transcript [MM:SS] -->`. These comments are preserved in the draft and stripped at publish time.
- **The transcript is the voice; Jira is the truth.** Match the presenter's teaching style and examples. When a transcript claim contradicts Jira AC, surface both quoted verbatim in a `> [!warning] Discrepancy` callout — do not silently pick one.
- **No invented specifics.** Exact labels, menu paths, error strings: cite or leave a `[TO VERIFY]` marker.
- **No "industry-standard" or "best-practice" filler.** If you can't cite the claim, cut it.
- **Internal jargon is translated.** Dev shorthand from Jira (`BABECL`, `CRUD permission`) becomes user-facing language. The original term goes in the `<!-- Source: -->` comment for traceability.

## Output format

Plain HTML — no `<html>`, `<head>`, or `<body>` wrappers. Use semantic tags: `<h2>` for section headings (the document has one implicit `<h1>` from the resource title), `<h3>` for subsections, `<ol>`/`<ul>` for lists, `<table>` for field-value reference grids, `<blockquote>` for callouts and verbatim transcript snippets, `<code>` for field names and UI labels. Inline source comments use `<!-- ... -->` HTML comment syntax — these survive into the draft and are stripped at publish.
