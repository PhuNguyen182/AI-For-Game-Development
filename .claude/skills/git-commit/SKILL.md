---
name: git-commit
description: "Commit message: English imperative subject, why-body, one change per commit. Use for every commit."
user-invocable: false
---

# Commit message

```
<subject — imperative, capitalized, no period, ≤50 chars where it fits, never >72>

<body — why the change was needed, wrapped at 72>

<trailers>
```

- **Prefixes:** none; no `feat:`/`fix:`.
- **Body:** what the diff cannot show: the reason, the approach chosen over another, what it deliberately does not do. Omit it only when the subject is the whole story (typo, version bump).
- **Split:** a body needing "and also" → two commits.
- **Banned content:** filler ("update code", "wip"), a secret, a reviewer note, a TODO, an unrun verification claim.

## Steps
1. **Compose:** subject + body in full.
2. **Stage only your paths:**
   - **Add:** `git add <paths>` in its own call; never `-A` or `.`.
   - **Hook:** the commit hook refuses `add && commit`, `commit -a` and a commit pathspec, because it scans the index before the command runs.
   - **Status:** `git status` first; files another session made stay out.
   - **Anchor:** record `git rev-parse HEAD`; it is the commit's anchor, undo `git reset --soft <sha>`.
3. **Check the index, then commit:**
   - **Index:** right before committing, `git diff --cached --name-only` must equal your paths; another session's `git add` can land in the shared index.
   - **Extra paths:** unstage only yours and stop.
   - **Message:** commit with both subject and body, never a placeholder to amend later.
   - **Bash:** `git commit -F - <<'EOF' … EOF`.
   - **PowerShell:** `$msg | git commit -F -`; a here-string after `-F -` becomes a pathspec.
4. **Confirm:** `git log -1 --stat` shows what was recorded.
5. **Report:** quote that `git log -1 --stat` output. Never push unless the GD ordered it; when ordered, push without asking.
