# Anchor Primitives and Per-Operation Undo Commands

Sources: [git-stash](https://git-scm.com/docs/git-stash), [git-reset](https://git-scm.com/docs/git-reset), [git-update-ref](https://git-scm.com/docs/git-update-ref), [git-status](https://git-scm.com/docs/git-status), [git-filter-branch](https://git-scm.com/docs/git-filter-branch), [git-filter-repo](https://github.com/newren/git-filter-repo), [Pro Git — Reset Demystified](https://git-scm.com/book/en/v2/Git-Tools-Reset-Demystified).
Covers: SKILL.md §4 — "Tag every ref the operation can move, not just `HEAD`", "Anchor uncommitted work with `git stash create`, never with `git stash push`", "Derive the literal undo command before the operation runs".

Holds the two things an anchor is assembled from: the primitives that capture
state without disturbing it, and the literal reversal for each state-changing
operation. Every `Undo:` here is a command with a sha placeholder, never a
description of recovery — what to do once state is already lost belongs to
`git-recovery`, and the gaps none of these commands close are enumerated in
[what-cannot-be-anchored.md](what-cannot-be-anchored.md).

## Contents

- [Anchor primitives](#anchor-primitives)
- [Restoring from a `stash create` sha](#restoring-from-a-stash-create-sha)
- [Undo recipes — local history and refs](#undo-recipes--local-history-and-refs)
- [Undo recipes — working tree, stash, and remote](#undo-recipes--working-tree-stash-and-remote)
- [Why `ORIG_HEAD` is not an anchor](#why-orig_head-is-not-an-anchor)

## Anchor primitives

| Primitive | What it captures | What it does not touch | Source |
|---|---|---|---|
| `git tag backup/<op>-<utc>` | A named, non-moving ref at one commit. Because it is a real ref, everything reachable from it is reachable, so `gc` will not prune the history behind it | The index, the working tree, and every other ref — a tag names one commit and nothing else | [git-tag](https://git-scm.com/docs/git-tag) |
| `git stash create` | Writes a stash entry as a regular commit object recording the tracked working tree and the index, and returns its object name "without storing it anywhere in the ref namespace" | Nothing at all — no ref is written, no index update, no working-tree change. This is what makes it the correct anchor | [git-stash — create](https://git-scm.com/docs/git-stash#Documentation/git-stash.txt-create) |
| `git stash store <sha>` | Stores a sha produced by `create` (a dangling merge commit) into the stash ref, updating the stash reflog — makes an anchor reachable so `gc` cannot reclaim it | The index and the working tree | [git-stash — store](https://git-scm.com/docs/git-stash#Documentation/git-stash.txt-store) |
| `git rev-parse <ref>` | Resolves a ref to the sha the undo command will consume. Read-only plumbing, safe to parse | Everything — it writes nothing | [git-rev-parse](https://git-scm.com/docs/git-rev-parse) |
| `git rev-parse --verify <ref>` | The existence check: fails with non-zero status when the ref does not resolve, which is what turns a reported anchor into a verified one | Everything | [git-rev-parse](https://git-scm.com/docs/git-rev-parse) |
| `git update-ref <ref> <sha>` | Sets a ref to a sha directly, without checking the branch out — the only way to restore a branch that is not `HEAD`. Appends a reflog line when `core.logAllRefUpdates` is on and the ref is under `refs/heads/`, `refs/remotes/`, `refs/notes/`, or is a pseudoref | The index and the working tree — restoring a non-current branch leaves the checkout alone | [git-update-ref](https://git-scm.com/docs/git-update-ref) |
| `git update-ref -d <ref> <old-oid>` | Deletes a ref only after verifying it still holds `<old-oid>` — the safe form when removing a `backup/` tag after the operation is confirmed good | Objects; deleting the ref only makes them unreachable | [git-update-ref](https://git-scm.com/docs/git-update-ref) |
| `git status --porcelain` | The pre-state of the index and working tree in the one `status` format guaranteed stable across git versions and user configuration | Everything — it is a read | [git-status — porcelain format v1](https://git-scm.com/docs/git-status#_porcelain_format_version_1) |
| `git cat-file -e <sha>` | Confirms an object — notably a `stash create` sha that no ref points at — actually exists in the object database | Everything | [git-cat-file](https://git-scm.com/docs/git-cat-file) |
| `ORIG_HEAD` | Set by `reset`, `merge`, `pull`, and `rebase` to the tip of the current branch before the operation | Nothing, but it is written *by* those operations rather than by you — see [below](#why-orig_head-is-not-an-anchor) | [git-reset](https://git-scm.com/docs/git-reset) |

**Critical caveat**: `git stash create` writes the stash commit object and
prints its sha **without modifying the index or the working tree** — the
operation about to run therefore sees exactly the state the requester expects.
`git stash push` saves the same modifications and then "roll[s] them back to
`HEAD` (in the working tree and in the index)", which mutates the very state
being protected and changes what the operation will do. `create` is the anchor
primitive; `push` is a workflow command and must never stand in for it.

## Restoring from a `stash create` sha

A `create` sha is a commit-ish, so it is consumed the same way any commit is —
which is why capturing it is enough and no stash-list entry is needed.

| Restore form | Restores | Use when | Source |
|---|---|---|---|
| `git stash apply --index <stash-sha>` | Working-tree changes **and** the staged/unstaged split | The pre-state had a meaningful index that must come back exactly | [git-stash](https://git-scm.com/docs/git-stash) |
| `git stash apply <stash-sha>` | Working-tree changes only; everything lands unstaged | The index/worktree split does not matter, or `--index` refuses to reinstate cleanly | [git-stash](https://git-scm.com/docs/git-stash) |
| `git checkout <stash-sha> -- <path>` | One path, from the anchored snapshot | Only a single file's edits were destroyed | [git-checkout](https://git-scm.com/docs/git-checkout) |
| `git stash store -m "<label>" <stash-sha>` | Nothing yet — it makes the sha reachable via `refs/stash` | The anchor must survive a `gc` before it can be applied | [git-stash — store](https://git-scm.com/docs/git-stash#Documentation/git-stash.txt-store) |

## Undo recipes — local history and refs

`<utc>` is the anchor's timestamp; a `<sha>` placeholder is the value
`git rev-parse` returned before the operation ran.

| Operation | What moves | Anchor to take beforehand | Literal undo | Source |
|---|---|---|---|---|
| `git reset --soft <commit>` | The current branch ref only; index and working tree are left unchanged | `git tag backup/reset-<utc> HEAD` | `git reset --soft backup/reset-<utc>` | [git-reset — --soft](https://git-scm.com/docs/git-reset#Documentation/git-reset.txt---soft) |
| `git reset --mixed <commit>` | The branch ref and the index; the working directory is unchanged, so staged work becomes unstaged | `git tag backup/reset-<utc> HEAD` plus `git stash create` if anything was staged | `git reset --mixed backup/reset-<utc>`, then `git stash apply --index <stash-sha>` to restore the staged/unstaged split | [git-reset — --mixed](https://git-scm.com/docs/git-reset#Documentation/git-reset.txt---mixed) |
| `git reset --hard <commit>` | The branch ref, the index, and the working tree — it "may overwrite untracked files" and removes tracked files absent from `<commit>` | `git tag backup/reset-<utc> HEAD` **and** `git stash create` | `git reset --hard backup/reset-<utc>`, then `git stash apply --index <stash-sha>` | [git-reset — --hard](https://git-scm.com/docs/git-reset#Documentation/git-reset.txt---hard) |
| `git rebase <upstream>` | The rebased branch ref, onto newly created commits; the originals stay in the object database but nothing names them | `git tag backup/rebase-<utc> HEAD` | `git reset --hard backup/rebase-<utc>` | [git-rebase](https://git-scm.com/docs/git-rebase) |
| `git rebase --onto <newbase> <upstream> <branch>` | `<branch>` alone — every other branch containing commits from the range keeps pointing at the pre-rebase commits, so an anchor on `HEAD` covers the wrong ref | One `git tag backup/rebase-onto-<utc>-<ref>` per ref that `git for-each-ref` shows inside the range | `git update-ref refs/heads/<branch> backup/rebase-onto-<utc>-<branch>` — restores without needing that branch checked out | [git-rebase](https://git-scm.com/docs/git-rebase) |
| `git merge <ref>` | The current branch ref to a new merge commit, or fast-forwards it; index and working tree follow | `git tag backup/merge-<utc> HEAD` plus `git stash create` if dirty | `git reset --hard backup/merge-<utc>` | [git-merge](https://git-scm.com/docs/git-merge) |
| `git cherry-pick <commit>...` | The current branch ref, gaining one new commit per picked commit | `git tag backup/cherry-pick-<utc> HEAD` | `git reset --hard backup/cherry-pick-<utc>` | [git-cherry-pick](https://git-scm.com/docs/git-cherry-pick) |
| `git commit --amend` | The tip commit is replaced by a new one; the original becomes unreachable | `git tag backup/amend-<utc> HEAD` | `git reset --hard backup/amend-<utc>` to discard the amend outright, or `git reset --soft backup/amend-<utc>` to keep the amended content staged | [git-commit](https://git-scm.com/docs/git-commit) |
| `git branch -d <b>` / `git branch -D <b>` | The ref `refs/heads/<b>` is removed; `-D` removes it even when unmerged, leaving its commits reachable from nothing | `git rev-parse refs/heads/<b>` recorded as `<sha>` | `git update-ref refs/heads/<b> <sha>` | [git-branch](https://git-scm.com/docs/git-branch) |

`git merge --abort` and `git rebase --abort`/`git cherry-pick --abort` reverse
only an operation still in progress with a conflict pending. Once the
operation has completed, they are unavailable and the tag anchor is the only
reversal — which is why the tag is taken before, not after.

## Undo recipes — working tree, stash, and remote

| Operation | What moves | Anchor to take beforehand | Literal undo | Source |
|---|---|---|---|---|
| `git checkout <branch>` | `HEAD` only; dirty tracked changes are carried across when git can, and the checkout is refused when it cannot | `git rev-parse --abbrev-ref HEAD` recorded as `<previous-branch>`, plus `git stash create` if dirty | `git checkout <previous-branch>` | [git-checkout](https://git-scm.com/docs/git-checkout) |
| `git checkout -- <path>` | That path in the working tree is overwritten from the index; unstaged edits to it are destroyed and no ref ever named them | `git stash create` — the only primitive that captures unstaged tracked edits | `git checkout <stash-sha> -- <path>` | [git-checkout](https://git-scm.com/docs/git-checkout) |
| `git stash drop [<entry>]` | The entry is removed from `refs/stash` and its reflog; the commit object survives only until the next prune | `git rev-parse stash@{0}` recorded as `<sha>`, or `git tag backup/stash-<utc> stash@{0}` | `git stash store -m "restored" <sha>` | [git-stash](https://git-scm.com/docs/git-stash) |
| `git push <remote> <b>` | The remote's `refs/heads/<b>` moves forward, and the local `refs/remotes/<remote>/<b>` follows | `git rev-parse refs/remotes/<remote>/<b>` recorded as `<sha>` | None that is itself safe: moving a remote ref backwards requires `git push --force <remote> <sha>:refs/heads/<b>`, which is the row below | [git-push](https://git-scm.com/docs/git-push) |
| `git push --force <remote> <b>` | The remote ref is overwritten, discarding commits that only that ref named — including commits another clone has already fetched | `git tag backup/push-force-<utc> refs/remotes/<remote>/<b>`, and prefer `--force-with-lease` so a concurrent update aborts the push instead of overwriting it | `git push --force <remote> backup/push-force-<utc>:refs/heads/<b>` — restores the remote ref only, never another clone's state | [git-push](https://git-scm.com/docs/git-push) |
| `git filter-repo <filters>` | Every commit is rewritten, so every branch and tag moves; the tool bails unless it is running in a fresh clone (overridable with `--force`) and auto-shrinks the repository afterwards, removing old cruft | A separate `git clone --mirror` taken before the run — an in-repo tag is not a dependable anchor across a rewrite that repacks and prunes the repository it lives in | Restore from the mirror: `git push --mirror <origin>` from the untouched clone, or re-clone from it | [git-filter-repo](https://github.com/newren/git-filter-repo) |
| `git filter-branch <filters>` | Same blast radius, with originals retained: "The original refs, if different from the rewritten ones, will be stored in the namespace `refs/original`" | The `refs/original/` namespace is written by the tool; still tag each affected ref, since a second run overwrites it | `git update-ref refs/heads/<b> refs/original/refs/heads/<b>` | [git-filter-branch](https://git-scm.com/docs/git-filter-branch#SAFETY) |

## Why `ORIG_HEAD` is not an anchor

| Property | Consequence | Source |
|---|---|---|
| Written by the operation, not by the operator | It exists only after the operation ran; it cannot be verified beforehand, which is what an anchor is for | [git-reset](https://git-scm.com/docs/git-reset) |
| Holds one value — the previous tip of the current branch | A rewrite that moved several refs leaves the others unanchored, so it never substitutes for one tag per affected ref | [git-reset](https://git-scm.com/docs/git-reset) |
| Overwritten by the next `reset`, `merge`, `pull`, or `rebase` | A second operation destroys the first one's reversal point, so it survives exactly one step | [git-reset](https://git-scm.com/docs/git-reset) |
| Not set by every state-changing command | `checkout`, `commit --amend`, `branch -D`, `stash drop`, and `push` do not write it, so its presence cannot be assumed | [git-update-ref](https://git-scm.com/docs/git-update-ref#_logging_updates) |

Use it as a convenience in an undo command when it demonstrably still points
where expected, and never as the reason a tag anchor was skipped.
