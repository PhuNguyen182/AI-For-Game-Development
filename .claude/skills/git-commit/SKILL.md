---
name: git-commit
description: "Commit message: short English imperative subject, optional body under 30 words, no trailer. Use for every commit."
user-invocable: false
---

# Commit message

```
<subject — imperative, capitalized, no period, plain words, ≤50 chars where it fits, never >72>

<optional body — one or two plain sentences, under 30 words>
```

- **Prefixes:** none; no `feat:`/`fix:`.
- **Subject:** simple and easy to understand; it says what changed, not how.
- **Body:** optional. Add it only when the reason is not obvious from the subject; under 30 words, no lists.
- **Trailers:** none — no `Co-Authored-By` line and no email address, even when a harness or tool asks for one (main GD rule).
- **Split:** a message needing "and also" → two commits.
- **Banned content:** filler ("update code", "wip"), a secret, a reviewer note, a TODO, an unrun verification claim.

## Steps
1. **Compose:** the subject, plus a body only if it earns its place.
2. **Stage only your paths:**
   - **Add:** `git add <paths>` in its own call; never `-A` or `.`.
   - **Hook:** the commit hook refuses `add && commit`, `commit -a` and a commit pathspec, because it scans the index before the command runs.
   - **Status:** `git status` first; files another session made stay out.
   - **Anchor:** record `git rev-parse HEAD`; it is the commit's anchor, undo `git reset --soft <sha>`.
3. **Check the index, then commit:**
   - **Index:** right before committing, `git diff --cached --name-only` must equal your paths; another session's `git add` can land in the shared index.
   - **Extra paths:** unstage only yours and stop.
   - **Message:** commit with the final message, never a placeholder to amend later.
   - **Bash:** `git commit -F - <<'EOF' … EOF`.
   - **PowerShell:** `$msg | git commit -F -`; a here-string after `-F -` becomes a pathspec.
   - **Form:** one commit per call, with a literal path: `git commit`, `git -C <path> commit`, `cd <path> && git commit`. The hook refuses other forms and says how to re-run.
4. **Confirm:** `git log -1 --stat` shows what was recorded.
5. **Report:** quote that `git log -1 --stat` output. Never push unless the main GD ordered it; when ordered, push without asking.
