# Index, Object Store, Submodule and LFS Repair

Sources: `git-read-tree`, `git-reset`, `git-update-index`, `git-fsck`, `git-submodule` under the `Docs:` base; [lfs-spec] `spec.md`, `man/git-lfs-*.adoc` under the LFS `Docs:` base.

## Index

| Symptom | Means |
|---|---|
| `git status` fails with an index read error | Index file corrupt — rebuild it |
| Every tracked file modified, no edits made | Line-ending or filemode change, not corruption |
| Unmerged entries persist after resolving | Stale conflict state — `git read-tree --reset HEAD` discards it |
| `fsck --cache` reports missing objects | Object-store damage, not the index |

| Rebuild | Effect |
|---|---|
| `git reset` | Index ← `HEAD`; work tree untouched. Needs a readable index |
| Move `"$(git rev-parse --git-dir)/index"` aside, then `git reset` or `git read-tree HEAD` | Index unreadable. Confirm `git rev-parse --verify HEAD` resolves first; copy the index aside rather than `rm` it. `read-tree` is the plumbing form and accepts a tree other than `HEAD` |
| `git read-tree --reset -u HEAD` | `-u` also overwrites the work tree, discarding uncommitted edits without aborting — never, unless the work tree is disposable |

A rebuild keeps objects, refs, reflogs, stashes, config and (without `-u`) the work tree. It loses: the staging state (everything reads unstaged), conflict resolutions that existed only as staged entries, `assume-unchanged`/`skip-worktree` bits (reapply sparse-checkout), and intent-to-add entries (`add -N` paths return to untracked).

## Object store

| Command | Fact that decides |
|---|---|
| `git fsck --full` | Loose objects, packs and alternates (the default) |
| `git verify-pack -v <pack>` | Isolates damage to one pack vs loose objects |
| `git cat-file -t <sha>` | Absent vs merely unreachable — similar `fsck` complaints, different repairs |
| `git fetch <healthy-clone> '+refs/*:refs/recovered/*'` | Pulls missing objects in without replacing this repository |
| Copy the loose object file from a healthy clone | Content-addressed, so the same sha is byte-identical |
| `git hash-object -w <file>` | Re-enters a blob recovered from outside git |
| `git unpack-objects < <pack>` | Explodes a pack to salvage single objects |

## Submodules

| `git submodule status` prefix | Means → repair |
|---|---|
| `-` | Not initialized → `git submodule update --init --recursive` |
| `+` | Checked-out commit ≠ superproject's recorded sha → `git submodule update`, or commit the new sha if the move was intended |
| `U` | Superproject merge conflict on the submodule sha → stage the intended sha in the superproject |

| Command | Fact that decides |
|---|---|
| `git submodule update` | Checks out the recorded sha — the repair |
| `git submodule update --remote` | Moves to the remote-tracking branch: a **content change**, not a repair |
| `git submodule deinit <path>` | Deletes the submodule's work tree. Confirm it is clean and its commits pushed first; the superproject's reflog records nothing of the submodule's history |

A detached submodule `HEAD` is normal; commits made there orphan on the next update — recover them from the submodule's own reflog.

## Git LFS

| Symptom / command | Fact that decides |
|---|---|
| File reads `version https://git-lfs.github.com/spec/v1`, `oid sha256:…`, `size …`, under 1024 bytes | A canonical pointer [lfs-spec] |
| `git lfs env` | Read first: tells "not installed" from "installed but cannot fetch" |
| `git lfs install`, then `git lfs pull` | Fixes a clone made without LFS (or with `--skip-smudge`); the repository is not damaged |
| `git lfs checkout` | Writes content from the local store only; downloads nothing, never overwrites a modified file |
| `git lfs fsck --objects` / `--pointers`, `-d` | Moves corrupt objects to `.git/lfs/bad`; `-d` is a dry run |

**Caveat:** a pointer on disk with a correct commit is a filter problem — `pull` fixes it. A pointer committed where the binary belonged (the path was not in `.gitattributes` then) is a history problem: no `pull` changes it; it needs a rewrite per [history-surgery.md](history-surgery.md). A raw binary committed where a pointer belonged (`fsck --pointers` flags it) is also a history rewrite.
