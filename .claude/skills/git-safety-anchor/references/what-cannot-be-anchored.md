# What Cannot Be Anchored — Gaps No Ref, Stash, or Reflog Holds

Sources: [git-stash](https://git-scm.com/docs/git-stash), [git-reflog](https://git-scm.com/docs/git-reflog), [git-gc](https://git-scm.com/docs/git-gc), [git-config](https://git-scm.com/docs/git-config), [git-fsck](https://git-scm.com/docs/git-fsck), [git-update-ref](https://git-scm.com/docs/git-update-ref), [gitignore](https://git-scm.com/docs/gitignore), [Pro Git — Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules), [git-lfs-push](https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-push.adoc).
Covers: SKILL.md §4 — "Classify the blast radius before running anything", "State what this anchor does not cover".

Enumerates the state that no `backup/` tag, no `git stash create` sha, and no
reflog entry can restore, each with the mechanism that causes the gap. These
rows are what separates a radius-2 operation the reflog genuinely covers from a
radius-3 one it never did, and they are the source of the `Not covered:` line —
the anchors themselves live in [anchor-and-undo-recipes.md](anchor-and-undo-recipes.md).

## Contents

- [Content git never hashed](#content-git-never-hashed)
- [State stored outside this repository](#state-stored-outside-this-repository)
- [Objects that existed and are already gone](#objects-that-existed-and-are-already-gone)
- [Reflog coverage boundaries](#reflog-coverage-boundaries)

## Content git never hashed

| Gap | Mechanism | Consequence | Source |
|---|---|---|---|
| Untracked files | Not in the index, so no blob object exists for their content. `git stash create` records the tracked working tree and the index — it has no untracked-file option at all | Outside every anchor this skill can produce. An operation whose purpose is deleting them (`git clean -xdf`) has no reversal, only a preview | [git-stash — create](https://git-scm.com/docs/git-stash#Documentation/git-stash.txt-create) |
| Ignored files | Excluded by `.gitignore` from ever being staged, and hidden from `git status` by default, so they are absent from the recorded pre-state as well as from the anchor | Build output, local config, and generated assets vanish silently; the pre-state snapshot does not even show that they were there | [gitignore](https://git-scm.com/docs/gitignore) |
| Anything never `git add`ed | Git stores an object only for content it has hashed; a file that has never been staged has no blob in the object database at any point in its history | No sha exists to name in an undo command — the loss is unreportable in shas, only describable in prose | [Pro Git — Plumbing and Porcelain](https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain) |
| Uncommitted work at any moment other than the anchor | `git stash create` snapshots the instant it runs; edits made between the anchor and the operation are not in that commit object | The anchor must be the last thing to run before the operation, or it silently protects a stale state | [git-stash — create](https://git-scm.com/docs/git-stash#Documentation/git-stash.txt-create) |

**Critical caveat**: `git stash create` takes no `--include-untracked` — that
option belongs to `git stash push`, which cannot be used here because it
mutates the working tree the operation is about to act on. Untracked and
ignored files are therefore structurally unanchorable by this skill, and an
operation that targets them is reported as unanchorable rather than anchored.

## State stored outside this repository

| Gap | Mechanism | Consequence | Source |
|---|---|---|---|
| Submodule working trees | The superproject records the submodule with mode `160000` — "recording a commit as a directory entry rather than a subdirectory or a file" — and "doesn't track its contents". A tag in the parent anchors that one sha | The submodule's dirty working tree, its staged changes, and its local branch names are not in the parent's object database and are not restored by restoring the parent | [Pro Git — Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules) |
| Submodule commits never pushed | The parent's gitlink names a commit that must exist in the submodule's own repository; nothing in the parent contains it | Restoring the parent's gitlink after the submodule's own objects are gone leaves a reference to a commit no clone can resolve | [Pro Git — Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules) |
| Unpushed Git LFS objects | The committed git object is a small pointer file; the large content is uploaded separately by `git lfs push`, which "Upload[s] Git LFS files to the configured endpoint for the current Git remote" | A `backup/` tag anchors the pointer, never the content it points at. If the content was never pushed and the local store is cleared, the pointer resolves to nothing | [git-lfs-push](https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-push.adoc) |
| The local LFS object store | Lives under `.git/lfs/objects`, outside git's own object database, so no ref reaches it and `git fsck` does not account for it | Any operation that cleans or re-clones the repository can drop content the git history still references | synthesized |
| Another clone's refs after a force-push | The remote ref moved; a clone that already fetched the old tip holds it in its own remote-tracking ref and its own reflog, in a repository this one cannot read or write | No anchor taken here restores it, which is why a force-push against a ref with an upstream is radius 3 regardless of who uses the branch | [git-push](https://git-scm.com/docs/git-push) |
| The remote's own reflog | Git provides no protocol for reading a remote reflog; whether one exists at all depends on the hosting platform keeping and exposing it | "The server has it" is an assumption about the host, not a property of git, and must never be reported as coverage | [git-reflog](https://git-scm.com/docs/git-reflog) |

## Objects that existed and are already gone

| Gap | Mechanism | Consequence | Source |
|---|---|---|---|
| A fresh clone's absent reflog | A clone's reflogs begin at the moment of cloning; there is no record of the source repository's earlier ref movements | Immediately after cloning, "the reflog has it" is false for every commit not reachable from a fetched ref | [git-reflog](https://git-scm.com/docs/git-reflog) |
| Objects removed by `git gc --prune` | `git gc` calls `prune --expire 2.weeks.ago` by default, and `--prune=now` "prunes loose objects regardless of their age" | Once pruned, nothing points at the content and no salvage path exists — recovery attempts are `git-recovery`'s territory and may find nothing | [git-gc — options](https://git-scm.com/docs/git-gc#_options) |
| Entries removed by `git reflog expire` | It "prunes older reflog entries"; entries past `gc.reflogExpire`, or past `gc.reflogExpireUnreachable` and unreachable from the current tip, are removed | The reflog stops being a fallback for exactly the commits an anchor would otherwise not have needed to cover | [git-reflog](https://git-scm.com/docs/git-reflog) |
| Objects unreachable once a reflog entry expires | `git fsck` "defaults to using the index file, all SHA-1 references in the `refs` namespace, and all reflogs (unless --no-reflogs is given) as heads" | An object that was findable only through a reflog entry leaves fsck's reachable set when that entry expires, and becomes prunable | [git-fsck](https://git-scm.com/docs/git-fsck#_options) |
| Repositories with ref logging disabled | Ref updates are logged only when `core.logAllRefUpdates` is true and the ref is under `refs/heads/`, `refs/remotes/`, `refs/notes/`, or is a pseudoref such as `HEAD` or `ORIG_HEAD` | In a repository or namespace where logging is off, there is no reflog to fall back on at all — the tag anchor is the only reversal | [git-update-ref](https://git-scm.com/docs/git-update-ref#_logging_updates) |

## Reflog coverage boundaries

| Boundary | Value or mechanism | Source |
|---|---|---|
| `gc.reflogExpire` | Removes reflog entries older than this time; "defaults to 90 days". `now` expires everything immediately, `never` suppresses expiry | [git-gc — configuration](https://git-scm.com/docs/git-gc#_configuration) |
| `gc.reflogExpireUnreachable` | Removes entries older than this time that "are not reachable from the current tip"; "defaults to 30 days" — the shorter window, and the one that applies to commits an operation orphaned | [git-gc — configuration](https://git-scm.com/docs/git-gc#_configuration) |
| Per-pattern override | Both settings accept a `<pattern>` (for example `refs/stash`) so expiry can differ per ref namespace | [git-gc — configuration](https://git-scm.com/docs/git-gc#_configuration) |
| `gc.pruneExpire` | Grace period before unreachable objects are deleted; `git gc` calls `prune --expire 2.weeks.ago` unless overridden, and `now` disables the grace period entirely | [git-gc — configuration](https://git-scm.com/docs/git-gc#_configuration) |
| Default `--expire` when unspecified | "the expiration time is taken from the configuration setting `gc.reflogExpire`, which in turn defaults to 90 days" | [git-reflog](https://git-scm.com/docs/git-reflog) |
| Scope — one reflog per ref | The reflog records movements of a single ref in a single repository; it is never fetched, pushed, or shared between clones | [git-reflog](https://git-scm.com/docs/git-reflog) |
| Scope — refs only | It logs ref updates, so index and working-tree state that was never committed has no entry in it under any configuration | [git-update-ref](https://git-scm.com/docs/git-update-ref#_logging_updates) |
| `refs/stash` has its own reflog | Each stash entry is a reflog entry on that ref, which is what `git stash drop` removes — leaving the commit object unreachable until the next prune | [git-stash](https://git-scm.com/docs/git-stash) |
| Effective values are per-repository | Every default above is overridable configuration, so the real window is whatever `git config` reports in the repository the operation will run in, not the documented number | [git-config](https://git-scm.com/docs/git-config) |

Every row here describes a gap that exists *before* the operation runs, which
is what makes it reportable as `Not covered:` rather than discovered
afterwards. Once state has actually been lost, salvage — dangling-object
recovery, `fsck --lost-found`, reflog archaeology — is `git-recovery`'s scope,
and nothing in this folder should be read as a promise that it will succeed.
