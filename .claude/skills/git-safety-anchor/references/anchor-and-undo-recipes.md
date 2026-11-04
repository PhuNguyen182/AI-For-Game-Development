# Anchor Primitives and Per-Operation Undo

Docs: https://git-scm.com/docs/git-<subcommand> (stash, reset, update-ref, rebase, push, filter-branch); filter-repo: https://github.com/newren/git-filter-repo.

`<utc>` = anchor timestamp as `YYYYMMDDTHHMMSSZ` (no `:`, which a ref name cannot hold); `<sha>` = value `git rev-parse` returned before the operation.

Undos never use a form the hooks block. `reset --keep <ref>` moves branch, index and working tree like `--hard` but refuses instead of overwriting an uncommitted change; after an operation that left the tree clean it is the same reset. Refused, or the row says GD-run → the undo is the exact command under `Needs GD`, for the GD to run.

## Primitives
| Primitive | Use |
|---|---|
| `git tag backup/<op>-<utc>` | Named non-moving ref; keeps history reachable from `gc`. Lightweight, never `-a`: `push --follow-tags` sends annotated tags |
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
| `commit` | record `git rev-parse HEAD` as `<sha>` | `git reset --soft <sha>` (the commit's changes return to the index) |
| `reset --soft` (moves branch ref only) | tag `backup/reset-<utc>` at `HEAD` | `git reset --soft backup/reset-<utc>` |
| `reset --mixed` (branch ref + index; working tree untouched) | tag, plus `stash create` if anything staged | `git reset backup/reset-<utc>`; if anything was staged, then `git read-tree <stash-sha>^2` (the stash's index commit restores the staged state exactly) |
| `reset --hard` (GD-run; ref, index, working tree; may overwrite untracked files) | tag **and** `stash create` | `git reset --keep backup/reset-<utc>`, then `git stash apply --index <stash-sha>` |
| `rebase <upstream>` | tag `backup/rebase-<utc>`; with `--update-refs` or `rebase.updateRefs=true`, also one tag per other branch in the range (it moves them too) | `git reset --keep backup/rebase-<utc>`, plus `git update-ref refs/heads/<b> backup/rebase-<utc>-<b>` per moved branch |
| `rebase --onto <newbase> <upstream> <branch>` (moves `<branch>` only; other branches in the range keep old commits, so a `HEAD` anchor covers the wrong ref) | one tag `backup/rebase-onto-<utc>-<ref>` per ref `git for-each-ref` shows in the range | `git update-ref refs/heads/<branch> backup/rebase-onto-<utc>-<branch>` |
| `merge <ref>` / `pull` | tag `backup/merge-<utc>`, plus `stash create` if dirty | `git reset --keep backup/merge-<utc>` |
| `cherry-pick` / `revert` | tag `backup/<op>-<utc>` | `git reset --keep backup/<op>-<utc>` |
| `commit --amend` | tag `backup/amend-<utc>` | `git reset --keep backup/amend-<utc>` (discard) or `--soft` (keep amended content staged) |
| `branch -d/-D <b>` (`-D` leaves commits reachable from nothing) | record `git rev-parse refs/heads/<b>` as `<sha>` | `git update-ref refs/heads/<b> <sha>` |

`merge/rebase/cherry-pick --abort` work only while the operation is in progress with a conflict pending; once complete, the tag is the only reversal, hence taken before.

## Undo — working tree, stash, remote
| Operation | Anchor first | Literal undo |
|---|---|---|
| `checkout <branch>` / `switch` | record `git rev-parse --abbrev-ref HEAD` as `<previous-branch>` and `git rev-parse HEAD` as `<sha>`, plus `stash create` if dirty | `git checkout <previous-branch>`; when it read `HEAD` (detached), `git checkout --detach <sha>` |
| `checkout -- <path>` / `restore <path>` (destroys unstaged edits no ref named) | `stash create` — the only primitive that captures them | `git checkout <stash-sha> -- <path>` |
| `stash drop` | record `git rev-parse stash@{0}` as `<sha>` | `git stash store -m "restored" <sha>` |
| `stash pop` (apply, then drop) | record `git rev-parse stash@{0}` as `<sha>`, plus `stash create` of the tree before it if dirty | `git stash store -m "restored" <sha>`; `git restore --source=HEAD --staged --worktree -- <paths>` for the paths `git stash show --name-only <sha>` lists; delete the files `git ls-tree -r --name-only <sha>^3` lists (its untracked part, if it has one); then `git stash apply --index <pre-sha>` if the tree was dirty |
| `config <key> <value>` (write) | record `git config --get-all <key>` (empty: unset) and the scope (`--local`/`--global`) | `git config <scope> --replace-all <key> <old>`, or `git config <scope> --unset-all <key>` when it was unset |
| `remote add` / `remote set-url` | record `git remote get-url <name>` (absent: none) | `git remote set-url <name> <old-url>`, or `git remote remove <name>` |
| `branch -f <b> <c>` / `branch -m <old> <new>` | record `git rev-parse refs/heads/<b>` as `<sha>` | `git update-ref refs/heads/<b> <sha>` / `git branch -m <new> <old>` |
| `stash clear` | record `git rev-parse stash@{<n>}` for every `git stash list` entry | `git stash store -m "restored" <sha>` per entry, oldest first |
| `tag -d <t>` | record `git rev-parse refs/tags/<t>` as `<sha>` | `git update-ref refs/tags/<t> <sha>` (restores the exact ref value, annotated or not) |
| `fetch --prune` (deletes remote-tracking refs and their reflogs, the usual trace of a force-pushed tip) | tag `backup/prune-<utc>-<b>` per ref `git fetch --prune --dry-run` lists | `git update-ref refs/remotes/<remote>/<b> backup/prune-<utc>-<b>` |
| `push <remote> <b>` | record the live value: `git ls-remote <remote> refs/heads/<b>` | none itself safe; moving the ref back is the force-push row |
| `push --force` (GD-run; discards commits only that ref named, including ones another clone fetched) | tag `backup/push-force-<utc>` at the `git ls-remote` sha, fetched first so the object exists here | GD-run: `git push --force-with-lease=refs/heads/<b>:<new-sha> <remote> backup/push-force-<utc>:refs/heads/<b>` — restores the remote ref only, never another clone's state |
| `filter-repo` (rewrites every commit; refuses outside a fresh clone unless `--force`; auto-shrinks, removing old cruft) | separate `git clone --mirror` before the run; an in-repo tag is not dependable across a repack/prune | GD-run: push the old refs back from the untouched clone, or re-clone from it. A purge's untouched clone still holds the purged value: delete it once the GD accepts the purge |
| `filter-branch` (originals kept under `refs/original/`; a second run overwrites them) | still tag each affected ref | `git update-ref refs/heads/<b> refs/original/refs/heads/<b>` |
