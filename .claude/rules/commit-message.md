# Shared — Commit Message Convention

Applies to: every commit made in this repository — by `git-expert`, by any agent explicitly authorized to
commit, and by the orchestrator committing directly. Like `language-and-comments.md`, this file sits above
the `.claude/rules/<group>/` folders rather than inside one.

## Why it exists

A commit message is the only durable record of *why* a change was made. The diff already says what changed,
and it says it better than any prose could — but nothing in the repository states the reason except the
message. `git-forensics` exists to reconstruct that reason months later from history alone; every empty or
vague message is a question it will have to answer by guessing.

## Language

English, always — per `language-and-comments.md`'s Working language section. This holds even when the
request that produced the change was written in Vietnamese.

## Structure

```
<subject — imperative, one line>
                                  <- blank line, mandatory
<body — why the change was needed, wrapped at 72 columns>

<trailers, if any>
```

- **Subject**: imperative mood ("Add the safety anchor skill", not "Added" or "Adding"), capitalized, no
  trailing period. Under 50 characters where it fits, never over 72.
- **No type prefixes.** This repository does not use Conventional Commits — `feat:`, `fix(scope):` and
  `chore:` are machinery, not natural language, and the existing history has none. Don't introduce them.
- **Trailers** (`Co-Authored-By:`, `Reviewed-by:`) sit after the body, separated by a blank line. A trailer
  is not a description and never satisfies the body requirement.

## The body is where the work is

Write what a reader who has the diff still cannot see:

- The reason the change was needed — the request, the defect, the constraint that forced it.
- The approach, when another reasonable approach existed and this one was chosen over it.
- What the change deliberately does *not* do, when a reader would otherwise assume it did.

Never restate the diff in prose. This is the same discipline `language-and-comments.md` applies to code
comments — explain the non-obvious why, never the what the reader can already read.

Every commit carries a body. The single exception is a change whose subject is already the complete
explanation — a typo fix, a version bump — where a body could only restate it; padding one in makes history
harder to read, not easier.

## One commit, one change

A body that needs "and also" is two commits. This is not tidiness: `git bisect` can only name a commit as
the cause of a defect if that commit did one thing, and `git revert` can only undo a change cleanly if the
commit did not carry three unrelated ones alongside it.

## Order of operations

The full message goes into the commit **before** the work is reported and before any push is mentioned.

1. Compose the subject and the body in full.
2. Commit with both — never a placeholder subject to be amended later, and never `-m` alone when a body is
   owed.
3. Verify with `git log -1` that the message actually recorded is the one intended.
4. Then report, quoting that message, and ask before pushing.

The explanation belongs in the commit, not in the reply that follows it. A chat reply scrolls out of reach;
the commit is still there in a year, which is the entire reason the message is written at all.

## What never goes in a commit message

- Filler that would fit any commit in the repository: "update code", "fix bug", "wip", "misc changes".
- A secret, a token, or a path containing a credential. A message cannot be corrected out of published
  history without a rewrite — a radius-3 operation, per `git-expert`'s blast-radius table.
- A note to the reviewer, an apology, or a TODO. Those belong in the Implementation Note per
  `implementation-note.md`, or in an issue.
- A claim of verification nobody performed — `qa/verification-standards.md` governs what a verification
  claim requires, and a commit message is not exempt from it.

## Rules

- English, imperative subject, blank line, body. No `feat:`/`fix:` prefixes.
- Every commit carries a body unless the subject is genuinely the whole explanation — and then no body,
  rather than a padded one.
- One commit, one change; a body needing "and also" splits into two commits.
- The complete message is in the commit before the work is reported, and the report quotes what `git log -1`
  actually shows.
- Never push as part of committing. The user authorizes a push separately, per each agent's own guardrails.
- Never put a secret, a reviewer note, or an unperformed verification claim in a commit message.