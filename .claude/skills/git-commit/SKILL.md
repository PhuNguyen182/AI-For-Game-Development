---
name: git-commit
description: Write and record a commit message — English imperative subject, why-body, one change per commit, verified with `git log -1` before reporting. Use for every commit.
user-invocable: false
---

# Commit message

```
<subject — imperative, capitalized, no period, ≤50 chars where it fits, never >72>

<body — why the change was needed, wrapped at 72>

<trailers>
```

- No `feat:`/`fix:` prefixes.
- Body = what the diff cannot show: the reason, the approach chosen over another, what it deliberately does not do. Never restate the diff.
- Body omitted only when the subject is the whole story (typo, version bump).
- A body needing "and also" → two commits.
- Never: filler ("update code", "wip"), a secret, a reviewer note, a TODO, an unrun verification claim.

## Order
1. Compose subject + body in full.
2. Stage only your paths (`git add <paths>`, never `-A` on a shared folder); `git status` first — files another session made stay out.
3. Commit with both (heredoc / `-F -`), never a placeholder to amend later.
4. `git log -1 --stat` — confirm what was recorded.
5. Report quoting it. Ask before any push.
