---
name: git-recovery
description: "Recover a repo from an unintended state: lost commits, half-done rebase/merge/cherry-pick, force-push overwrite, broken index or objects, reflog and fsck. Use when work looks lost or git is stuck."
user-invocable: false
---

# Git Recovery

Not for: anchoring before a command (`git-safety-anchor`), attributing a change to a commit (`git-forensics`), Unity scenes, `.meta`/GUIDs, LFS tracking choice and the pointer-vs-content checkout check (`git-unity-repo`; this skill repairs LFS objects missing or corrupt in the store), deciding a published-history rewrite (`cto` plans it; the GD authorises the run).
Docs: https://git-scm.com/docs — unversioned, so check `git --version` before trusting a flag. LFS: https://github.com/git-lfs/git-lfs/tree/main/docs — `main` branch; a flag there may be missing from the installed `git-lfs`.

| Reference | Read when |
|---|---|
| [interrupted-and-overwritten-state.md](references/interrupted-and-overwritten-state.md) | A state file is under the git dir, `HEAD` is detached, a branch moved backwards or was force-pushed, or a merge silently lost a change |
| [reflog-and-unreachable-objects.md](references/reflog-and-unreachable-objects.md) | A commit, branch or stash is missing and you must find what still points at it |
| [index-object-and-submodule-repair.md](references/index-object-and-submodule-repair.md) | `git status` errors, `fsck` reports bad or missing objects, a submodule is on the wrong commit or deinitialised, or an LFS file is pointer text |
| [history-surgery.md](references/history-surgery.md) | The requester asked for a rewrite: squash, split, reorder, purge a path, purge a secret or PII, move binaries into LFS (`lfs migrate`); any `rebase -i` |

## Steps
1. **Read the real state** — `git status --porcelain=v1 --branch`, `git rev-parse --abbrev-ref HEAD`, and the state files under the git dir, per [interrupted-and-overwritten-state.md](references/interrupted-and-overwritten-state.md); one symptom has different repairs per operation. Parse only plumbing output (`rev-parse`, `cat-file`, `rev-list`, `for-each-ref`, `status --porcelain=v1`, `git log -g --format=`); porcelain text is a hint.
2. **Intended end state not stated → return blocked** — "put it back how it was" has several readings after a rebase, differing by exactly the commits at issue.
3. **Anchor via `git-safety-anchor` before any state change**, the repair included; run every state-changing command of the recovery with `-c gc.auto=0 -c maintenance.auto=false`, since `commit`, `merge`, `rebase` and `fetch` can start an automatic gc that prunes the unreachable objects being hunted — a botched first attempt destroys the evidence the second needs. Mid-operation: tag `ORIG_HEAD` and `rebase-merge/orig-head`; copy the git-dir state files and the index aside.
4. **Resolve an interrupted operation before anything else** — `--continue`, `--abort`, `--skip` or `--quit` in the direction the requester intended; until then other commands refuse or misbehave.
5. **Never-staged work is gone** — no object exists; `fsck --lost-found` only finds blobs written by `add`/stash (`fsck --cache` covers staged work only while the index still holds it). Report the gap; offer no reflog/fsck search; an outside-git copy re-enters via `hash-object -w`.
6. **Search every reflog and `ORIG_HEAD` before declaring a commit gone; then `fsck` for objects once written**, per [reflog-and-unreachable-objects.md](references/reflog-and-unreachable-objects.md). Re-check every `fsck` sha with `git cat-file`; make a confirmed sha reachable in the same session.
7. **Force-pushed branch: recoverable only where something still references the old tip** — walk the location table in [interrupted-and-overwritten-state.md](references/interrupted-and-overwritten-state.md) before promising anything.
8. **Repair the narrowest broken layer** — index, object store, submodule or LFS, per [index-object-and-submodule-repair.md](references/index-object-and-submodule-repair.md). Never re-clone for index or work-tree damage: a clone lacks unpushed branches, stashes, every reflog, local config, hooks, worktrees and uncommitted work-tree changes.
9. **Rewrite only on explicit request**, confirmed for that specific operation (and each `push --force` publishing it) in this conversation (dispatched: the GD's words quoted verbatim in the brief), never inferred from an earlier approval; at the blast radius `git-safety-anchor` assigned, per [history-surgery.md](references/history-surgery.md).
10. **Verify against the stated intent** — compare resulting shas and branch positions to it and report both; an error that stopped is not a success. Commit messages per `git-commit`.

## Never
- Run `git gc` in any form (expires reflogs, prunes), `prune`, or `reflog expire`/`delete`/`drop` during a recovery — they delete the pointers and objects a recovery depends on.

## Output
```
## Recovery — <state repaired>
- Diagnosed state: <what the git dir and `git status` showed>
- Blast radius: 1 | 2 | 3 (from `git-safety-anchor`)
- Anchor: <backup ref + sha, or why none>
- Route: <repair path; alternatives rejected and why>
- Commands run: <verbatim, in order>
- Recovered: <what is back, with shas>
- Not recoverable: <what is gone and why — never omit this line>
- Verified: <shas and branch positions compared to the stated intent>
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Just re-clone, that fixes a corrupt index" → declined: damage was confined to `.git/index`; rebuilt it from `HEAD` and listed the unpushed branches a re-clone would have destroyed.
