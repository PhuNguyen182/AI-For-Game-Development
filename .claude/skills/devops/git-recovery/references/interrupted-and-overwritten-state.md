# Interrupted and Overwritten State — Mid-Operation, Detached, and Force-Pushed

Sources: [git-rebase](https://git-scm.com/docs/git-rebase), [git-merge](https://git-scm.com/docs/git-merge), [git-cherry-pick](https://git-scm.com/docs/git-cherry-pick), [git-revert](https://git-scm.com/docs/git-revert), [git-bisect](https://git-scm.com/docs/git-bisect), [git-status](https://git-scm.com/docs/git-status), [git-push](https://git-scm.com/docs/git-push), [gitglossary](https://git-scm.com/docs/gitglossary).

Covers: SKILL.md §4 — "Establish the actual repository state before choosing a repair", "Finish or abandon an interrupted operation before attempting anything else", "Treat a force-pushed remote branch as gone from this clone unless a local ref still holds it".

The same symptom — a conflicted index, a branch pointing somewhere unexpected —
has a different repair depending on which operation is mid-flight, and the
git directory names that operation unambiguously while the requester's
description often does not. Reading a *ref position* back after the state is
resolved belongs to [reflog-and-unreachable-objects.md](reflog-and-unreachable-objects.md);
producing the pre-repair anchor belongs to `git-safety-anchor`.

## Contents

- [Detecting the operation from the git directory](#detecting-the-operation-from-the-git-directory)
- [Resolving each operation](#resolving-each-operation)
- [What `--abort` restores and what it cannot](#what---abort-restores-and-what-it-cannot)
- [Detached `HEAD`](#detached-head)
- [Force-push overwrite — where the old objects still live](#force-push-overwrite--where-the-old-objects-still-live)
- [Evil merges — a merge whose content matches neither parent](#evil-merges--a-merge-whose-content-matches-neither-parent)

## Detecting the operation from the git directory

| Path under the git directory | Operation it means is in progress | Source |
|---|---|---|
| `rebase-merge/` | An interactive or merge-backend rebase — the todo list, `done` list, and `onto` sha live inside it, so the remaining steps are readable without guessing | synthesized (from the [git-rebase](https://git-scm.com/docs/git-rebase) backend description; upstream does not document this directory's layout) |
| `rebase-apply/` | An `am`-backend rebase, or a plain `git am` — the two share this directory, so its presence alone does not distinguish them | synthesized (see [git-am](https://git-scm.com/docs/git-am)) |
| `REBASE_HEAD` | The commit the rebase stopped on, addressable as a revision while the rebase is unfinished | synthesized (not named on the [git-rebase](https://git-scm.com/docs/git-rebase) page) |
| `MERGE_HEAD` | A merge that has not been committed. Upstream describes it as what causes "the next `git commit` command to create a merge commit" — which is why committing before resolving produces a merge, not an ordinary commit | [git-merge `--squash`](https://git-scm.com/docs/git-merge) |
| `CHERRY_PICK_HEAD` | A stopped cherry-pick; the ref "is set to point at the commit that introduced the change that is difficult to apply" | [git-cherry-pick](https://git-scm.com/docs/git-cherry-pick) |
| `REVERT_HEAD` | A stopped revert — the revert counterpart of the row above | synthesized (not named on the [git-revert](https://git-scm.com/docs/git-revert) page) |
| `sequencer/` | A multi-commit cherry-pick or revert sequence; `--continue` "continue[s] the operation in progress using the information in `.git/sequencer`" | [git-cherry-pick](https://git-scm.com/docs/git-cherry-pick) |
| `BISECT_LOG` | A bisect session is open, so `HEAD` is on a bisect-chosen commit rather than anywhere the requester put it. `git bisect log` prints the session and `git bisect reset` returns the tree "to the commit that was checked out before `git bisect start`" | synthesized filename; behaviour from [git-bisect](https://git-scm.com/docs/git-bisect) |
| Unmerged index entries | Conflicts, independent of which operation caused them — `git status` reports them with two-letter codes (`UU` both modified, `AA` both added, `DU`/`UD` deleted by us/them, `AU`/`UA` added by us/them) | [git-status short format](https://git-scm.com/docs/git-status) |

```sh
gitdir="$(git rev-parse --git-dir)"
for f in MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD REBASE_HEAD BISECT_LOG; do
  if test -e "$gitdir/$f"; then echo "state file present: $f"; fi
done
for d in rebase-merge rebase-apply sequencer; do
  if test -d "$gitdir/$d"; then echo "state dir present: $d/"; fi
done
git status --porcelain=v1 --branch
git rev-parse --abbrev-ref HEAD
```

**Critical caveat**: `git status`'s in-progress banners ("You are currently
rebasing…") are human-facing text that upstream does not document as a format,
so they are read as a hint and never as the detection mechanism. The state
files above and `--porcelain=v1` are what a repair decides on.

## Resolving each operation

| Operation | `--continue` | `--skip` | `--abort` / equivalent | Source |
|---|---|---|---|---|
| `rebase` | "Restart the rebasing process after having resolved a merge conflict" | "Restart the rebasing process by skipping the current patch" — the current commit is dropped from the result | "Abort the rebase operation and reset `HEAD` to the original branch" | [git-rebase](https://git-scm.com/docs/git-rebase) |
| `merge` | Commits the resolved merge (`git merge --continue`, or a plain `git commit` while `MERGE_HEAD` exists) | Not offered — a merge has one step, so there is nothing to skip | "Abort the current conflict resolution process, and try to reconstruct the pre-merge state. If an autostash entry is present, apply it to the worktree" | [git-merge](https://git-scm.com/docs/git-merge) |
| `cherry-pick` | "Continue the operation in progress using the information in `.git/sequencer`" | "Skip the current commit and continue with the rest of the sequence" | "Cancel the operation and return to the pre-sequence state" | [git-cherry-pick](https://git-scm.com/docs/git-cherry-pick) |
| `revert` | Same sequencer semantics as cherry-pick | Same | Same | [git-revert](https://git-scm.com/docs/git-revert) |
| `bisect` | Not applicable — progress is `git bisect good`/`bad` | Use `git bisect skip` for an untestable commit | `git bisect reset` returns to the pre-`bisect start` commit | [git-bisect](https://git-scm.com/docs/git-bisect) |
| `cherry-pick` / `revert`, state only | — | — | `--quit`: "Forget about the current operation in progress" — clears sequencer state **without** returning to the pre-sequence tree, so it keeps partial results that `--abort` would discard | [git-cherry-pick](https://git-scm.com/docs/git-cherry-pick) |

## What `--abort` restores and what it cannot

| Situation | Restored | Not restored | Source |
|---|---|---|---|
| `merge --abort` with a clean tree at merge start | The pre-merge `HEAD`, index and working tree | — | [git-merge](https://git-scm.com/docs/git-merge) |
| `merge --abort` with uncommitted changes at merge start | Best effort only — upstream: "if there were uncommitted worktree changes present when the merge started, `git merge --abort` will in some cases be unable to reconstruct these changes" | Those uncommitted changes, especially if further modified after the merge began. This is the case where an abort is itself lossy | [git-merge `--abort`](https://git-scm.com/docs/git-merge) |
| `merge --abort` with an autostash entry | The autostash is applied back to the worktree | — | [git-merge `--abort`](https://git-scm.com/docs/git-merge) |
| `rebase --abort` | `HEAD` and the original branch position | Any commit created *during* the rebase by an `edit` or `exec` step that the abort discards — those become unreachable objects, findable per [reflog-and-unreachable-objects.md](reflog-and-unreachable-objects.md) | [git-rebase `--abort`](https://git-scm.com/docs/git-rebase) |
| `cherry-pick --abort` | The pre-sequence state — every already-applied commit in the sequence is undone | — | [git-cherry-pick](https://git-scm.com/docs/git-cherry-pick) |
| `cherry-pick --quit` | Nothing is undone; only the sequencer state is cleared | The remaining unapplied commits are simply abandoned, with no record that the sequence was incomplete | [git-cherry-pick](https://git-scm.com/docs/git-cherry-pick) |

## Detached `HEAD`

Upstream defines the state precisely, and the consequence follows from the
definition: "commands that operate on the history of the current branch (e.g.
`git commit`…) still work while the `HEAD` is detached. They update the `HEAD`
to point at the tip of the updated history **without affecting any branch**."

| Question | Answer | Source |
|---|---|---|
| How is it detected | `git rev-parse --abbrev-ref HEAD` prints the literal `HEAD`; `git status` reports no branch | [git-rev-parse](https://git-scm.com/docs/git-rev-parse) |
| What happens to commits made there | They exist as real objects, reachable only through `HEAD` itself | [gitglossary — detached HEAD](https://git-scm.com/docs/gitglossary) |
| Why leaving loses them | Moving `HEAD` elsewhere removes the only reference, making those commits unreachable — nothing warns loudly and nothing else pointed at them | [gitglossary — unreachable object](https://git-scm.com/docs/gitglossary) |
| How they are kept before leaving | `git switch -c <name>` (or `git branch <name>`) creates a real ref at the current position | [git-switch](https://git-scm.com/docs/git-switch) |
| How they are recovered after leaving | `HEAD`'s own reflog still holds the detached position, or `git fsck` finds the commit if the entry expired — see [reflog-and-unreachable-objects.md](reflog-and-unreachable-objects.md) | [git-reflog](https://git-scm.com/docs/git-reflog) |

## Force-push overwrite — where the old objects still live

`--force` "can cause the remote repository to lose commits; use it with care",
and `--force-with-lease` is the guard: it "overrides this restriction if the
current value of the remote ref is the expected value", failing instead of
overwriting when someone else advanced the branch.

| Location | Still holds the pre-push commits when | Source |
|---|---|---|
| This clone's `refs/remotes/<remote>/<branch>` reflog | The clone had fetched the old history, and the entry is still inside `gc.reflogExpireUnreachable` — this is the only in-clone source, and `<ref>@{1}` addresses it | [git-reflog](https://git-scm.com/docs/git-reflog), [gitrevisions](https://git-scm.com/docs/gitrevisions) |
| A local branch or tag in this clone | Something local still points at the old tip — check before assuming the remote-tracking reflog is the only candidate | [git-for-each-ref](https://git-scm.com/docs/git-for-each-ref) |
| Another clone | That clone fetched the old history and has not yet fetched or pruned. Its reflog is a separate artifact and must be read there — this clone cannot see it | [git-reflog](https://git-scm.com/docs/git-reflog) |
| The hosting provider | Provider-specific retention, not git behaviour; nothing under the roots in [root-links.md](root-links.md) documents it, so it is a question to the provider, never an assumption | [root-links.md](root-links.md) |
| Genuinely nowhere | This clone was created or first fetched **after** the force-push, so it never held the old objects and has no reflog entry for them. No command run here can produce them | [gitglossary — unreachable object](https://git-scm.com/docs/gitglossary) |

```sh
remote_ref="$(git rev-parse --symbolic-full-name '@{upstream}')"
git reflog show "$remote_ref" --date=iso
git log --oneline "$remote_ref@{1}" "^$remote_ref"
git branch "recovered-${remote_ref##*/}" "$remote_ref@{1}"
```

## Evil merges — a merge whose content matches neither parent

Upstream's definition: "An evil merge is a merge that introduces changes that do
not appear in any parent." That is why a change silently dropped during conflict
resolution produces **no conflict marker and no error later** — the merge commit
records a tree that is simply missing it, and the merge is a valid commit.

| Instrument | What it exposes | Source |
|---|---|---|
| `git log --merges` | Which commits are merges at all, the candidate set for the checks below | [git-log](https://git-scm.com/docs/git-log) |
| `git diff <merge>^1 <merge>` | What the merge changed relative to its **first** parent — the mainline side. Content here that neither side introduced is the evil part | [gitrevisions `^<n>`](https://git-scm.com/docs/gitrevisions), [git-diff](https://git-scm.com/docs/git-diff) |
| `git diff <merge>^2 <merge>` | The same against the **second** parent — the merged-in side. A change present in `^2` but absent from the merge is a dropped change | [gitrevisions `^<n>`](https://git-scm.com/docs/gitrevisions), [git-diff](https://git-scm.com/docs/git-diff) |
| `git show --cc <merge>` | The combined diff, which by design shows only hunks differing from **every** parent — that is, exactly the resolution the merger typed by hand | [git-diff combined diff format](https://git-scm.com/docs/git-diff) |
| `git diff <merge> <parent1>...<parent2>` | Upstream's dedicated form: "This form is to view the results of a merge commit. The first listed *<commit>* must be the merge itself; the remaining two or more commits should be its parents" | [git-diff](https://git-scm.com/docs/git-diff) |

```sh
merge="$(git rev-list --merges -n 1 HEAD)"
git show --cc --stat "$merge"
git diff --stat "$merge^1" "$merge"
git diff --stat "$merge^2" "$merge"
```

**Critical caveat**: `git show <merge>` without `-c`/`--cc` shows a diff against
the first parent only, so a change dropped from the second parent's side does not
appear at all. Both parent diffs are needed before a merge can be called clean —
one of them being empty is the normal case, not evidence.
