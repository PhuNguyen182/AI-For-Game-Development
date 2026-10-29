# Finding Lost and Deleted Work

Locates and reads content; restoring it is `git-recovery`'s job.

## Which loss
| Symptom | Instrument |
|---|---|
| Path in an older commit, absent at `HEAD`; removing commit still reachable | `git log --all --full-history --diff-filter=D` |
| Known sha resolves on no branch (rebase, squash, amend, force-push) | `git reflog --all`, then `git fsck` |
| Committed work, branch gone | `git fsck --lost-found --unreachable --dangling` |
| Stashed work, stash gone | `git fsck --unreachable` filtered to commits (below) |
| Never committed or staged | Never written to the object database: unrecoverable, report it |

## History simplification
Default path-limited logs follow only one parent of a merge TREESAME to it, silently dropping the other side. `--full-history` follows all parents; `--simplify-merges` then trims merges nobody contributed to (walks the whole graph); `--ancestry-path[=<commit>]` limits to commits descended from `<commit>`. `--all` covers every ref but not reflogs; `--reflog` adds objects only a reflog mentions.

## Hunting the deleting commit
```sh
git log --all --full-history --diff-filter=D -- <path>
```
- `--full-history` is mandatory: without it a merge that dropped the path is pruned and the result looks plausible but incomplete. One obvious commit does not show no other removed the path.
- `--all` because the deleter may be on another branch. `--` separates path from ref (the path no longer exists).

## Reading pre-deletion content
The deleting commit's tree lacks the path, so read its parent.
- `git show <sha>^:<path>`: first parent; `<sha>^<n>:<path>` for the n-th parent (a merge that dropped it on one side).
- `git show <sha>^:<dir>`: tree listing, recovers names after a directory deletion.
- `git cat-file -p <sha>^:<path>` accepts the same form (verified on git 2.55; the man page frames it under `--textconv`/`--filters`). `cat-file -t`/`-s` confirm type and size before printing.

## Unreachable objects
| Instrument | Reports |
|---|---|
| `git reflog --all` | Every recorded ref update in this clone, incl. rebase/force-push moves |
| `ORIG_HEAD` | `HEAD` before the last drastic move |
| `git fsck --unreachable` | Objects reachable from no ref, tag, branch, index or reflog |
| `git fsck --dangling` | Objects never directly used (default) |
| `git fsck --lost-found` | Writes dangling objects to `.git/lost-found/{commit,other}/` with blob contents; names and structure not restored |
| `git fsck --no-reflogs` | Isolates commits held solely by a reflog |
| `git fsck --cache` | Counts index objects reachable, so staged work is not reported lost; unstaged edits remain unfindable |
| `git fsck --root` | Root commits (orphaned history vs detached tip) |
| `git fsck --connectivity-only` | Faster; missing/unconnected commits and trees, not blob corruption |

Reflog expiry defaults: `gc.reflogExpire` 90 days, `gc.reflogExpireUnreachable` 30 days. Reflogs are per-clone and not transferred by clone or fetch (inferred, not stated upstream), so another clone's positions are invisible.

`fsck` finds only objects that were written. Empty output is equally consistent with `gc` having pruned them or the work living in another clone: report which was ruled out, not "permanent loss".

## Dropped stashes
```sh
git fsck --unreachable | grep commit | cut -d\  -f3 | xargs git log --merges --no-walk --grep=WIP
```
A dropped stash keeps its commit until `gc`. A stash entry is a merge commit (index state is the second parent), hence `--merges`. `--grep=WIP` matches only the default `WIP on <branch>` subject; widen it for stashes with a custom message. Surviving entries: `git stash list`.

Report the sha and the instrument that found it; route restore/cherry-pick/ref recreation to `git-recovery`. Credentials: [secret-history-archaeology.md](secret-history-archaeology.md).
