# Root Links — Git Reference Manual and Pro Git

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Git publishes **no versioned documentation URLs** — `https://git-scm.com/docs`
always serves the manual for the current release, so there is no version
segment to pin and none is invented here. Every link in this folder resolves
under one of the two roots below; because the pin is the live site rather than
a release, a flag documented upstream may not exist in the git binary running
the trace, so confirm with `git <subcommand> --help` locally before depending
on one.

| Root | Holds | Source |
|---|---|---|
| Reference manual | The per-subcommand man pages every flag in this folder is taken from, grouped by category and linked as `/docs/git-<subcommand>` | [Git Reference](https://git-scm.com/docs) |
| Pro Git, 2nd edition | The conceptual chapters behind the instruments — bisection, history rewriting, and object-database recovery | [Pro Git](https://git-scm.com/book/en/v2) |

## History simplification — the mechanism every query here inherits

| Behaviour | What it does to a path-limited query | Source |
|---|---|---|
| Default (no flag) | Shows only commits that are not TREESAME to a parent, and for a merge TREESAME to one parent follows **only that parent** — every commit on the other side is dropped from the walk | [History Simplification](https://git-scm.com/docs/git-log#_history_simplification) |
| `--full-history` | Follows all parents of every merge regardless of TREESAME, so the merge that dropped a path is no longer skipped; the mandatory flag for a deletion hunt | [History Simplification](https://git-scm.com/docs/git-log#_history_simplification) |
| `--simplify-merges` | Applies `--full-history` then removes merges to which no selected commit contributed, and rewrites parent lists; more accurate, but walks the whole commit graph | [History Simplification](https://git-scm.com/docs/git-log#_history_simplification) |
| `--sparse` | Shows every commit walked in the simplified history, including TREESAME ones | [History Simplification](https://git-scm.com/docs/git-log#_history_simplification) |
| `--dense` | Shows only selected commits, excluding TREESAME ones — the default | [History Simplification](https://git-scm.com/docs/git-log#_history_simplification) |
| `--ancestry-path[=<commit>]` | Restricts output to commits that are ancestors of, descendants of, or equal to `<commit>` — answers "which of these commits actually descend from that one" | [History Simplification](https://git-scm.com/docs/git-log#_history_simplification) |
| `--all` | Substitutes every ref under `refs/` plus `HEAD` for the commit arguments, so the walk is not confined to the current branch. Does **not** include reflogs | [git rev-list](https://git-scm.com/docs/git-rev-list) |
| `--reflog` | Substitutes every object mentioned by a reflog — separate from `--all`, and the only way an unreachable-but-logged commit enters the walk | [git rev-list](https://git-scm.com/docs/git-rev-list) |

**Critical caveat**: a path-limited history query is not a complete list of the
commits that touched that path, and simplification is silent — a query that
returns nothing and a query whose answer was pruned are indistinguishable from
the output alone. This is why a deletion hunt, an ownership count, and a
pickaxe sweep can each miss the commit that matters, and why `--full-history`
recurs throughout the sibling files. A negative result on a path-limited log is
never evidence of absence until it has been re-run with `--full-history --all`.

## Topic → file map

| Topic | File | Source |
|---|---|---|
| `blame` whitespace/copy/move neutralisation, `--ignore-rev`, `.git-blame-ignore-revs`, `git log -L` line evolution | [blame-and-line-history.md](blame-and-line-history.md) | [git blame](https://git-scm.com/docs/git-blame), [git log](https://git-scm.com/docs/git-log) |
| Pickaxe `-S` vs `-G`, `--pickaxe-regex`, `--pickaxe-all`, and the full `git bisect` surface including the `run` exit-code contract | [content-search-and-bisect.md](content-search-and-bisect.md) | [diffcore-pickaxe](https://git-scm.com/docs/gitdiffcore#_diffcore_pickaxe_for_detecting_additiondeletion_of_specified_string), [git bisect](https://git-scm.com/docs/git-bisect) |
| Deletion hunting with `--diff-filter=D --full-history`, pre-deletion content retrieval, `reflog`, `fsck --lost-found`, dropped stashes | [finding-lost-and-deleted-work.md](finding-lost-and-deleted-work.md) | [git fsck](https://git-scm.com/docs/git-fsck), [git reflog](https://git-scm.com/docs/git-reflog), [gitrevisions](https://git-scm.com/docs/gitrevisions) |
| Sweeping every reachable object for a credential pattern, `git rev-list --all` with `git grep`, and what reachability does not prove | [secret-history-archaeology.md](secret-history-archaeology.md) | [git grep](https://git-scm.com/docs/git-grep), [git rev-list](https://git-scm.com/docs/git-rev-list) |
| What each instrument actually reports versus what a reader assumes it reports — author vs committer, squash collapse, exposing vs causing commit, `shortlog` counts | [attribution-honesty.md](attribution-honesty.md) | [git blame](https://git-scm.com/docs/git-blame), [git shortlog](https://git-scm.com/docs/git-shortlog) |
| Bisection as a concept, and the object-database recovery model behind `fsck` | this file's roots | [Debugging with Git](https://git-scm.com/book/en/v2/Git-Tools-Debugging-with-Git), [Maintenance and Data Recovery](https://git-scm.com/book/en/v2/Git-Internals-Maintenance-and-Data-Recovery) |
| Why the commit a trace lands on may not be the commit that was written | this file's roots | [Rewriting History](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History) |

## Disclosed gaps

| Area | Issue | Source |
|---|---|---|
| `--ignore-rev` with an abbreviated sha | The man page specifies "unabbreviated object name" for the revs **file** but states no behaviour for a short sha passed to `--ignore-rev` itself, and names no error. Treat the full 40-character form as the only supported input and verify the rev was actually ignored rather than assuming it was | [git blame](https://git-scm.com/docs/git-blame) |
| Reflogs are local-only | The `git reflog` page documents expiry defaults (`gc.reflogExpire` 90 days, `gc.reflogExpireUnreachable` 30 days) but does not state that reflogs are per-clone and never transferred. Every reachability conclusion in [finding-lost-and-deleted-work.md](finding-lost-and-deleted-work.md) that rests on that property is marked `synthesized` there | [git reflog](https://git-scm.com/docs/git-reflog) |
| `git cat-file -p <rev>:<path>` | The page frames `<tree-ish>:<path>` addressing under `--textconv`/`--filters` rather than under `-p`, yet `-p` accepts the extended syntax in practice (verified against git 2.55). Stated as verified behaviour, not as documented behaviour | [git cat-file](https://git-scm.com/docs/git-cat-file) |
| Version skew | No upstream page states which git release introduced a given flag, so nothing in this folder can promise a flag exists locally | [Git Reference](https://git-scm.com/docs) |

Each row above is something the sibling files depend on that upstream does not
state, marked here rather than presented as documented. Because the roots are
unversioned, a link that resolved when this folder was
written can change content without changing URL. Re-read the upstream page
before citing a default value or an exit code in a finding, and treat anything
not reachable under these two roots as out of scope for this skill rather than
merely undocumented here.
