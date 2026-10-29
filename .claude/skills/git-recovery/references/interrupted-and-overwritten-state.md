# Interrupted and Overwritten State

Sources: `git-rebase`, `git-merge`, `git-cherry-pick`, `git-bisect`, `git-status`, `gitglossary` under the `Docs:` base.

## Which operation is in progress

| Under `$(git rev-parse --git-dir)` | Means |
|---|---|
| `rebase-merge/` | Interactive or merge-backend rebase; todo, `done` and `onto` are readable inside (layout undocumented) |
| `rebase-apply/` | `am`-backend rebase or a plain `git am` — presence alone does not tell which |
| `REBASE_HEAD` | The commit the rebase stopped on |
| `MERGE_HEAD` | Uncommitted merge: the next `git commit` creates a merge commit |
| `CHERRY_PICK_HEAD`, `REVERT_HEAD` | Stopped cherry-pick or revert |
| `sequencer/` | Multi-commit cherry-pick or revert |
| `BISECT_LOG` | Bisect open: `HEAD` is bisect's pick; `git bisect reset` returns to the pre-start commit |
| `UU AA DU UD AU UA` in `status --porcelain=v1` | Unmerged entries, whatever the operation |

```sh
gitdir="$(git rev-parse --git-dir)"
for f in MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD REBASE_HEAD BISECT_LOG rebase-merge rebase-apply sequencer; do
  test -e "$gitdir/$f" && echo "present: $f"
done
```

## Resolving it

| Command | Fact that decides |
|---|---|
| `rebase --skip` | **Drops** the current commit from the result |
| `rebase --abort` | Back to the original branch; commits made by `edit`/`exec` steps become unreachable (find them per [reflog-and-unreachable-objects.md](reflog-and-unreachable-objects.md)) |
| `merge --abort` | Full restore only from a clean tree, plus any autostash. Uncommitted changes present at merge start may be lost by the abort itself |
| `merge --continue`, or `git commit` while `MERGE_HEAD` exists | Completes the merge; a merge has no `--skip` |
| `cherry-pick --abort`, `revert --abort` | Undoes every already-applied commit of the sequence |
| `cherry-pick --quit`, `revert --quit` | Clears sequencer state only: applied commits stay, the rest are abandoned with no record |
| `bisect skip` / `bisect reset` | Untestable commit / leave the session |

## Detached `HEAD`

Commits made there are reachable only through `HEAD`; switching away orphans them without warning. Before leaving: `git switch -c <name>`. After: `HEAD`'s reflog, or `fsck` once the entry expired.

## Force-push — where the old commits still live

| Location | Holds them when |
|---|---|
| This clone's `refs/remotes/<remote>/<branch>` reflog | It fetched the old history and the entry is inside `gc.reflogExpireUnreachable` (default 30 days) |
| A local branch or tag here | Still points at the old tip — check `for-each-ref` before the reflog |
| Another clone | It fetched the old history and has not re-fetched; read its reflog there |
| Hosting provider | Provider retention policy, not git — ask the provider, never assume |
| Genuinely nowhere | This clone was created or first fetched after the push; no command here can produce them |

```sh
remote_ref="$(git rev-parse --symbolic-full-name '@{upstream}')"
git reflog show "$remote_ref" --date=iso      # pick the entry just before the forced update, e.g. @{n}
git log --oneline "$remote_ref@{n}" "^$remote_ref"
git branch "recovered-${remote_ref##*/}" "$remote_ref@{n}"
```
Several fetches since the push make `@{1}` the wrong entry.

## Evil merges — a change dropped in conflict resolution

No marker, no error: the merge records a tree that lacks the change. `git show`'s default `--cc` hides a hunk resolved by taking one side wholesale; diff against each parent.

```sh
merge="$(git rev-list --merges -n 1 HEAD)"   # or the suspect merge's sha
git show --cc --stat "$merge"          # hunks differing from every parent = the hand-typed resolution
git diff --stat "$merge^1" "$merge"
git diff --stat "$merge^2" "$merge"    # in ^2 but absent from the merge = dropped
```

**Caveat:** one empty parent diff is normal, not evidence of a clean merge — read both.
