# Index, Object Store, Submodule and LFS Repair — Narrowest Fix First

Sources: [git-read-tree](https://git-scm.com/docs/git-read-tree), [git-reset](https://git-scm.com/docs/git-reset), [git-update-index](https://git-scm.com/docs/git-update-index), [git-fsck](https://git-scm.com/docs/git-fsck), [git-hash-object](https://git-scm.com/docs/git-hash-object), [git-submodule](https://git-scm.com/docs/git-submodule), [Git LFS](https://git-lfs.com), [git-lfs docs](https://github.com/git-lfs/git-lfs/tree/main/docs).

Covers: SKILL.md §4 — "Rebuild the index rather than the repository when only the index is corrupt".

Four layers can fail independently — the index, the object store, a submodule's
own repository, and the LFS filter chain — and each has a repair that touches
only that layer. The reason this matters is asymmetric cost: rebuilding an index
loses staging state, while a re-clone loses every unpushed branch, stash and
local config in the repository. Finding lost commits once the layer is healthy
belongs to [reflog-and-unreachable-objects.md](reflog-and-unreachable-objects.md).

## Contents

- [Index corruption](#index-corruption)
- [Rebuilding the index — what survives and what does not](#rebuilding-the-index--what-survives-and-what-does-not)
- [Object-store damage](#object-store-damage)
- [Why a re-clone is the expensive repair](#why-a-re-clone-is-the-expensive-repair)
- [Submodules](#submodules)
- [Git LFS](#git-lfs)

## Index corruption

The index is "a collection of files with stat information, whose contents are
stored as objects… a stored version of your working tree" — a cache, derived
entirely from a tree plus the staging the user did on top of it. Nothing unique
to history lives there, which is what makes discarding it safe.

| Symptom | What it indicates | Source |
|---|---|---|
| `git status` fails with an index read error rather than reporting files | The index file is truncated or malformed; commands that read it refuse before touching anything else | synthesized (upstream documents the index's role, not its error strings) |
| `git status` reports every tracked file as modified with no edits made | Stat-cache mismatch rather than corruption — often a line-ending or filemode setting change, not a repair case | synthesized |
| Unmerged entries persist after the operation that caused them was resolved | A stale conflict state; `git read-tree --reset` "discard[s]" unmerged entries "instead of failing" | [git-read-tree `--reset`](https://git-scm.com/docs/git-read-tree) |
| `git fsck --cache` reports objects the index references that do not exist | The damage is in the object store, not the index — go to [object-store damage](#object-store-damage) | [git-fsck `--cache`](https://git-scm.com/docs/git-fsck) |

| Rebuild route | Effect | Use when | Source |
|---|---|---|---|
| `git reset` (no mode, no pathspec) | Defaults to `--mixed`: resets the index to `HEAD` and leaves the working tree untouched | The index file is readable but its contents are wrong | [git-reset](https://git-scm.com/docs/git-reset) |
| Delete the index file, then `git reset` | Recreates the index from `HEAD` from nothing | The index file itself cannot be read, so `git reset` also fails | [git-reset](https://git-scm.com/docs/git-reset) |
| Delete the index file, then `git read-tree HEAD` | The plumbing equivalent: "Reads the tree information given by *<tree-ish>* into the index, but does not actually **update** any of the files it caches" | A script needs the stable interface, or the index must be built from a tree that is not `HEAD` | [git-read-tree](https://git-scm.com/docs/git-read-tree) |
| `git read-tree --reset -u HEAD` | Also updates the working tree — with `--reset`, "updates leading to loss of working tree changes or untracked files or directories will not abort the operation" | Never, in a recovery, unless the working tree is already known to be disposable. This is the destructive variant | [git-read-tree `--reset`](https://git-scm.com/docs/git-read-tree) |

```sh
git rev-parse --verify HEAD
rm -f "$(git rev-parse --git-dir)/index"
git read-tree HEAD
git status --porcelain=v1
```

**Critical caveat**: the `-u` flag is what separates an index rebuild from a
working-tree overwrite. `git read-tree HEAD` touches no file on disk;
`git read-tree --reset -u HEAD` silently discards uncommitted edits, and per
[reflog-and-unreachable-objects.md](reflog-and-unreachable-objects.md) nothing
unstaged that it destroys exists as an object anywhere.

## Rebuilding the index — what survives and what does not

| Preserved | Lost | Source |
|---|---|---|
| Every commit, tree, blob and tag in the object store | The staging state: which of the working tree's modifications were `git add`-ed. After the rebuild everything modified reads as unstaged | [git-reset](https://git-scm.com/docs/git-reset) |
| The working tree's file contents, including uncommitted edits, as long as `-u` is not used | Resolved-but-uncommitted conflict resolutions that existed only as staged index entries | [git-read-tree](https://git-scm.com/docs/git-read-tree) |
| All branches, tags, remote-tracking refs and their reflogs | `assume-unchanged` and `skip-worktree` bits, which are index flags — sparse-checkout patterns survive on disk but must be reapplied to the new index | [git-update-index](https://git-scm.com/docs/git-update-index) |
| Stashes, local config, hooks, and everything else under the git directory | Intent-to-add entries (`git add -N`) — the path returns to untracked | [git-update-index](https://git-scm.com/docs/git-update-index) |

## Object-store damage

| Instrument | What it does | Source |
|---|---|---|
| `git fsck --full` | Checks loose objects, packfiles, and alternate object pools; the default, disabled with `--no-full` | [git-fsck `--full`](https://git-scm.com/docs/git-fsck) |
| `git verify-pack -v <pack>` | Verifies one packfile's integrity and lists its contents, isolating whether damage is in a pack or in loose objects | [git-verify-pack](https://git-scm.com/docs/git-verify-pack) |
| `git cat-file -t <sha>` on a reported sha | Confirms whether the object is genuinely absent or merely unreachable — the two produce similar-looking `fsck` complaints and have different repairs | [git-cat-file](https://git-scm.com/docs/git-cat-file) |
| `git fetch <path-to-healthy-clone> '+refs/*:refs/recovered/*'` | Pulls the missing objects from another clone that still has them, without replacing this repository | [git-fetch](https://git-scm.com/docs/git-fetch) |
| Copy the loose object file from a healthy clone's object directory | Object files are content-addressed and immutable, so the same sha in another clone is byte-identical | [Pro Git — Maintenance and Data Recovery](https://git-scm.com/book/en/v2/Git-Internals-Maintenance-and-Data-Recovery) |
| `git hash-object -w <file>` | Writes a file's contents into the object store and prints the resulting sha — the way a blob recovered from outside git (a backup, an editor's temp file) re-enters the repository | [git-hash-object](https://git-scm.com/docs/git-hash-object) |
| `git unpack-objects < <pack>` | Explodes a packfile into loose objects, so an individual object can be recovered from a pack that a repair cannot otherwise index | [git-unpack-objects](https://git-scm.com/docs/git-unpack-objects) |

```sh
git fsck --full --no-progress
git cat-file -t "$(git rev-parse HEAD^{tree})"
git fetch /path/to/healthy-clone '+refs/heads/*:refs/recovered/*'
git fsck --full --no-progress
```

## Why a re-clone is the expensive repair

| Not present in a fresh clone | Why | Source |
|---|---|---|
| Branches that were never pushed | A clone copies refs from the remote; a ref that exists only locally has no remote counterpart to copy | [git-clone](https://git-scm.com/docs/git-clone) |
| Stashes | `refs/stash` is not fetched by a clone's default refspec | [git-stash](https://git-scm.com/docs/git-stash) |
| Every reflog | Reflogs are per-clone records of local ref movement; the new clone starts its own from the moment of cloning, so all recovery history is gone with them | [git-reflog](https://git-scm.com/docs/git-reflog) |
| Local config, hooks, worktree registrations | All live inside the discarded git directory, not in the remote | [git-config](https://git-scm.com/docs/git-config) |
| Uncommitted working-tree work | Never existed as an object, per [reflog-and-unreachable-objects.md](reflog-and-unreachable-objects.md) | [git-clone](https://git-scm.com/docs/git-clone) |

## Submodules

`git submodule status` prints, for each submodule, the sha of the checked-out
commit, the path, and `git describe` output — prefixed by one character that is
the whole diagnosis.

| Prefix | Meaning | Repair | Source |
|---|---|---|---|
| `-` | "the submodule is not initialized" — the directory exists but is empty and no `submodule.<name>` config entry is present | `git submodule update --init --recursive` | [git-submodule `status`](https://git-scm.com/docs/git-submodule) |
| `+` | "the currently checked out submodule commit does not match the SHA-1 found in the index of the containing repository" — the submodule is on a different commit than the superproject records | `git submodule update` to return it to the recorded sha, or commit the new sha in the superproject if the move was intended | [git-submodule `status`](https://git-scm.com/docs/git-submodule) |
| `U` | "the submodule has merge conflicts" — the superproject merge produced two competing submodule shas | Resolve in the superproject by staging the intended sha; the submodule itself is not conflicted | [git-submodule `status`](https://git-scm.com/docs/git-submodule) |
| (no prefix) | Initialized and at the recorded commit | — | [git-submodule `status`](https://git-scm.com/docs/git-submodule) |

| Operation | Semantics | Source |
|---|---|---|
| `git submodule update --init --recursive` | `--init` initializes from `.gitmodules` "if the submodule is not yet initialized"; `--recursive` "will recurse into the registered submodules, and update any nested submodules within" | [git-submodule](https://git-scm.com/docs/git-submodule) |
| `git submodule update` (no `--remote`) | Checks the submodule out at **the superproject's recorded sha** — the default, and the one a repair wants | [git-submodule](https://git-scm.com/docs/git-submodule) |
| `git submodule update --remote` | "Instead of using the superproject's recorded SHA-1… use the status of the submodule's remote-tracking branch", defaulting to the remote `HEAD` unless `submodule.<name>.branch` is set. This **moves the submodule forward** and is a content change, not a repair | [git-submodule `--remote`](https://git-scm.com/docs/git-submodule) |
| `git submodule deinit <path>` | "remove the whole `submodule.$name` section from .git/config together with their work tree" — subsequent `update`, `foreach` and `sync` skip it until initialized again | [git-submodule `deinit`](https://git-scm.com/docs/git-submodule) |
| Detached submodule `HEAD` | The normal state, not a fault: an update checks out a recorded sha, which by definition is not a branch tip. Commits made there are unreachable once the next update moves it — recover them from the submodule's own reflog | [gitglossary — detached HEAD](https://git-scm.com/docs/gitglossary) |

**Critical caveat**: `deinit` deletes the submodule's **work tree**. Commits made
inside a submodule and never pushed live in that submodule's own git directory;
confirm the submodule is clean and pushed before deinitializing, because the
superproject's reflog records nothing about the submodule's internal history.

## Git LFS

LFS "replaces large files such as audio samples, videos, datasets, and graphics
with text pointers inside Git", and those pointers become real content only when
LFS's smudge filter runs. If the filter was never configured, the pointer is what
lands on disk — and it is valid committed content, so nothing reports an error.

| Symptom / instrument | Fact | Source |
|---|---|---|
| A tracked binary checks out as a ~130-byte text file beginning `version https://git-lfs.github.com/spec/v1`, then `oid sha256:<hash>` and `size <bytes>` | That is a canonical LFS pointer file. Pointer files "MUST contain only UTF-8 characters", each line is `{key} {value}\n`, and the whole file stays under 1024 bytes | [Git LFS spec](https://github.com/git-lfs/git-lfs/blob/main/docs/spec.md) |
| `git lfs env` | Prints the resolved LFS environment — endpoint, local object store paths, and whether the filters are configured. The first thing to read, because it distinguishes "not installed" from "installed but cannot fetch" | [git-lfs-env](https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-env.adoc) |
| `git lfs install` | Configures "clean and smudge filters under the name 'lfs' in the global Git config" and installs a pre-push hook for the current repository | [git-lfs-install](https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-install.adoc) |
| `git lfs checkout` | "scans the current ref for all LFS objects that would be required, then where a file is either missing in the working copy, or contains placeholder pointer content with the same SHA, the real file content is written, provided we have it in the local store" — it downloads nothing and never overwrites a modified file | [git-lfs-checkout](https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-checkout.adoc) |
| `git lfs pull` | "generally equivalent to" `git lfs fetch` followed by `git lfs checkout` — the repair when the local object store does not yet have the content | [git-lfs-pull](https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-pull.adoc) |
| `git lfs fsck` | "Check[s] GIT LFS files for consistency", relocating corrupted files to `.git/lfs/bad`. `--objects` validates each object in `HEAD` against its expected hash and presence on disk; `--pointers` verifies each pointer is canonical and that files meant to be LFS files actually are; `-d`/`--dry-run` checks without moving anything | [git-lfs-fsck](https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-fsck.adoc) |
| LFS not installed at clone time | The smudge filter was never configured, so every LFS-tracked path checked out as its pointer text. The repository is not damaged: `git lfs install` then `git lfs pull` populates the working tree. `git lfs install --skip-smudge` produces the same appearance deliberately and "requires a manual `git lfs pull` every time a new commit is checked out" | [git-lfs-install](https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-install.adoc) |
| A pointer committed as the real file, or a real file committed where a pointer belonged | `.gitattributes` did not cover the path when the commit was made, so history holds the wrong content. Fixing this in existing commits is a rewrite, not a checkout — see [history-surgery.md](history-surgery.md) | [git-lfs-fsck `--pointers`](https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-fsck.adoc) |

```sh
git lfs env
git lfs fsck --pointers --dry-run
git lfs install
git lfs pull
```

A pointer left in the working tree is a *filter* problem and never a *history*
problem: the object is on the LFS server and the commit is correct. A pointer
recorded in a commit where the binary belonged is the reverse, and no amount of
`git lfs pull` will change it.
