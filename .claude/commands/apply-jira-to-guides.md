---
description: Apply a Jira CSV to module guides — 4-pass workflow (edit, strip-to-sidecar, drift check, voice spot-check)
argument-hint: <csv-path> <module> [platform=SC]
---

Apply the Jira CSV at `$1` to the **$2** module guides. Platform defaults to `SC` if `$3` is empty.

## Inputs

- Jira CSV: `$1`
- Module: `$2`
- Platform: `$3` (default `SC`)
- Guides directory: `raw/guides/markdown/<platform>/$2/`
- Protected paths (never modify): `*.raw.md`, `*.legacy`, `manifest.csv`, `failures.csv`, `snapshots/`, anything in `diffs/` outside `diffs/proposed/`, anything outside the guides directory

Read CLAUDE.md for the project's anti-hallucination rules, citation rules, and guide-layer authority rules before starting. The "Verbatim-citation rule for guide edits" and the five anti-hallucination rules apply with full force.

## Pass 1 — Apply edits

### Filter the CSV to:

- `Custom field (Module)` = `$2`
- `Resolution` in (`Done`, `Fixed`, `Resolved`)
- `Resolved` >= 2023-01-01
- `Custom field (Release Notes Required)` indicates RN exists in some form (i.e., not `Not Required`). If `Not Required` and AC clearly shows a user-visible change, keep it; otherwise skip.

Note on CSV quirks: `Resolved` is `M/D/YYYY h:mm AM/PM`. `Release Notes Required` values seen in practice: `External Only`, `External/Internal`, `Internal Only`, `Not Required`. Treat anything other than `Not Required` as RN-exists.

### For each filtered ticket:

- Read **Release Notes first**, then Acceptance Criteria. Description is context only — never sole basis.
- If the change is user-visible, edit the relevant guide. If no guide applies, skip and note it.
- Internal-Only RN tickets are usually skipped (RN written for internal audience).

### Editing rules:

- Edit only `*.md` files (not `.raw.md`, not `.legacy`) under the guides directory.
- Iterative diffs only. Don't reformat unchanged sections. Preserve frontmatter exactly.
- Above each changed block, add an HTML comment:
  ```
  <!-- Source: TICKET-1234 (resolved YYYY-MM-DD) — one-sentence reason from RN or AC -->
  ```
- **Match the guide's voice**: short imperatives in step lists, bullet brevity. Don't paste AC text into prose. Avoid release-note voice ("we have added", "we've updated", "we will roll out") — rewrite to instructive voice ("A new setting controls...", "The grid now includes...").
- **Translate internal codes** (e.g., `BABECL`, `CRUD`, `FOH`, `FRENOSSN`, `AUTODCNOTIFY`, `INCCEPVER`, `ADDINCSUR`) to the on-screen label the user sees. If the on-screen label can't be found from the source, state the gap as an Open note — don't pass the code through.
- Don't invent steps, validations, or permissions not in the source.

## Pass 2 — Strip inline citations to sidecar changelog

The inline `<!-- Source: ... -->` comments are noisy in review and would leak to published rendering. After Pass 1 lands:

1. For each modified `.md`:
   - Regex-extract every `<!-- Source: TICKET-XXX (resolved YYYY-MM-DD) — ... -->` capturing (ticket, resolved, reason).
   - Strip the citation line (consume leading whitespace and trailing newline so no stray blank line remains).
2. Write a sidecar changelog at `raw/guides/ticket-updates/<YYYY-MM-DD>-$2.md`:
   - One `###` section per modified guide (file path as header).
   - Under each: a Markdown table with columns `Ticket | Resolved | Reason`. Reason = the exact text that was inside the inline comment.
   - At the bottom, a `## Skipped tickets` section grouping the IDs you reported as skipped, by reason.

## Pass 3 — Claim drift check

For each modified `.md`:

- Reconstruct Pass 1 (post-edit, pre-strip): take the current disk content (Pass 2), reverse-apply cleaned edits to get baseline, then forward-apply the original new-strings (with citations) to get Pass 1.
- Strip `<!-- Source: -->` and `<!-- TODO: -->` lines from both Pass 1 and Pass 2.
- Compare stripped(Pass 1) to Pass 2.

Classify each remaining textual change:

- **REWORDING** — same claim, different words (allowed)
- **COMPRESSION** — Pass 2 says less than Pass 1 (allowed if dropped content was redundant; flag if a specific claim was lost)
- **NEW CLAIM** — Pass 2 says something not in Pass 1 (NOT allowed under the cleanup pass)
- **LOST CLAIM** — Pass 1 said something Pass 2 dropped (flag for review)

If any NEW CLAIM or LOST CLAIM is found, **stop**. Do not generate the final HTML diff. Report violation with file path, Pass 1 text, Pass 2 text, classification. Wait for guidance.

A CLEAN drift result is expected when Pass 1 already produced clean prose (no codes, no release-note voice) — the check earns its keep when Pass 1 was rough and Pass 2 had to rewrite.

## Pass 4 — Voice & jargon spot-check

Grep the modified `.md` files for failure modes that drift check alone won't catch:

- Release-note voice: `\b[Ww]e (have|'ve|'re|'ll|will|are|advise|added|made|updated|removed|completed|rolled|finished|moved|introduced|implemented)`
- Surviving codes: `\b(BABECL|CRUD|FOH|FRENOSSN|AUTODCNOTIFY|INCCEPVER|PINLENGTH|PINTYPE|STAFFPINTP|ADDINCSUR)\b` (extend with any module-specific codes seen in the CSV)
- AC-paste tells: `^\s*(\*\s*)?Verify (that|users|user can)`
- RN pleasantries: `based on user feedback|please contact|cheers|thank you` (case-insensitive)
- Internal team / dev jargon: `Cybersoft|Implementation team|preapproval data|secondary matching`

Any hit → either fix in place (small) or flag as Open note (judgment call needed).

## Combined HTML diff

After Pass 2 (and before Pass 3), regenerate a single consolidated HTML diff at:

```
raw/guides/diffs/proposed/all-$2-diffs.html
```

Structure:

- Sticky left sidebar TOC listing each modified guide with its line delta.
- Main column with one anchored `<section>` per file: header (path + line counts + delta), `<table class="diff">` (difflib.HtmlDiff, context=True, numlines=3, wrapcolumn=100), and a "Sources for this file" block (small muted table: Ticket / Resolved / Reason) appended below the diff table.
- Green = added, red = removed, yellow = changed. Monospace, no external assets, embedded CSS.
- Files are untracked in git — reconstruct the baseline by reverse-applying the cleaned session edits.

Print the `file://` URL of the combined HTML at the end.

## Final report (this is the canonical output template)

Structure your final response exactly as follows:

1. **Files modified** — count + paths
2. **Tickets applied** — table: `Ticket | Guide | What changed`
3. **Tickets skipped** — grouped by reason, each as `**TICKET** — one-line reason`
4. **Open notes** — jargon you couldn't translate verbatim, ambiguous changes, on-screen labels missing from source, anything an SME should confirm
5. **Confirmation: no protected files touched** — verified by mtime or file enumeration
6. **Pass 2 cleanup** — citations stripped count, sidecar changelog path, regenerated HTML diff path with `file://` URL
7. **Pass 3 drift check** — `N/N files CLEAN` or list of drifted files with classified hunks
8. **Pass 4 voice & jargon spot-check** — table of patterns searched + hit counts + brief notes on any hits

Do not commit. Wait for the user's review and approval before any further changes.
