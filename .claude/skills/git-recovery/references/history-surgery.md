# History Surgery

Sources: `git-rebase`, `git-merge`, `git-commit`, `git-filter-branch` under the `Docs:` base; [subtree] https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging#_subtree_merging.

Every technique here mints new shas; no branch position survives it.

| Technique | Fact that decides |
|---|---|
| `rebase -i` todo list | Deleting a line drops that commit, same as `drop` — a truncated list silently loses commits |
| Split a commit | Mark it `edit`, `git reset HEAD^` (index rewinds, work tree stays), then `git add <paths>` + `commit` per part until clean, `rebase --continue`. A split inside one file: write the part as a patch and `git apply --cached <patch>`; never `add -p` (no terminal) |
| `git merge --squash <branch>` | Writes no `MERGE_HEAD`: the next commit is an ordinary one — a branch lands as one commit without rewriting it |
| `commit --fixup=<c>` / `--fixup=amend:<c>` / `--fixup=reword:<c>` / `--squash=<c>` | Content only / content and message / message only / messages merged — consumed by `rebase -i --autosquash`, which keeps the target's original author |
| `git subtree` | Lives in git's `contrib/` with no doc page — confirm the installed git provides it. Otherwise `read-tree --prefix=<dir>/ -u <branch>`, then `merge --squash -s recursive -Xsubtree=<dir>` [subtree] |
| Path purge | Use `filter-repo` (not bundled with git — confirm installed); upstream deprecates `filter-branch`; use it only if `filter-repo` cannot be installed |

## Without an editor
No terminal is attached and `GIT_EDITOR=true`: a bare `rebase -i` replays the todo list unchanged and reports success with nothing squashed or dropped. Write the whole todo list to a file outside the repo (every commit of the range, oldest first, `pick`/`fixup`/`squash`/`drop`/`edit` per line), then:
```sh
GIT_SEQUENCE_EDITOR="cp '<todo-file>'" git rebase -i <base>
```
`--fixup`/`--squash` commits need no todo file: `GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash <base>` (git 2.56 also honours `git rebase --autosquash <base>` without `-i`; confirm on the installed version). Verify with `git log --format='%h %s' <base>..HEAD` against the todo list before reporting.

## Secret or PII purge
Runs only on a `cto` plan from `secret-exposure-response` (rotated and verified dead wherever rotation exists; a value that cannot be invalidated, or PII, is why the purge runs at all) plus the GD's authorisation quoted verbatim in the brief. `filter-repo` is not bundled and is a third-party install: `security-reviewer` clears it first. The rewrite runs here; the force-push is GD-run.

1. Record the remote's refs outside every repo: `git ls-remote --heads --tags <url> > <dir>/pre-refs.txt`. Ask the GD to freeze pushes until step 5.
2. `git clone --mirror <url> <dir>/purge.git`, plus a second untouched `--mirror` clone as the anchor. Never purge the working clone: its stashes, reflogs and unpushed branches still hold the value.
3. In `purge.git`: a whole file → `git filter-repo --invert-paths --path <path>`; a value inside a kept file → `git filter-repo --replace-text <expr-file>`, one `regex:<pattern>==>REDACTED` line per value, never the literal; a value in a commit or tag message → add `--replace-message <expr-file>` (same format; confirm both options with `git filter-repo -h`). The expressions file lives outside every repo and is deleted after.
4. Verify in `purge.git` before anything leaves it: `git log --all --format=%H -- <path>` (file) or `git log --all --format=%H -G'<pattern>'` (value) prints nothing, `git rev-list --all | xargs git grep -l -E -e '<pattern>'` prints nothing, and the message sweep in `git-forensics` → `references/secret-history-archaeology.md` prints nothing. Report the sweep, never the value.
5. Hand the GD the push. `filter-repo` removes `origin` on purpose: `git remote add origin <url>`; `git ls-remote --heads --tags origin` must equal `pre-refs.txt` (anything new: stop, redo from step 1); then `git push --force origin 'refs/heads/*:refs/heads/*' 'refs/tags/*:refs/tags/*'`. Never `--mirror`: it deletes refs pushed since the clone and fails on host-hidden refs such as `refs/pull/*`.
6. Report what the push does not reach, every one: host pull-request refs and caches (host support request), forks, CI caches, the LFS object on the server for a purged LFS file (host-side delete), every other clone (re-clone; a `pull` merges the old history back). Delete the anchor clone once the GD accepts the purge: it still holds the value.

## Binaries committed before LFS
| Command | Fact that decides |
|---|---|
| `git lfs migrate info --everything --top=20` | Read-only: which types and sizes sit in history; decides whether a rewrite is worth it |
| `git lfs migrate import --no-rewrite --message="<subject>" <path>...` | One new commit converts the current files to pointers; history keeps the old blobs. Radius 2: no rewrite, no force-push; the default when only the working set matters |
| `git lfs migrate import --everything --include="<patterns>"` | Rewrites every local ref (radius 3), with the steps of a purge: fresh clone, anchor clone, verify (`git lfs ls-files`, `migrate info` shows the types gone from history), GD-run force-push, every other clone re-clones. `--include` patterns match the `.gitattributes` lines it writes |

