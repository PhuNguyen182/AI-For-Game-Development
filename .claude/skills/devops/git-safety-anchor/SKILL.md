---
name: git-safety-anchor
description: >
  Pre-flight gate for any state-changing git command: classify its blast
  radius, create a named backup ref before it runs, and derive the literal
  undo command. Covers `git tag backup/...`, `git stash create` for
  uncommitted work, `git rev-parse` ref snapshots, `ORIG_HEAD`, and what the
  reflog cannot recover — untracked files, a fresh clone, anything dropped by
  `gc --prune` or `reflog expire`. Use before `reset`, `rebase`, `merge`,
  `checkout`, `push --force`, `filter-repo`, `clean -xdf`, or `branch -D`.
  Not for: recovering state already lost (`git-recovery`), tracing a change
  to its commit (`git-forensics`), Unity asset and LFS specifics
  (`git-unity-repo`).
---

# Git Safety Anchor — Blast Radius, Backup Refs, and the Undo Command

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short. "Read when" is a real condition, not a restatement of the topic.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Upstream git documentation roots, and the plumbing-vs-porcelain stability distinction this skill relies on | Starting any task here, or confirming a flag against the installed git version |
| [anchor-and-undo-recipes.md](references/anchor-and-undo-recipes.md) | Per-operation undo commands — the literal reversal for `reset`, `rebase`, `merge`, `cherry-pick`, `checkout`, `branch -D`, `push --force` | Deriving the `Undo:` line for a specific operation, rather than writing "use the reflog" |
| [what-cannot-be-anchored.md](references/what-cannot-be-anchored.md) | The gaps: untracked and ignored files, submodule working trees, unpushed LFS objects, anything never staged, a fresh clone with no reflog | Before claiming an anchor is complete, or when the operation touches submodules, LFS, or untracked files |

## 1. Objective
Guarantee that no git command destroys state that was still recoverable, by producing — before the command runs — a named backup ref, a separate anchor for uncommitted work, and a literal undo command. This prevents the one failure in this domain that cannot be reported honestly: discovering after the fact that work was lost, with no ref pointing at it, no reflog entry covering it, and no way to tell the requester what they had. It also prevents the softer failure of reporting "the reflog has it" for the three cases where the reflog never did.

## 2. Role
Act as the repository safety gate for the devops track — the skill reached for whenever a git command is about to change the index, the working tree, a local ref, or a remote ref, before that command runs rather than after it fails.

## 3. When to invoke this skill
- A `reset`, `rebase`, `merge`, `cherry-pick`, `checkout`, `stash drop`, or `branch -d` is about to run against real work.
- A `push`, `push --force`, `filter-repo`, `gc --prune`, `reflog expire`, `branch -D`, `clean -xdf`, or `submodule deinit` has been requested.
- A requester asks for something whose blast radius is not stated, and the operation is not obviously read-only.
- Negative trigger: state is already lost and the question is how to get it back — that's `git-recovery`; this skill runs before the damage, not after.
- Negative trigger: identifying which commit introduced a line, a string, or a behaviour — that's `git-forensics`.
- Negative trigger: whether a `.unity` scene merge is safe, or which asset files belong in LFS — that's `git-unity-repo`.

## 4. How to use this skill
1. **Classify the blast radius before running anything** — radius 1 touches nothing and needs no anchor; radius 2 touches the index, working tree, or local refs and is reflog-recoverable; radius 3 touches remote refs or state the reflog never held. Misclassifying downward is how work disappears, so when a command spans two rows, take the higher one.
2. **Refuse to proceed at radius 3 without authorization for that exact operation in the current prompt** — a general instruction to tidy the branch does not authorize rewriting published history, and an anchor cannot restore a ref another clone already fetched.
3. **Tag every ref the operation can move, not just `HEAD`** — a rebase moves one branch, a `filter-repo` moves all of them, and an anchor that covers only `HEAD` silently loses the rest. Use one `backup/<op>-<utc>` tag per affected ref, per [anchor-and-undo-recipes.md](references/anchor-and-undo-recipes.md).
4. **Anchor uncommitted work with `git stash create`, never with `git stash push`** — `create` writes the stash commit object and returns its sha while leaving the index and working tree exactly as they are, so the operation about to run sees the state the requester expects; `push` would mutate the very thing being protected.
5. **Record the pre-state as shas rather than as prose** — capture `git rev-parse` for every affected ref plus `git status --porcelain`, because "was on develop with some local edits" is not something an undo command can consume.
6. **Derive the literal undo command before the operation runs** — a named reversal (`git reset --hard <sha>`, `git update-ref refs/heads/<b> <sha>`) is verifiable now, whereas "recover it from the reflog" is a hope that has to hold later. Take the exact form from [anchor-and-undo-recipes.md](references/anchor-and-undo-recipes.md).
7. **State what this anchor does not cover** — check the operation against [what-cannot-be-anchored.md](references/what-cannot-be-anchored.md) and name every gap, because a requester who believes everything is covered will authorize an operation they would otherwise refuse.
8. **Verify the anchor resolves before returning** — run `git rev-parse <backup-ref>` and `git cat-file -e <stash-sha>` and report what they returned; an anchor that was never confirmed to exist is indistinguishable from no anchor, and must never be reported as one. Read only plumbing output when a check is scripted, per the stability table in [root-links.md](references/root-links.md).
9. **Name backup refs and report in English** — per `language-and-comments.md`'s Working language section, so a ref created in one session is readable in the next.
10. **Return `Decision: blocked` when the radius cannot be determined or the anchor cannot be made** — an unanchorable radius-2 or radius-3 operation is a stop, not a judgement call to make on the requester's behalf.

## 5. Specific goals / tasks this skill performs
- Assign a blast radius of 1, 2, or 3 to a specific git command, with the reason it landed there.
- Create and verify `backup/<op>-<utc>` tags covering every ref the operation can move.
- Anchor uncommitted work non-destructively and report the sha that restores it.
- Produce the literal undo command for the operation, not a description of how recovery might work.
- Enumerate what the anchor cannot restore, so the authorization decision is made on real information.
- Out of scope: recovering state already lost (`git-recovery`), attributing a change to a commit (`git-forensics`), Unity asset and LFS handling (`git-unity-repo`), and the authorization decision itself for a published-history rewrite (`cto`).

## 6. Output format
```
## Safety Anchor — <operation being anchored>
- Blast radius: 1 | 2 | 3 — <why it landed there>
- Operation: <the exact command about to run>
- Anchor refs: <backup/... names and the shas they point at, or "none — radius 1">
- Uncommitted work: <the `git stash create` sha and the command that restores it, or "working tree clean">
- Undo: <the literal command that reverses the operation>
- Not covered: <what this anchor cannot restore>
- Verified: <what `git rev-parse` / `git cat-file -e` actually returned>
- Decision: proceed | blocked
- Routed to: <git-expert / cto / gd / none>
```

**Extended report — emit ONLY when the requester asks for it.** It adds all three fields below the decision:
```
- Known limitations: <what this anchor does not protect — omit this line entirely if there are genuinely none>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Drop the last two commits on my local feature branch, I want to redo them."
- Output: radius 2. Tagged `backup/reset-20260823T101500Z` at the current `HEAD`, anchored dirty tracked files with `git stash create` (sha reported), derived `Undo: git reset --hard backup/reset-20260823T101500Z`, and flagged that two untracked files in the working tree are outside the stash object. `Decision: proceed`.

**Example 2**
- Input: "just squash and force-push develop, the anchor is overkill for a branch only I use."
- Output: declined — `develop` has an upstream, so the reflog of every other clone is outside this repository's reach and radius 3 applies regardless of who currently uses it. Reported `Decision: blocked`, `Routed to: gd`, with the exact command quoted and the cost stated; nothing run.

**Example 3**
- Input: "Anchor before I run `git clean -xdf` to fix a weird build."
- Output: radius 3, and the anchor is reported as structurally incomplete — untracked and ignored files are what `clean -xdf` deletes and are exactly what no ref, stash, or reflog holds, per [what-cannot-be-anchored.md](references/what-cannot-be-anchored.md). `Decision: blocked` pending an explicit list of what may be deleted, with `git clean -xdn` offered as the read-only preview.

## 8. Edge cases & guardrails
- Never report an anchor that was not verified to resolve — an unconfirmed backup ref is worse than no anchor, because it converts a cautious requester into a confident one.
- Never use `git stash push` to anchor uncommitted work — it mutates the working tree the operation is about to act on, changing the very state being protected.
- Never anchor only `HEAD` when the operation can move several refs; a `rebase --onto`, a `filter-repo`, or a branch-deleting cleanup leaves the unanchored refs unrecoverable.
- Never claim reflog coverage for uncommitted work, for a fresh clone, or after `gc --prune`/`reflog expire` — the reflog never held the first and no longer holds the last two.
- Never write "use the reflog" in the `Undo:` field — derive the literal command with its sha, or state that no reversal exists and why.
- If the blast radius cannot be determined from the command and the repository state, return `Decision: blocked` rather than assuming the lower radius.
- A radius-3 operation requires explicit confirmation for that specific operation in the current conversation, never inferred from an earlier approval or from the requester's evident intent.
