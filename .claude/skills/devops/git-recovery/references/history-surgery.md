# History Surgery — Deliberate Rewriting, Kept Separate From Repair

Sources: [git-rebase](https://git-scm.com/docs/git-rebase), [git-merge](https://git-scm.com/docs/git-merge), [git-commit](https://git-scm.com/docs/git-commit), [git-worktree](https://git-scm.com/docs/git-worktree), [git-filter-branch](https://git-scm.com/docs/git-filter-branch), [git-push](https://git-scm.com/docs/git-push), [Pro Git — Rewriting History](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History).

Covers: SKILL.md §4 — "Keep deliberate rewriting separate from repair", "Prefer `git filter-repo` over `git filter-branch`".

Every technique here produces new commits with new shas, which is the opposite
of what a repair wants: a repair restores the shas the requester already had.
The instruments overlap with recovery — `rebase --abort`, `ORIG_HEAD`, the
reflog — but the intent does not, and that distinction is what decides whether
an operation needs authorization at all. Recovering from a rewrite that went
wrong is [reflog-and-unreachable-objects.md](reflog-and-unreachable-objects.md);
detecting one already mid-flight is
[interrupted-and-overwritten-state.md](interrupted-and-overwritten-state.md).

## Contents

- [Interactive rebase todo verbs](#interactive-rebase-todo-verbs)
- [Rebasing onto a different base](#rebasing-onto-a-different-base)
- [Splitting one commit into several](#splitting-one-commit-into-several)
- [Collapsing history — squash, fixup, autosquash](#collapsing-history--squash-fixup-autosquash)
- [Worktrees — a second checkout instead of a stash](#worktrees--a-second-checkout-instead-of-a-stash)
- [Subtree](#subtree)
- [`filter-repo` versus `filter-branch`](#filter-repo-versus-filter-branch)

## Interactive rebase todo verbs

| Verb | Effect | Source |
|---|---|---|
| `pick` | Use the commit as-is — the default for every line | [git-rebase](https://git-scm.com/docs/git-rebase) |
| `reword` | Use the commit, but edit its log message; content untouched | [git-rebase](https://git-scm.com/docs/git-rebase) |
| `edit` | Use the commit, then stop for amending. The stop is what makes commit splitting possible | [git-rebase](https://git-scm.com/docs/git-rebase) |
| `squash` | Meld into the previous commit, opening an editor with both messages | [git-rebase](https://git-scm.com/docs/git-rebase) |
| `fixup` | Like `squash`, but discard this commit's log message. `fixup -C` keeps only this commit's message instead; `fixup -c` opens the merged message in an editor | [git-rebase](https://git-scm.com/docs/git-rebase) |
| `drop` | Remove the commit. Deleting the line entirely does the same thing, which is why an accidentally truncated todo list silently drops commits | [git-rebase](https://git-scm.com/docs/git-rebase) |
| `exec` | Run a shell command at that point in the sequence — the mechanism for running a build or test between every commit | [git-rebase](https://git-scm.com/docs/git-rebase) |
| `break` | Stop rebasing at that point — "same as `edit` but without cherry-picking", so it pauses without a commit to amend | [git-rebase](https://git-scm.com/docs/git-rebase) |
| `label`, `reset`, `merge` | Name a position, move `HEAD` to one, and recreate a merge — the verbs `--rebase-merges` emits to preserve a merge topology instead of flattening it | [git-rebase](https://git-scm.com/docs/git-rebase) |

## Rebasing onto a different base

| Form | Semantics | Source |
|---|---|---|
| `git rebase <upstream>` | Replays commits not in `<upstream>` on top of `<upstream>`; the starting point defaults to `<upstream>` itself | [git-rebase](https://git-scm.com/docs/git-rebase) |
| `git rebase --onto <newbase> <since> <branch>` | `--onto` is the "starting point at which to create the new commits… May be any valid commit, and not just an existing branch name". `<since>` bounds which commits move, so this is the form that transplants a range without dragging its old base along | [git-rebase `--onto`](https://git-scm.com/docs/git-rebase) |
| `git rebase --onto <newbase> A...B` | `A...B` is "a shortcut for the merge base of A and B if there is exactly one merge base", with at most one side omittable (defaulting to `HEAD`) | [git-rebase `--onto`](https://git-scm.com/docs/git-rebase) |
| `git rebase --rebase-merges` | Rebuilds merge commits rather than flattening them, using the `label`/`reset`/`merge` todo verbs | [git-rebase](https://git-scm.com/docs/git-rebase) |
| `--continue` / `--skip` / `--abort` | Resolve an interrupted rebase; `--skip` **drops** the current patch from the result rather than deferring it — see [interrupted-and-overwritten-state.md](interrupted-and-overwritten-state.md) | [git-rebase](https://git-scm.com/docs/git-rebase) |

## Splitting one commit into several

Upstream documents the exact mechanism: mark the commit `edit`, then "execute
`git reset HEAD^`. The effect is that the `HEAD` is rewound by one, and the index
follows suit. However, the working tree stays the same." From there each partial
`git add` plus `git commit` produces one of the split commits, repeated "until
your working tree is clean", then `git rebase --continue`.

| Step's role | Command | Why it works | Source |
|---|---|---|---|
| Reach the commit | `git rebase -i <commit>^` with that line marked `edit` | "any commit range will do, as long as it contains that commit" | [git-rebase — splitting commits](https://git-scm.com/docs/git-rebase) |
| Undo the commit, keep the files | `git reset HEAD^` | Mixed reset moves `HEAD` and the index back but leaves the working tree, so the changes become unstaged material to redistribute | [git-reset](https://git-scm.com/docs/git-reset) |
| Build each piece | `git add -p` then `git commit` | Stages a subset of the hunks per commit; repeat while anything remains unstaged | [git-add](https://git-scm.com/docs/git-add) |
| Resume | `git rebase --continue` | Replays the remaining todo entries onto the new commits | [git-rebase](https://git-scm.com/docs/git-rebase) |

```sh
split_target="$(git rev-parse HEAD~1)"
git rebase -i "$split_target^"
git reset "$split_target^"
git add -p
git commit -m "First half of the split"
git add -A
git commit -m "Second half of the split"
git rebase --continue
```

## Collapsing history — squash, fixup, autosquash

| Instrument | Effect | Use when | Source |
|---|---|---|---|
| `git merge --squash <branch>` | Produces "the working tree and index state as if a real merge happened… but do[es] not actually make a commit, move the `HEAD`, or record `$GIT_DIR/MERGE_HEAD`" — so the next commit is an ordinary one, not a merge | A whole branch should land as one commit with no merge commit and no rewritten branch | [git-merge `--squash`](https://git-scm.com/docs/git-merge) |
| `git commit --fixup=<commit>` | Creates a `fixup!` commit changing `<commit>`'s content but leaving its message untouched | A correction is known now but the rewrite will happen later, in one pass | [git-commit `--fixup`](https://git-scm.com/docs/git-commit) |
| `git commit --fixup=amend:<commit>` | Creates an `amend!` commit replacing both content **and** log message, with the original message opened for refinement | The message was wrong as well as the content | [git-commit `--fixup`](https://git-scm.com/docs/git-commit) |
| `git commit --fixup=reword:<commit>` | Shorthand for `--fixup=amend:<commit> --only` — message-only, ignoring staged changes | Only the message needs replacing | [git-commit `--fixup`](https://git-scm.com/docs/git-commit) |
| `git commit --squash=<commit>` | Creates a `squash!` commit whose message will be merged into the target's | The correction's own message should survive into the combined message | [git-commit `--squash`](https://git-scm.com/docs/git-commit) |
| `git rebase --autosquash` | Recognizes `squash!`, `fixup!` and `amend!` titles, rewrites their todo actions to `squash`/`fixup`/`fixup -C`, and moves them "right after the commit they modify" | The rewrite pass that consumes the markers above. Pair with `--interactive` to review the reordered list first | [git-rebase `--autosquash`](https://git-scm.com/docs/git-rebase) |

Upstream notes that "neither `fixup!` nor `amend!` commits change authorship" of
the target when applied by `--autosquash`, so the collapsed commit keeps its
original author — relevant when a rewrite must not reassign attribution.

## Worktrees — a second checkout instead of a stash

| Command | Effect | Source |
|---|---|---|
| `git worktree add <path> [<commit-ish>]` | "Create a worktree at *<path>* and checkout *<commit-ish>* into it. The new worktree is linked to the current repository, sharing everything except per-worktree files such as `HEAD`, `index`, etc." | [git-worktree `add`](https://git-scm.com/docs/git-worktree) |
| `git worktree list` | Lists each worktree with its checked-out revision and branch, or `detached HEAD`, plus `locked` and `prunable` status. `--porcelain` gives the machine form | [git-worktree `list`](https://git-scm.com/docs/git-worktree) |
| `git worktree remove <path>` | "Only clean worktrees (no untracked files and no modification in tracked files) can be removed. Unclean worktrees or ones with submodules can be removed with `--force`. The main worktree cannot be removed" | [git-worktree `remove`](https://git-scm.com/docs/git-worktree) |
| `git worktree prune` | Clears stale entries for worktrees "whose working trees are missing" — the cleanup after a directory was deleted by hand instead of via `remove` | [git-worktree `prune`](https://git-scm.com/docs/git-worktree) |
| Same branch in two worktrees | Refused: `add` "refuses to create a new worktree when *<commit-ish>* is a branch name and is already checked out by another worktree", overridable only with `--force` | [git-worktree `add`](https://git-scm.com/docs/git-worktree) |

Why this belongs in a rewriting file rather than a repair one: a long
`rebase -i` occupies the working tree for its whole duration, and a worktree
gives the reviewer a second clean checkout of the pre-rewrite tip to compare
against without aborting the rebase or stashing anything.

```sh
git worktree add ../review-before-rewrite "$(git rev-parse HEAD)"
git worktree list --porcelain
git worktree remove ../review-before-rewrite
```

## Subtree

| Aspect | Fact | Source |
|---|---|---|
| Reading another project into a subdirectory | `git read-tree --prefix=<dir>/ -u <branch>` "reads the root tree of one branch into your current staging area and working directory", placing it under `<dir>` — the primitive the whole approach rests on | [Pro Git — Subtree Merging](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging#_subtree_merging) |
| Pulling later upstream changes in | `git merge --squash -s recursive -Xsubtree=<dir>` merges the upstream branch into the subdirectory as one commit | [Pro Git — Subtree Merging](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging#_subtree_merging) |
| The `git subtree` porcelain | It ships in the git source tree's `contrib/` directory and has **no page under `git-scm.com/docs`** — that URL returns 404, verified. Confirm the installed git actually provides the subcommand before proposing it, per [root-links.md](root-links.md) | [root-links.md](root-links.md) |

## `filter-repo` versus `filter-branch`

Upstream's own `git filter-branch` page opens with the verdict, quoted in full
because it is the whole basis for the preference: "*git filter-branch* has a
plethora of pitfalls that can produce non-obvious manglings of the intended
history rewrite (and can leave you with little time to investigate such problems
since it has such abysmal performance). These safety and performance issues
cannot be backward compatibly fixed and as such, its use is not recommended.
Please use an alternative history filtering tool such as
[git filter-repo](https://github.com/newren/git-filter-repo/)."

| Aspect | `git filter-repo` | `git filter-branch` | Source |
|---|---|---|---|
| Upstream status | The recommended alternative, named by the git documentation itself | "its use is not recommended" | [git-filter-branch WARNING](https://git-scm.com/docs/git-filter-branch) |
| Bundled with git | **No** — a separate tool, installed independently; it is not available merely because git is | Yes, part of git | [git-filter-repo](https://github.com/newren/git-filter-repo) |
| Correctness | Documented as not suffering the safety problems of `filter-branch` | Pitfalls that "produce non-obvious manglings of the intended history rewrite", catalogued in the page's own SAFETY section | [git-filter-branch](https://git-scm.com/docs/git-filter-branch) |
| Performance | Documented as not suffering the performance problems | "abysmal performance", which upstream ties directly to the safety risk — a slow rewrite leaves little time to notice it went wrong | [git-filter-branch PERFORMANCE](https://git-scm.com/docs/git-filter-branch) |
| Migration path for existing tooling | Ships `filter-lamely`, a drop-in `filter-branch` replacement that "suffers from the same safety issues" but "ameliorates the performance issues somewhat" | — | [git-filter-branch WARNING](https://git-scm.com/docs/git-filter-branch) |
| When `filter-branch` is still the answer | Only when `filter-repo` cannot be installed, and then only after reading the SAFETY and PERFORMANCE sections upstream directs the reader to | — | [git-filter-branch](https://git-scm.com/docs/git-filter-branch) |

**Critical caveat**: every technique in this file rewrites shas — a rebase, a
squash, a split, a filter and an `--autosquash` pass all produce new commit
objects, so no branch position survives them. Any branch that has already been
pushed therefore requires the radius-3 authorization path `git-safety-anchor`
defines, obtained for that specific operation in the current conversation. The
publishing step is what makes it irreversible for everyone else:
`git push --force` "can cause the remote repository to lose commits", while
`--force-with-lease` at least fails rather than overwriting when the remote ref
is not the value expected ([git-push](https://git-scm.com/docs/git-push)).
