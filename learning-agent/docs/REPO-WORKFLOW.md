# Repo & push workflow (Learning Studio)

How the Learning Studio code is laid out and how to get local changes onto GitHub.
Written after a push went sideways — follow this and it's repeatable.

## Where things live (important: there are TWO copies)

| Path | What it is |
|---|---|
| `…/Financials-Documentation-KT/jira-brain/` | **The git repo.** Remote: `github.com/beginnersmind94/jira-second-brain`, default branch `main`. |
| `jira-brain/learning-agent/` | **The tracked, canonical copy** of Learning Studio (vendored into the repo). This is what's on GitHub. |
| `…/Financials-Documentation-KT/learning-agent/` | **The live working copy** (sibling of jira-brain). The demo server runs from here and edits usually happen here. **It is NOT a git repo.** |

> ⚠️ Because there are two copies, they can drift. The sibling is where work happens; the repo copy is the source of truth on GitHub. **Always sync sibling → repo before pushing.** (Better long-term: pick one copy and work only there — see "Consolidate" below.)

## Pushing changes (mirrors PR #36 / the `claude/…` branch flow)

From Git Bash:

```bash
JB="/c/Users/rahul.mehta/Downloads/Financials-Documentation-KT/jira-brain"
SIB="/c/Users/rahul.mehta/Downloads/Financials-Documentation-KT/learning-agent"

# 0) one-time per machine (git complains the folder is owned by Administrators)
git config --global --add safe.directory "$JB"

# 1) sanity-check the working copy before syncing
"$SIB/.venv/Scripts/python.exe" -m py_compile "$SIB"/demo_app.py "$SIB"/demo_d.py "$SIB"/demo.py
"$SIB/.venv/Scripts/python.exe" "$SIB/test_qbank_gate.py"            # grounding gate
"$SIB/.venv/Scripts/python.exe" "$SIB/test_qbank_gate_enforcement.py" # human-approval gate

# 2) sync sibling -> repo copy, EXCLUDING venv/secrets/caches/outputs
#    (robocopy is native Windows; /XD = exclude dirs, /XF = exclude files)
powershell -NoProfile -Command "robocopy '$SIB' '$JB/learning-agent' /E \
  /XD .venv __pycache__ .git logs drafts published .codex .claude \
  /XF .env *.log *.pyc *.output ; exit 0"

# 3) branch named claude/<topic>-<YYYY-MM-DD>, commit, push
cd "$JB"
git checkout -b "claude/learning-studio-<topic>-$(date +%F)"
git add learning-agent
git commit -m "Learning Studio: <one-line summary>

<bullet details>

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
git push -u origin "$(git branch --show-current)"
```

Then open the PR from the URL git prints and **Merge pull request** into `main`
(same as PR #36). `gh` is **not installed** on this machine, so the PR is opened/
merged in the browser — or install `gh` / use a PAT to do it from the CLI.

## Never commit
`.env` (Jira creds + tokens) and `.venv/` (~520 MB) are gitignored — keep them that
way. Generated outputs (`drafts/`, `logs/`, `published/`, `*.log`) are excluded too;
they're regenerable noise.

## Gotchas seen in the wild
- **"dubious ownership"** → run the `safe.directory` line above.
- **"Repository not found" on push** → the *repo name/path is wrong*, or it's private
  and you're unauthenticated. The real repo is `jira-second-brain` and `learning-agent`
  is a **folder inside it**, not its own repo.
- **Don't `git init` the sibling.** It's a plain working folder; a stray `.git` there
  just creates a second, confusing repo.

## Consolidate (recommended next cleanup)
The two-copy setup is the root cause of drift. Either (a) work directly in
`jira-brain/learning-agent/` and run the server from there, or (b) make the sibling a
proper `git worktree`/clone of the repo. Until then, step 2 (sync) is mandatory before every push.
