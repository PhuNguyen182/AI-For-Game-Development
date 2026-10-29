# What Cannot Be Anchored

Docs: https://git-scm.com/docs/git-<subcommand> (stash, reflog, gc, config, fsck, update-ref); Pro Git submodules: https://git-scm.com/book/en/v2/Git-Tools-Submodules; LFS: https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-push.adoc.

These gaps exist before the operation runs; each feeds the `Not covered:` line. Salvage after loss is `git-recovery`'s, with no promise it succeeds.

## Content git never hashed
| Gap | Consequence |
|---|---|
| Untracked files | No blob exists; `stash create` has no `--include-untracked` (that is `push`, which mutates the tree). An operation whose purpose is deleting them (`clean -xdf`) has a preview, no reversal |
| Ignored files | Never staged and hidden from `status`, so absent from the pre-state too; build output, local config, generated assets vanish silently |
| Anything never `git add`ed | No object at any point, so no sha to name; the loss is describable only in prose |
| Edits made between anchor and operation | `stash create` snapshots one instant; run it last |

## State outside this repository
| Gap | Consequence |
|---|---|
| Submodule working trees | Parent records only gitlink mode `160000` (one sha). Dirty tree, staged changes and local branch names are not restored by restoring the parent |
| Unpushed submodule commits | Restoring the gitlink after the submodule's objects are gone leaves a commit no clone can resolve |
| Unpushed LFS objects | A tag anchors the pointer, not the content; if never `git lfs push`ed and the local store is cleared, the pointer resolves to nothing |
| Local LFS store (`.git/lfs/objects`) | Outside git's object database; no ref reaches it and `fsck` does not account for it, so clean/re-clone can drop content history still references |
| Another clone after a force-push | Holds the old tip in its own remote-tracking ref and reflog, unreadable from here; why force-push on a ref with an upstream is radius 3 |
| Remote reflog | Git has no protocol to read one; "the server has it" is a host assumption, never coverage |

## Objects already gone
| Gap | Consequence |
|---|---|
| Fresh clone | Reflogs start at clone time; "the reflog has it" is false for commits not reachable from a fetched ref |
| `git gc --prune` | Default `prune --expire 2.weeks.ago`; `--prune=now` prunes loose objects regardless of age. Pruned content has no salvage path |
| `git reflog expire` | Removes entries past `gc.reflogExpire` or unreachable ones past `gc.reflogExpireUnreachable`, making orphaned objects prunable (fsck counts reflogs as heads) |
| Ref logging off | Logged only when `core.logAllRefUpdates` is true and the ref is under `refs/heads/`, `refs/remotes/`, `refs/notes/` or a pseudoref; otherwise the tag is the only reversal |

## Reflog boundaries
| Setting / scope | Value |
|---|---|
| `gc.reflogExpire` | Default 90 days; `now` expires all, `never` suppresses |
| `gc.reflogExpireUnreachable` | Default 30 days; the window for commits an operation orphaned |
| `gc.pruneExpire` | Default 2 weeks grace for unreachable objects; `now` disables it |
| Per-pattern override | Both reflog settings accept a `<pattern>` such as `refs/stash` |
| Scope | One reflog per ref per repository, never fetched or shared; logs ref updates only, so uncommitted index/working-tree state has no entry |
| `refs/stash` | Own reflog; `stash drop` removes the entry, leaving the commit unreachable until the next prune |
| Effective values | Read with `git config` in the repo that will run the operation |
