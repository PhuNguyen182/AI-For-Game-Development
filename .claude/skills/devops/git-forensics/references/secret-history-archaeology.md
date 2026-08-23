# Secret History Archaeology — Sweeping Every Object for a Credential Pattern

Sources: [git log](https://git-scm.com/docs/git-log), [diffcore-pickaxe](https://git-scm.com/docs/gitdiffcore#_diffcore_pickaxe_for_detecting_additiondeletion_of_specified_string), [git rev-list](https://git-scm.com/docs/git-rev-list), [git grep](https://git-scm.com/docs/git-grep), [git stash](https://git-scm.com/docs/git-stash), [git fsck](https://git-scm.com/docs/git-fsck).
Covers: SKILL.md §4 — "Pick the instrument from the question rather than from habit", "Give every finding a location, an expected, an actual, evidence, and an owning agent-id".

A credential question has two halves that must not be collapsed: did this
pattern ever enter history, and is it still reachable today. The sweep below
answers both and stops there — whether a match is a real secret is
`security-reviewer`'s verdict, and whether to rotate the key or purge history is
`cto`'s decision. This file's only output is located objects with the command
that found them.

- [Two instruments, two coverage shapes](#two-instruments-two-coverage-shapes)
- [Pickaxe sweep over diffs](#pickaxe-sweep-over-diffs)
- [Grep sweep over trees](#grep-sweep-over-trees)
- [Ref scope](#ref-scope)
- [What reachability does and does not prove](#what-reachability-does-and-does-not-prove)
- [Ownership of the verdict](#ownership-of-the-verdict)

## Two instruments, two coverage shapes

| Instrument | Searches | Misses | Source |
|---|---|---|---|
| `git log -S` / `-G` over `--all` | The **diff text** of every commit reachable from any ref | A value present in a tree but never introduced by a diff the walk visited — a file added on a pruned side of a merge, unless `--full-history` is given | [diffcore-pickaxe](https://git-scm.com/docs/gitdiffcore#_diffcore_pickaxe_for_detecting_additiondeletion_of_specified_string) |
| `git rev-list --all` piped to `git grep` | The **full tree content** of every listed commit, not just what changed | Nothing within the listed revisions, but it is proportionally far more expensive and reports every commit whose tree still contains the value rather than the one that introduced it | [git grep](https://git-scm.com/docs/git-grep) |
| Both together | Introduction point (pickaxe) plus current extent (grep) | Objects outside the ref set given — reflog-only, stash-only, and other clones | synthesized |

## Pickaxe sweep over diffs

```sh
git log -p --all -S'AKIA[0-9A-Z]{16}' --pickaxe-regex
```

| Element | Why it is there | Source |
|---|---|---|
| `--all` | Confines nothing to the current branch; substitutes every ref under `refs/` plus `HEAD` | [git rev-list](https://git-scm.com/docs/git-rev-list) |
| `-S` with `--pickaxe-regex` | Treats the argument as an extended POSIX regex while keeping `-S`'s occurrence-count semantics, which is what matches a key **shape** rather than one known literal | [diffcore-pickaxe](https://git-scm.com/docs/gitdiffcore#_diffcore_pickaxe_for_detecting_additiondeletion_of_specified_string) |
| `-G` as the second pass | Matches added or deleted diff lines directly, catching a rotation that replaced one key with another without changing the occurrence count | [diffcore-pickaxe](https://git-scm.com/docs/gitdiffcore#_diffcore_pickaxe_for_detecting_additiondeletion_of_specified_string) |
| `-p` | Prints the diff, so the finding can quote the matched line as evidence instead of a bare sha | [git log](https://git-scm.com/docs/git-log) |
| `--full-history` | Stops a merge TREESAME to one parent from pruning the side the secret arrived on | [History Simplification](https://git-scm.com/docs/git-log#_history_simplification) |
| `-i` | Case-insensitive, for a pattern like a config key name rather than a fixed-case token | [git log](https://git-scm.com/docs/git-log) |

**Critical caveat**: a single `-S` pass is never a clean sweep for a credential.
A commit that swapped one key for another leaves the occurrence count unchanged
and is invisible to `-S`; only `-G` reports it. A report claiming history is
clean on the strength of `-S` alone has not covered rotation.

## Grep sweep over trees

```sh
git rev-list --all | xargs git grep -n -e 'AKIA[0-9A-Z]\{16\}'
```

| Option | Effect | Source |
|---|---|---|
| tree-ish arguments | Searches blobs in the given trees instead of the working tree; several tree-ish arguments may be passed at once, which is what makes the piped form work | [git grep](https://git-scm.com/docs/git-grep) |
| `-e <pattern>` | Names the pattern explicitly — required when it starts with `-`, and the safe form for any pattern assembled from input | [git grep](https://git-scm.com/docs/git-grep) |
| `--all-match` | With several patterns combined by `--or`, restricts matches to files matching **all** of them — narrows a noisy sweep to files carrying both a key name and a key-shaped value | [git grep](https://git-scm.com/docs/git-grep) |
| `--untracked` | Adds untracked working-tree files to the search; a key sitting in an ignored `.env` is not in history but is still on disk | [git grep](https://git-scm.com/docs/git-grep) |
| `--cached` | Searches blobs registered in the index — catches a secret already staged but not yet committed | [git grep](https://git-scm.com/docs/git-grep) |
| `-n` | Prefixes line numbers, which is what turns a hit into the `path:line` a finding requires | [git grep](https://git-scm.com/docs/git-grep) |
| `-I` | Suppresses matches inside binary files, cutting the false positives a high-entropy pattern produces there | [git grep](https://git-scm.com/docs/git-grep) |
| `--no-index` | Searches the directory as plain `grep -r` would, ignoring git entirely; cannot combine with `--cached` or `--untracked` | [git grep](https://git-scm.com/docs/git-grep) |

## Ref scope

| Scope | Adds | Source |
|---|---|---|
| The scope itself | Coverage is decided entirely by which refs enter the walk; each row below adds a set the row above excludes | [git rev-list](https://git-scm.com/docs/git-rev-list) |
| No option | Only the current `HEAD` | [git rev-list](https://git-scm.com/docs/git-rev-list) |
| `--all` | Every ref under `refs/` plus `HEAD` — branches, tags, remote-tracking refs, and the stash ref. Does **not** add reflogs | [git rev-list](https://git-scm.com/docs/git-rev-list) |
| `--reflog` | Every object any reflog mentions, including commits no ref points at any more — the only scope that covers a rebased-away or force-pushed commit | [git rev-list](https://git-scm.com/docs/git-rev-list) |
| `--remotes` | Only refs under `refs/remotes`, for asking the narrower question of what a fetch has already brought in | [git rev-list](https://git-scm.com/docs/git-rev-list) |
| `--single-worktree` | **Removes** coverage: restricts `--all` and `--reflog` to the current working tree, where the default examines all of them | [git rev-list](https://git-scm.com/docs/git-rev-list) |
| `git stash list` | Names surviving stash entries; a stash's own commit is reached by `--all` through the stash ref, but a dropped entry is not | [git stash](https://git-scm.com/docs/git-stash) |
| `git fsck --unreachable` | Objects reachable from nothing at all, which no revision walk will list | [git fsck](https://git-scm.com/docs/git-fsck) |

## What reachability does and does not prove

| Claim | What actually holds | Source |
|---|---|---|
| "The sweep found nothing, so the key was never committed" | The sweep covered the refs it was given. A commit only in a reflog, a dropped stash, or an unreachable object is outside `--all`, and a `gc` may already have pruned the object that would have proved it | [git rev-list](https://git-scm.com/docs/git-rev-list) |
| "The commit is unreachable, so the key is gone" | Unreachable means no local ref names it. The object is still in this clone's database until `gc` prunes it, and `git fsck --unreachable` still lists it | [git fsck](https://git-scm.com/docs/git-fsck) |
| "`gc` will prune it, so exposure ends there" | `gc` timing is not a guarantee: pruning is governed by expiry windows, the reflog still holds unreachable entries for `gc.reflogExpireUnreachable` (30 days by default) and reachable ones for `gc.reflogExpire` (90 days), and nothing forces the run to happen on schedule | [git reflog](https://git-scm.com/docs/git-reflog) |
| "The local repository is clean, so the credential is contained" | Reachability is a per-clone property. A reflog is never transferred by clone or fetch, so a commit unreachable here may be reachable on the remote, in another developer's clone, in a CI cache, or in a fork | synthesized |
| "Removing the file in a later commit removed the secret" | The earlier blob remains in history and is reachable from the earlier commit; the pickaxe finds the deletion, and the tree sweep still finds the value in every commit before it | synthesized |
| "The remote no longer shows the branch, so the object is gone from it" | Deleting a ref does not delete objects; the server decides its own expiry and may keep the object reachable through a pull-request ref or its own reflog | synthesized |
| "It was only ever in a stash" | `--all` reaches a live stash through the stash ref, so a stash-only secret is in history for every purpose that matters | [git stash](https://git-scm.com/docs/git-stash) |

**Critical caveat**: exposure and reachability are different questions. A value
that was ever pushed must be treated as disclosed regardless of what the local
object database now holds — no sweep of this clone can establish that nobody
else fetched it.

## Ownership of the verdict

| Question | Owner | Why it is not answered here | Source |
|---|---|---|---|
| Is the matched string an actual credential, or a public SDK identifier or test fixture | `security-reviewer` | Distinguishing a live key from a documented public identifier is a security judgement, not a history query | synthesized |
| Should the key be rotated, and should history be purged or rewritten | `cto` | It is a strategic, hard-to-reverse decision with vendor and release consequences | synthesized |
| Which commit introduced it, and is it still reachable | this skill | Both are answerable from the object database with the commands above | synthesized |
| Who committed it | this skill, with the caveats in [attribution-honesty.md](attribution-honesty.md) | The recorded author may not be the person who wrote the line | [git blame](https://git-scm.com/docs/git-blame) |
| Restoring, rewriting, or force-pushing anything | `git-recovery` | This skill locates and attributes; it does not modify history | synthesized |

Every finding here carries the pattern searched, the exact command, the ref
scope it covered, and — explicitly — the scopes it did not, because a sweep
reported without its scope reads downstream as exhaustive when it was not.
