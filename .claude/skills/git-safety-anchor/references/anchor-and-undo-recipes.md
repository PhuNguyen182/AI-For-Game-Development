# Anchor Primitives and Per-Operation Undo

Docs: https://git-scm.com/docs/git-<subcommand> (stash, reset, update-ref, rebase, push, filter-branch); filter-repo: https://github.com/newren/git-filter-repo.

`<utc>` = anchor timestamp; `<sha>` = value `git rev-parse` returned before the operation.

## Primitives
| Primitive | Use |
|---|---|
| `git tag backup/<op>-<utc>` | Named non-moving ref; keeps history reachable from `gc` |
| `git stash create` | Commit object of tracked working tree + index; prints sha, writes no ref, changes nothing. Excludes untracked/ignored files |
| `git stash store -m "<label>" <sha>` | Makes a `create` sha reachable via `refs/stash` so `gc` cannot reclaim it |
| `git rev-parse --verify <ref>` | Resolves to the sha for the undo; non-zero exit if it does not resolve |
| `git cat-file -e <sha>` | Confirms an unreferenced object (a `create` sha) exists |
| `git update-ref <ref> <sha>` | Restores a non-current branch without checkout; logs a reflog line only under `refs/heads/`, `refs/remotes/`, `refs/notes/` or pseudorefs with `core.logAllRefUpdates` |
| `git update-ref -d <ref> <old-oid>` | Deletes a `backup/` tag only if it still holds `<old-oid>` |
| `git status --porcelain` | Stable pre-state of index and working tree |

`git stash push` is a workflow command, never an anchor: it saves changes then rolls the working tree and index back to `HEAD`.

`ORIG_HEAD` is not an anchor: written by the operation (cannot be verified beforehand), one value, overwritten by the next `reset`/`merge`/`pull`/`rebase`, and not set by `checkout`, `commit --amend`, `branch -D`, `stash drop` or `push`. Use it in an undo only if it demonstrably still points where expected.

## Restore from a `stash create` sha
| Form | Restores |
|---|---|
| `git stash apply --index <stash-sha>` | Working tree and staged/unstaged split |
| `git stash apply <stash-sha>` | Working tree only, all unstaged (use if `--index` refuses) |
| `git checkout <stash-sha> -- <path>` | One path |

## Undo — local history and refs
| Operation | Anchor first | Literal undo |
|---|---|---|
| `reset --soft` (moves branch ref only) | tag `backup/reset-<utc>` at `HEAD` | `git reset --soft backup/reset-<utc>` |
| `reset --mixed` (branch ref + index) | tag, plus `stash create` if anything staged | `git reset --mixed backup/reset-<utc>`, then `git stash apply --index <stash-sha>` |
| `reset --hard` (ref, index, working tree; may overwrite untracked files) | tag **and** `stash create` | `git reset --hard backup/reset-<utc>`, then `git stash apply --index <stash-sha>` |
| `rebase <upstream>` | tag `backup/rebase-<utc>` | `git reset --hard backup/rebase-<utc>` |
| `rebase --onto <newbase> <upstream> <branch>` (moves `<branch>` only; other branches in the range keep old commits, so a `HEAD` anchor covers the wrong ref) | one tag `backup/rebase-onto-<utc>-<ref>` per ref `git for-each-ref` shows in the range | `git update-ref refs/heads/<branch> backup/rebase-onto-<utc>-<branch>` |
| `merge <ref>` | tag `backup/merge-<utc>`, plus `stash create` if dirty | `git reset --hard backup/merge-<utc>` |
| `cherry-pick` | tag `backup/cherry-pick-<utc>` | `git reset --hard backup/cherry-pick-<utc>` |
| `commit --amend` | tag `backup/amend-<utc>` | `git reset --hard backup/amend-<utc>` (discard) or `--soft` (keep amended content staged) |
| `branch -d/-D <b>` (`-D` leaves commits reachable from nothing) | record `git rev-parse refs/heads/<b>` as `<sha>` | `git update-ref refs/heads/<b> <sha>` |

`merge/rebase/cherry-pick --abort` work only while the operation is in progress with a conflict pending; once complete, the tag is the only reversal, hence taken before.

## Undo — working tree, stash, remote
| Operation | Anchor first | Literal undo |
|---|---|---|
| `checkout <branch>` | record `git rev-parse --abbrev-ref HEAD` as `<previous-branch>`, plus `stash create` if dirty | `git checkout <previous-branch>` |
| `checkout -- <path>` (destroys unstaged edits no ref named) | `stash create` — the only primitive that captures them | `git checkout <stash-sha> -- <path>` |
| `stash drop` | record `git rev-parse stash@{0}` as `<sha>`, or tag it `backup/stash-<utc>` | `git stash store -m "restored" <sha>` |
| `push <remote> <b>` | record `git rev-parse refs/remotes/<remote>/<b>` | none itself safe; moving the ref back is the force-push row |
| `push --force` (discards commits only that ref named, including ones another clone fetched) | tag `backup/push-force-<utc>` at `refs/remotes/<remote>/<b>`; prefer `--force-with-lease` | `git push --force <remote> backup/push-force-<utc>:refs/heads/<b>` — restores the remote ref only, never another clone's state |
| `filter-repo` (rewrites every commit; refuses outside a fresh clone unless `--force`; auto-shrinks, removing old cruft) | separate `git clone --mirror` before the run; an in-repo tag is not dependable across a repack/prune | `git push --mirror <origin>` from the untouched clone, or re-clone from it |
| `filter-branch` (originals kept under `refs/original/`; a second run overwrites them) | still tag each affected ref | `git update-ref refs/heads/<b> refs/original/refs/heads/<b>` |
