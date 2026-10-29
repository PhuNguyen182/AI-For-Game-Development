# History Surgery

Sources: `git-rebase`, `git-merge`, `git-commit`, `git-filter-branch` under the `Docs:` base; [subtree] https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging#_subtree_merging.

Every technique here mints new shas; no branch position survives it.

| Technique | Fact that decides |
|---|---|
| `rebase -i` todo list | Deleting a line drops that commit, same as `drop` — a truncated list silently loses commits |
| Split a commit | Mark it `edit`, `git reset HEAD^` (index rewinds, work tree stays), `add -p` + `commit` until clean, `rebase --continue` |
| `git merge --squash <branch>` | Writes no `MERGE_HEAD`: the next commit is an ordinary one — a branch lands as one commit without rewriting it |
| `commit --fixup=<c>` / `--fixup=amend:<c>` / `--fixup=reword:<c>` / `--squash=<c>` | Content only / content and message / message only / messages merged — consumed by `rebase -i --autosquash`, which keeps the target's original author |
| `git subtree` | Lives in git's `contrib/` with no doc page — confirm the installed git provides it. Otherwise `read-tree --prefix=<dir>/ -u <branch>`, then `merge --squash -s recursive -Xsubtree=<dir>` [subtree] |
| Path purge | Use `filter-repo` (not bundled with git — confirm installed); upstream deprecates `filter-branch`; use it only if `filter-repo` cannot be installed |
