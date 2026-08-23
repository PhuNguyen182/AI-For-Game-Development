# Finding Lost and Deleted Work — Locating Content That Is No Longer There

Sources: [git log](https://git-scm.com/docs/git-log), [git fsck](https://git-scm.com/docs/git-fsck), [git reflog](https://git-scm.com/docs/git-reflog), [git stash](https://git-scm.com/docs/git-stash), [gitrevisions](https://git-scm.com/docs/gitrevisions), [Maintenance and Data Recovery](https://git-scm.com/book/en/v2/Git-Internals-Maintenance-and-Data-Recovery).
Covers: SKILL.md §4 — "Confirm the evidence is still reachable before reading any of it".

Two different losses look identical from the working tree: content a commit
deliberately removed, and content whose commit is no longer reachable from any
ref. The first is found by walking history; the second by walking the object
database, because the commit is still there and simply nothing points at it.
This file locates and reads that content — restoring it is `git-recovery`'s
scope, not this skill's.

- [Which loss is it](#which-loss-is-it)
- [Hunting the deleting commit](#hunting-the-deleting-commit)
- [Reading pre-deletion content](#reading-pre-deletion-content)
- [Instruments for unreachable objects](#instruments-for-unreachable-objects)
- [What each instrument can and cannot surface](#what-each-instrument-can-and-cannot-surface)
- [Dropped stashes](#dropped-stashes)

## Which loss is it

| Symptom | The loss | Instrument | Source |
|---|---|---|---|
| A path existed in an older commit and does not exist at `HEAD` | A commit removed it, and that commit is still reachable | `git log --all --full-history --diff-filter=D` | [git log](https://git-scm.com/docs/git-log) |
| A commit sha is known but resolves to nothing on any branch | A rebase, squash, amend, or force-push moved the refs away from it | `git reflog --all`, then `git fsck` | [git reflog](https://git-scm.com/docs/git-reflog) |
| The work was committed but the branch is gone | The commit is unreachable but still in the object database until `gc` prunes it | `git fsck --lost-found --unreachable --dangling` | [git fsck](https://git-scm.com/docs/git-fsck) |
| The work was stashed and the stash is gone | The stash commit is unreachable; `stash` has no reflog entry left to name it | `git fsck --unreachable` filtered to commits | [git stash](https://git-scm.com/docs/git-stash) |
| The work was never committed or staged | Nothing was ever written to the object database; no instrument here can find it | none — report it as unrecoverable | [git fsck](https://git-scm.com/docs/git-fsck) |

## Hunting the deleting commit

| Option | Why it is needed | Source |
|---|---|---|
| `--diff-filter=D` | Selects only commits where the path was **deleted**, instead of every commit that touched it | [git log](https://git-scm.com/docs/git-log) |
| `--full-history` | **Mandatory.** By default a merge TREESAME to one parent is followed down that parent only, so a merge that resolved a conflict by dropping the path is pruned from the walk and the deletion appears never to have happened | [History Simplification](https://git-scm.com/docs/git-log#_history_simplification) |
| `--all` | The deleting commit may sit on a branch other than the current one | [git rev-list](https://git-scm.com/docs/git-rev-list) |
| `--simplify-merges` | Narrows a `--full-history` result that returned too many merges, at the cost of walking the whole graph | [History Simplification](https://git-scm.com/docs/git-log#_history_simplification) |
| `--` before the pathspec | Disambiguates a path from a ref of the same name, which matters most when the path no longer exists and cannot be checked | [gitrevisions](https://git-scm.com/docs/gitrevisions) |

```sh
git log --all --full-history --diff-filter=D -- .
```

**Critical caveat**: omitting `--full-history` does not produce an error or an
empty result — it produces a *plausible* result that skips the merge. A
deletion hunt that returned one obvious commit without `--full-history` has not
established that no other commit also removed the path.

## Reading pre-deletion content

| Form | What it produces | Source |
|---|---|---|
| Why the parent, not the commit | The deleting commit's own tree no longer holds the path, so the content is read out of its parent | [gitrevisions](https://git-scm.com/docs/gitrevisions) |
| `<sha>^:<path>` | The blob at `<path>` in the **first parent** of `<sha>` — `^` is the first parent and `:` names a path inside a tree-ish | [gitrevisions](https://git-scm.com/docs/gitrevisions) |
| `<sha>^<n>:<path>` | The same from the `<n>`th parent, which is what a merge that dropped the path on one side requires | [gitrevisions](https://git-scm.com/docs/gitrevisions) |
| `git show <sha>^:<path>` | Prints that blob to stdout | [gitrevisions](https://git-scm.com/docs/gitrevisions) |
| `git cat-file -p <sha>^:<path>` | Pretty-prints the object by type; verified to accept the extended `<rev>:<path>` form against git 2.55, although the man page presents path addressing under `--textconv`/`--filters` | [git cat-file](https://git-scm.com/docs/git-cat-file) |
| `git cat-file -t` / `-s` | The object's type and its size in bytes — the cheap way to confirm a blob is the expected file before printing it | [git cat-file](https://git-scm.com/docs/git-cat-file) |
| `git show <sha>^:<dir>` | The tree listing for a directory, which recovers the names of files a directory-wide deletion removed | [gitrevisions](https://git-scm.com/docs/gitrevisions) |

```sh
git show HEAD^:.gitignore
```

## Instruments for unreachable objects

| Instrument | What it reports | Source |
|---|---|---|
| `git reflog --all` | Every recorded update to every ref, including the moves a rebase or force-push made — the fastest route to a sha that no ref names any more | [git reflog](https://git-scm.com/docs/git-reflog) |
| `ORIG_HEAD` | The commit `HEAD` pointed at before the last operation that moved it drastically; a single-step undo target with no searching | [gitrevisions](https://git-scm.com/docs/gitrevisions) |
| `git fsck --unreachable` | Objects present in the database but reachable from no ref, tag, branch, index, or reflog | [git fsck](https://git-scm.com/docs/git-fsck) |
| `git fsck --dangling` | Objects never *directly* used; on by default, and a dangling commit may be a root node | [git fsck](https://git-scm.com/docs/git-fsck) |
| `git fsck --lost-found` | Writes dangling objects into `.git/lost-found/commit/` and `.git/lost-found/other/`, with blob **contents** written into the file rather than just the name | [git fsck](https://git-scm.com/docs/git-fsck) |
| `git fsck --no-reflogs` | Stops reflog-only references from counting as reachable, which isolates commits that used to be on a ref but are now held solely by the reflog | [git fsck](https://git-scm.com/docs/git-fsck) |
| `git fsck --cache` | Treats objects recorded in the index as reachable head nodes, so staged-but-uncommitted content is not reported as lost | [git fsck](https://git-scm.com/docs/git-fsck) |
| `git fsck --root` | Reports root commits, which distinguishes a genuinely orphaned history from a detached tip | [git fsck](https://git-scm.com/docs/git-fsck) |
| `gc.reflogExpire` / `gc.reflogExpireUnreachable` | 90 days and 30 days by default — the window in which the reflog still holds an unreachable commit | [git reflog](https://git-scm.com/docs/git-reflog) |

```sh
git fsck --lost-found --unreachable --dangling
```

## What each instrument can and cannot surface

**Critical caveat**: `fsck` finds objects that **were written** into the object
database and later became unreachable. Anything never committed and never
staged was never written, and no instrument here will produce it — which is the
distinction that decides whether a search is worth running at all.

| Instrument | Can surface | Cannot surface | Source |
|---|---|---|---|
| `git log --diff-filter=D --full-history --all` | Deletions on any reachable branch, including those inside merges | Anything whose commit is no longer reachable from a ref | [History Simplification](https://git-scm.com/docs/git-log#_history_simplification) |
| `git reflog --all` | Ref positions this clone recorded, within the expiry window | Positions from another clone — reflogs are per-repository and are not transferred by clone or fetch | synthesized |
| `git fsck --unreachable` | Committed objects now reachable from nothing | Objects already pruned by `gc`, and anything never written | [git fsck](https://git-scm.com/docs/git-fsck) |
| `git fsck --lost-found` | The same objects, materialised as files with blob contents | Any relationship between them — file names and directory structure are not restored | [git fsck](https://git-scm.com/docs/git-fsck) |
| `git fsck --cache` | Staged-but-uncommitted blobs, by treating the index as a root | Working-tree edits that were never `git add`ed | [git fsck](https://git-scm.com/docs/git-fsck) |
| `git fsck --connectivity-only` | Missing or unconnected commits and trees, faster | Corruption inside blob contents, which it does not read | [git fsck](https://git-scm.com/docs/git-fsck) |
| `git stash list` | Stash entries still referenced by the stash reflog | Entries dropped or cleared | [git stash](https://git-scm.com/docs/git-stash) |

**Critical caveat**: `fsck` returning nothing is not proof the work never
existed — it is equally consistent with `gc` having already pruned it, or with
the work living only in another clone's object database. Report which of those
was ruled out and which was not, rather than reporting the loss as permanent.

## Dropped stashes

Upstream documents this incantation for listing stash commits that survive
unreachably after the entry was dropped or cleared:

```sh
git fsck --unreachable | grep commit | cut -d\  -f3 | xargs git log --merges --no-walk --grep=WIP
```

| Element | Why it is there | Source |
|---|---|---|
| The search is possible at all | A dropped entry has no reflog entry left to name it, but its commit stays in the object database until `gc` runs | [git stash](https://git-scm.com/docs/git-stash) |
| `--unreachable` filtered to `commit` | A stash entry is a commit object; blobs and trees in the output are not entries | [git stash](https://git-scm.com/docs/git-stash) |
| `--merges` | A stash entry is a merge commit — it records the index state as a second parent | [git stash](https://git-scm.com/docs/git-stash) |
| `--no-walk` | Shows only the listed commits, without traversing their ancestors | [git rev-list](https://git-scm.com/docs/git-rev-list) |
| `--grep=WIP` | Matches the default `WIP on <branch>` subject; a stash created with an explicit message will not match and needs the filter widened | [git stash](https://git-scm.com/docs/git-stash) |
| `stash@{0}` naming | `git stash list` names surviving entries with the branch that was current and the commit they were based on | [git stash](https://git-scm.com/docs/git-stash) |

Once the object is located, the finding names the sha and the instrument that
found it; the pre-deletion content is read with the forms above, and any
restore, cherry-pick, or ref recreation is routed to `git-recovery`. Whether
the located content is a credential, and whether it is still reachable
elsewhere, is [secret-history-archaeology.md](secret-history-archaeology.md).
