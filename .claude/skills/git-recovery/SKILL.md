---
name: git-recovery
description: >
  Get a repository out of a state its owner did not intend: lost commits, a
  `rebase`/`merge`/`cherry-pick` stopped midway (`REBASE_HEAD`, `MERGE_HEAD`,
  `ORIG_HEAD`, `--continue`/`--abort`/`--skip`), a force-push that overwrote
  work, detached `HEAD` carrying commits, a deleted branch, a corrupt index
  or object store, `clean -xdf` aftermath, broken submodules, an LFS pointer
  committed without LFS. Uses `git reflog --all`, `git fsck --lost-found`,
  `git cat-file`. Also covers deliberate rewriting with `rebase -i`,
  `filter-repo` and `worktree`. Not for: anchoring before a command runs
  (`git-safety-anchor`), tracing which commit caused a defect
  (`git-forensics`), Unity scene and `.meta` handling (`git-unity-repo`).
---

# Git Recovery — Unintended States, Lost Work, and Deliberate History Rewriting

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short. "Read when" is a real condition, not a restatement of the topic.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Upstream git documentation roots, and which recovery commands are plumbing versus porcelain | Starting any task here, or confirming a flag against the installed git version |
| [reflog-and-unreachable-objects.md](references/reflog-and-unreachable-objects.md) | `git reflog --all`, `ORIG_HEAD`, reflog expiry defaults, `git fsck --lost-found --unreachable`, `git cat-file` triage, and precisely what each one cannot hold | A commit or branch is gone and the question is whether anything still points at it |
| [interrupted-and-overwritten-state.md](references/interrupted-and-overwritten-state.md) | Detecting a stopped `rebase`/`merge`/`cherry-pick` from `.git` state, `--continue`/`--abort`/`--skip` semantics, detached `HEAD`, force-push overwrite, evil merges that silently drop changes | The repository is mid-operation, on no branch, or a branch moved backwards without explanation |
| [index-object-and-submodule-repair.md](references/index-object-and-submodule-repair.md) | Rebuilding a corrupt index, `fsck` on a damaged object store, recovering from a healthy clone, submodule detach and `deinit`, LFS pointer corruption and `git lfs fsck` | `git status` errors out, objects fail integrity checks, or a submodule or LFS file behaves as text |
| [history-surgery.md](references/history-surgery.md) | `rebase -i` and `rebase --onto`, splitting and reordering commits, `merge --squash`, `git filter-repo` and why not `filter-branch`, `git worktree`, `git subtree` | The rewriting is intentional rather than a repair, and the requester has authorized it |

## 1. Objective
Return a repository to the state its owner intended, losing nothing that was still recoverable and claiming nothing that was not. The characteristic failure here is optimism: reporting that the reflog "will have it" for work that was never committed, that `git fsck` can recover a file that was never staged, or that a force-pushed branch can be restored from a clone that only ever fetched the new history. This skill establishes which of those actually hold before promising a repair, and says plainly when the answer is that the work is gone.

## 2. Role
Act as the repository repair specialist for the devops track — the skill reached for whenever a git operation left the repository somewhere its owner did not expect, and whenever a deliberate history rewrite has already been authorized.

## 3. When to invoke this skill
- Commits are missing after a `reset`, `rebase`, `checkout`, or branch deletion.
- `git status` reports an operation in progress, an unexpected detached `HEAD`, or errors out entirely.
- A push overwrote work, or a branch moved backwards with no local explanation.
- A submodule points at the wrong commit or has been deinitialised, or an LFS-tracked file checks out as a pointer file.
- A rewrite is wanted deliberately — squashing a branch, splitting a commit, purging a path — and authorization is already in hand.
- Negative trigger: the command has not run yet and the ask is to make it safe — that's `git-safety-anchor`.
- Negative trigger: which commit introduced a defect, or who last touched a line — that's `git-forensics`.
- Negative trigger: how to merge a `.unity` scene, or why a `.meta` GUID changed — that's `git-unity-repo`.

## 4. How to use this skill
1. **Establish the actual repository state before choosing a repair** — read `git status`, `git rev-parse --abbrev-ref HEAD`, and the presence of `rebase-merge/`, `rebase-apply/`, `MERGE_HEAD` or `CHERRY_PICK_HEAD` under the git directory, because the same symptom has different repairs depending on which of these is set, per [interrupted-and-overwritten-state.md](references/interrupted-and-overwritten-state.md). Parse only plumbing output when scripting a check, per the stability table in [root-links.md](references/root-links.md).
2. **Anchor before repairing, since a repair is itself a state change** — invoke `git-safety-anchor` first; a botched recovery on top of a bad state destroys the evidence needed for the second attempt.
3. **Finish or abandon an interrupted operation before attempting anything else** — a stopped `rebase` or `merge` leaves the index in a state where most other commands either refuse or make things worse, so resolve it with `--continue`, `--abort`, or `--skip` before any further diagnosis.
4. **Say plainly when uncommitted work is unrecoverable** — a `reset --hard` or `checkout` that discarded changes never staged leaves nothing behind, and `git fsck --lost-found` can only surface a blob that was written by a `git add` or a stash. Report the gap rather than offering a search that will find nothing.
5. **Search every reflog before concluding a commit is gone** — `git reflog --all` covers refs the default single-ref listing misses, and `ORIG_HEAD` still points at the pre-operation position after a `reset`, `merge`, or `rebase`, per [reflog-and-unreachable-objects.md](references/reflog-and-unreachable-objects.md).
6. **Fall back to `git fsck --lost-found` only for objects that were once written** — it enumerates unreachable commits and blobs that still exist in the object store, which is a different set from "everything that was ever in the working tree", and `gc --prune` may already have removed them.
7. **Treat a force-pushed remote branch as gone from this clone unless a local ref still holds it** — the old objects live only where something still references them, so check this repository's reflog, other clones, and the hosting provider's own retention before promising recovery.
8. **Rebuild the index rather than the repository when only the index is corrupt** — removing the index file and re-reading the tree restores a working state without touching commits, whereas a re-clone discards local branches that were never pushed, per [index-object-and-submodule-repair.md](references/index-object-and-submodule-repair.md).
9. **Keep deliberate rewriting separate from repair** — `rebase -i`, `filter-repo` and `merge --squash` share instruments with recovery but not intent; they run only on an explicit request, at the blast radius `git-safety-anchor` assigned, per [history-surgery.md](references/history-surgery.md).
10. **Prefer `git filter-repo` over `git filter-branch`** — upstream documents `filter-branch` as slow and dangerous with subtle failure modes and steers users to `filter-repo`, so reaching for the deprecated tool is a defect rather than a preference.
11. **Verify the repaired state against what the requester said they wanted** — compare the resulting shas and branch positions to the stated intent and report both; a repair that merely stopped erroring is not a repair that succeeded.
12. **Report in English** — per `language-and-comments.md`'s Working language section, and write any commit message made during the repair per `commit-message.md`.
13. **Return blocked when the intended state was never stated** — "put it back how it was" has several readings once a rebase is involved, and guessing between them can discard the very commits the requester wanted kept.

## 5. Specific goals / tasks this skill performs
- Diagnose the repository's actual state from `.git` contents rather than from the requester's description of it.
- Restore commits lost to a `reset`, `rebase`, or branch deletion, naming the ref or reflog entry that made it possible.
- Resolve an interrupted `rebase`, `merge`, or `cherry-pick` in the direction the requester intended.
- Repair a corrupt index or object store, choosing the narrowest repair that works.
- Restore a submodule to its recorded commit, and fix an LFS pointer checked out as text.
- Execute an authorized history rewrite, and report the new shas alongside the anchor that reverses it.
- State explicitly which requested recoveries are not possible, and why.
- Out of scope: creating the anchor (`git-safety-anchor`), attributing a change to a commit or an author (`git-forensics`), Unity scene, prefab and GUID semantics (`git-unity-repo`), and authorizing a published-history rewrite (`cto`).

## 6. Output format
```
## Recovery Work — <the state that was repaired>
- Diagnosed state: <what `.git` and `git status` actually showed>
- Blast radius: 1 | 2 | 3 — as assigned by `git-safety-anchor`
- Anchor: <backup ref and sha, or why none was needed>
- Route chosen: <the repair path, and the alternatives rejected with the reason>
- Commands run: <verbatim, in order>
- Recovered: <what is back, with shas>
- Not recoverable: <what is genuinely gone, and why — never omit this line to look complete>
- Verified: <how the repaired state was confirmed against the stated intent>
- Layer: repository metadata | Game.Core.* | Game.Client.*
- Known limitations: <what this repair does not address>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what this repair does not address — omit this line entirely if there are genuinely none>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "I ran `git reset --hard HEAD~3` and I need those three commits back."
- Output: `ORIG_HEAD` still pointed at the pre-reset position, so recovered with `git reset --hard ORIG_HEAD` after anchoring the current tip. Reported all four shas and confirmed the branch position matched the stated intent. Also reported that two files edited but never staged before the reset are not in any object and are gone.

**Example 2**
- Input: "just re-clone the repo, that always fixes a corrupt index."
- Output: declined — the corruption was confined to `.git/index`, which `rm .git/index && git reset` rebuilds from the committed tree, whereas a re-clone would have discarded three local branches that had never been pushed. Rebuilt the index, verified `git status` and `git fsck` clean, and listed the branches the re-clone would have destroyed.

**Example 3**
- Input: "Someone force-pushed over my work on the shared branch this morning."
- Output: this clone's `refs/remotes` reflog still held the pre-push sha, so recovered the overwritten commits into a new local branch and reported them. Stated clearly that had this clone already fetched the rewritten history without a reflog entry, the objects would have existed nowhere reachable from here, and recovery would have depended on another clone or the hosting provider.

## 8. Edge cases & guardrails
- Never claim the reflog will recover uncommitted work — it records where refs pointed, not what the working tree contained, and nothing that was never staged exists as an object.
- Never offer `git fsck --lost-found` as a general undo; it finds objects that were written and became unreachable, which excludes every change that was never added or stashed.
- Never run a repair before anchoring the broken state — a failed first attempt on top of it removes the evidence the second attempt needs.
- Never repair around an interrupted operation; resolve the `rebase`, `merge`, or `cherry-pick` first, or the index state will make the next command's result unpredictable.
- Never reach for `git filter-branch` when `git filter-repo` is available — upstream documents the former as dangerous and superseded.
- Never re-clone to fix a problem confined to the index or the working tree; unpushed branches, stashes, and local config do not survive it.
- Never report a repair as complete on the basis that the error stopped; verify the shas and branch positions against the stated intent and report what was compared.
- If the intended end state was not stated, ask for it rather than choosing between readings of "how it was" — the readings differ by exactly the commits at issue.
- A deliberate history rewrite, and any `push --force` that publishes one, requires explicit confirmation for that specific operation in the current conversation, never inferred from an earlier approval.
