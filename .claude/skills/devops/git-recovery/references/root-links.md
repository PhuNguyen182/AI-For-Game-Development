# Root Links — Git Documentation and the Porcelain/Plumbing Boundary

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Git publishes **no versioned documentation URLs**: every page under
`git-scm.com/docs` serves the reference manual for the release the site
currently tracks, with older releases reachable only through an on-page
selector, so there is no `@version` pin to carry across sibling files. Confirm
any flag against the installed `git --version` rather than against a pinned
page. This file also fixes the porcelain/plumbing boundary, because that is
what decides which of this skill's commands a recovery script may parse.

## Contents

- [Documentation roots](#documentation-roots)
- [Topic → file map](#topic--file-map)
- [Porcelain versus plumbing — what a script may parse](#porcelain-versus-plumbing--what-a-script-may-parse)
- [Disclosed gaps](#disclosed-gaps)

## Documentation roots

| Root | Holds | Source |
|---|---|---|
| Reference manual | One page per subcommand (`git-<name>`) plus the `git*` concept pages — `gitrevisions`, `gitglossary`, `gitrepository-layout`, `gitmodules` — and the `git(1)` command classification this skill's plumbing table is built on | [Git reference manual](https://git-scm.com/docs) |
| Pro Git, 2nd edition | The conceptual chapters: object model, data recovery, history rewriting, submodules, reset semantics | [Pro Git book](https://git-scm.com/book/en/v2) |
| Git LFS | LFS is a separate project with its own docs tree; nothing about it is documented under `git-scm.com` | [Git LFS](https://git-lfs.com), [git-lfs docs tree](https://github.com/git-lfs/git-lfs/tree/main/docs) |

## Topic → file map

| Topic | File | Source |
|---|---|---|
| Reflog listing and expiry, `ORIG_HEAD`, `@{n}`/`@{date}`, `fsck --lost-found`, `cat-file` triage, `gc --prune` | [reflog-and-unreachable-objects.md](reflog-and-unreachable-objects.md) | [git-reflog](https://git-scm.com/docs/git-reflog), [gitrevisions](https://git-scm.com/docs/gitrevisions), [git-fsck](https://git-scm.com/docs/git-fsck), [git-gc](https://git-scm.com/docs/git-gc) |
| Interrupted `rebase`/`merge`/`cherry-pick`/`revert`/`bisect` state, `--continue`/`--abort`/`--skip`, detached `HEAD`, force-push overwrite, evil merges | [interrupted-and-overwritten-state.md](interrupted-and-overwritten-state.md) | [gitrepository-layout](https://git-scm.com/docs/gitrepository-layout), [git-rebase](https://git-scm.com/docs/git-rebase), [git-merge](https://git-scm.com/docs/git-merge), [gitglossary](https://git-scm.com/docs/gitglossary) |
| Index corruption, object-store damage, submodule states, LFS pointer failures | [index-object-and-submodule-repair.md](index-object-and-submodule-repair.md) | [git-read-tree](https://git-scm.com/docs/git-read-tree), [git-fsck](https://git-scm.com/docs/git-fsck), [git-submodule](https://git-scm.com/docs/git-submodule), [git-lfs docs tree](https://github.com/git-lfs/git-lfs/tree/main/docs) |
| `rebase -i` todo verbs, `rebase --onto`, commit splitting, `merge --squash`, autosquash, `worktree`, `subtree`, `filter-repo` vs `filter-branch` | [history-surgery.md](history-surgery.md) | [git-rebase](https://git-scm.com/docs/git-rebase), [git-worktree](https://git-scm.com/docs/git-worktree), [git-filter-branch](https://git-scm.com/docs/git-filter-branch) |

## Porcelain versus plumbing — what a script may parse

`git(1)` states the guarantee directly: "The interface (input, output, set of
options and the semantics) to these low-level commands are meant to be a lot
more stable than Porcelain level commands, because these commands are
primarily for scripted use. The interface to Porcelain commands on the other
hand are subject to change in order to improve the end user experience."
A recovery script may therefore act on plumbing output, but must treat
porcelain output as advisory unless that command documents an explicit
machine format.

| Command | Class | What that means for parsing | Source |
|---|---|---|---|
| `git status` | Porcelain | Default and `--short` output vary by version and by user config; only `--porcelain=v1` is "guaranteed not to change in a backwards-incompatible way between Git versions or based on user configuration" | [git-status `--porcelain`](https://git-scm.com/docs/git-status) |
| `git reflog show` | Porcelain | It accepts `git log` options, so take the machine form from `git log -g --format=<fmt>` rather than from the default reflog rendering | [git-reflog](https://git-scm.com/docs/git-reflog) |
| `git reset` | Porcelain (manipulator) | Acts, does not report; read the result back with `git rev-parse`, never from its stdout | [git-reset](https://git-scm.com/docs/git-reset) |
| `git rebase`, `git merge`, `git cherry-pick`, `git revert` | Porcelain | Progress and conflict messages are user-facing text; detect their state from the git-directory files instead, per [interrupted-and-overwritten-state.md](interrupted-and-overwritten-state.md) | [git(1) porcelain list](https://git-scm.com/docs/git#_high_level_commands_porcelain) |
| `git fsck` | Porcelain (ancillary interrogator) | `dangling <type> <sha>` / `unreachable <type> <sha>` lines are stable enough to grep in practice but carry no interface guarantee — re-confirm every sha with `git cat-file` before acting | [git-fsck](https://git-scm.com/docs/git-fsck) |
| `git gc`, `git prune` | Porcelain (ancillary manipulator) | Destructive, and not a reporting surface; check what they would remove with `git fsck` first | [git-gc](https://git-scm.com/docs/git-gc), [git-prune](https://git-scm.com/docs/git-prune) |
| `git submodule`, `git worktree`, `git stash` | Porcelain | `git worktree list --porcelain` is the documented machine form; `git submodule status`'s prefix characters are documented but the surrounding text is not a fixed format | [git-worktree](https://git-scm.com/docs/git-worktree), [git-submodule](https://git-scm.com/docs/git-submodule) |
| `git rev-parse` | Plumbing (interrogator) | Stable single-value output — the correct way to resolve a ref, a sha, or `--git-dir` in a script | [git-rev-parse](https://git-scm.com/docs/git-rev-parse) |
| `git cat-file` | Plumbing (interrogator) | Stable; `-t` yields the object type and `-p` the pretty-printed content, which is what makes a bare sha from `fsck` identifiable | [git-cat-file](https://git-scm.com/docs/git-cat-file) |
| `git rev-list` | Plumbing (interrogator) | Stable sha-per-line output — use it, not `git log`, when a script needs a commit set | [git-rev-list](https://git-scm.com/docs/git-rev-list) |
| `git for-each-ref` | Plumbing (interrogator) | Stable, with an explicit `--format`; the scriptable alternative to parsing `git branch` | [git-for-each-ref](https://git-scm.com/docs/git-for-each-ref) |
| `git update-ref` | Plumbing (manipulator) | Stable; the safe way to recreate a deleted branch at a recovered sha without a checkout | [git-update-ref](https://git-scm.com/docs/git-update-ref) |
| `git read-tree` | Plumbing (manipulator) | Stable; writes the index from a tree and does not touch the working tree unless `-u` is given | [git-read-tree](https://git-scm.com/docs/git-read-tree) |
| `git hash-object` | Plumbing (manipulator) | Stable; `-w` writes a blob into the object store and prints its sha, which is how a file recovered from elsewhere re-enters this repository | [git-hash-object](https://git-scm.com/docs/git-hash-object) |
| `git update-index` | Plumbing (manipulator) | Stable; the low-level index writer behind `git add`, needed when the index must be rebuilt entry by entry | [git-update-index](https://git-scm.com/docs/git-update-index) |

## Disclosed gaps

| Page / area | Issue | Source |
|---|---|---|
| `git subtree` | It ships in the git source tree's `contrib/` directory and has **no page under `git-scm.com/docs`** — that URL returns 404, checked during authoring. [history-surgery.md](history-surgery.md) therefore sources subtree behaviour to the Pro Git book's [Subtree Merging](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging#_subtree_merging) section, and its availability must be confirmed against the installed git before use. | synthesized |
| `gc.reflogExpire` / `gc.reflogExpireUnreachable` | The 90-day and 30-day defaults are quoted from the two pages linked here, whose text agrees. The `git-config` page also lists them but is large enough that a fetch of it truncated before reaching the `gc.*` block, so no anchor into `git-config` is cited for them. | [git-gc](https://git-scm.com/docs/git-gc), [git-reflog](https://git-scm.com/docs/git-reflog) |
| Porcelain output stability | `git(1)`'s statement above is the only upstream text found that states the guarantee generally. The Pro Git [Plumbing and Porcelain](https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain) chapter draws the same distinction by design intent but does **not** claim output instability, and `gitcli` does not address it at all — so cite `git(1)`, not either of those, for the parsing rule. | [git(1) plumbing list](https://git-scm.com/docs/git#_low_level_commands_plumbing) |
| Hosting-provider retention | Whether a force-pushed sha survives on the server, and for how long, is provider policy (GitHub, GitLab, Azure DevOps), not git behaviour. No page under these roots documents it; treat any such claim as needing the provider's own documentation. | synthesized |
| Git LFS versioning | `git-lfs.com` tracks the current release (v3.7.1 at the time of writing) and the man pages cited in this folder are the `main`-branch `.adoc` sources, not a tagged release — a flag present there may not exist in an older installed `git-lfs`. | [Git LFS](https://git-lfs.com) |

Every other link in this `references/` folder is a specific page under these
roots, each verified to resolve before inclusion. Because none of them carries
a version segment, a page may describe a flag the installed git does not have:
when a command in this folder is rejected as unknown, check `git --version`
before concluding the documentation is wrong.
