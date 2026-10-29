# Secret History Archaeology

Two questions, kept apart: did the pattern ever enter history, and is it still reachable. Output is located objects plus the command that found them. Whether a match is a real secret is `security-reviewer`'s verdict; rotation or purge is `cto`'s. Never print or copy a matched secret into the report: cite sha, path and line only.

## Instruments
| Instrument | Searches | Misses |
|---|---|---|
| `git log -p --all -S/-G` | Diff text of every commit reachable from any ref | A value in a tree never introduced by a diff the walk visited (pruned merge side) unless `--full-history` |
| `git rev-list --all` piped to `git grep` | Full tree content of every listed commit; reports every commit still containing the value, not just the introducer; far costlier | Nothing within the listed revisions |

Together: introduction point (pickaxe) plus current extent (grep); both miss objects outside the ref set (reflog-only, stash-only, other clones).

## Pickaxe sweep
```sh
git log -p --all --full-history -S'AKIA[0-9A-Z]{16}' --pickaxe-regex
git log -p --all --full-history -G'AKIA[0-9A-Z]{16}'
```
A key swapped for another leaves the occurrence count unchanged: invisible to `-S`, so the `-G` pass is required. `-i` for case-insensitive config key names.

## Grep sweep
```sh
git rev-list --all | xargs git grep -n -e 'AKIA[0-9A-Z]\{16\}'
```
- Several tree-ish arguments are searched at once. `-e` is required when the pattern starts with `-` and is safe for assembled patterns.
- `--all-match` with `--or` patterns: files with both a key name and a key-shaped value.
- `--cached` finds staged secrets; `--untracked` finds an ignored `.env` on disk (not in history); `-I` skips binaries; `--no-index` ignores git entirely and cannot combine with `--cached`/`--untracked`.

## Ref scope
| Scope | Covers |
|---|---|
| none | current `HEAD` only |
| `--all` | every ref under `refs/` + `HEAD`: branches, tags, remote-tracking, stash ref; not reflogs |
| `--reflog` | objects any reflog mentions: the only scope for rebased-away or force-pushed commits |
| `--remotes` | `refs/remotes` only |
| `--single-worktree` | REMOVES coverage: limits `--all`/`--reflog` to the current worktree |
| `git fsck --unreachable` | objects reachable from nothing, which no revision walk lists |

A live stash is reached by `--all` via the stash ref; a dropped one is not (see [finding-lost-and-deleted-work.md](finding-lost-and-deleted-work.md)).

## What reachability proves
| Claim | Reality |
|---|---|
| "Sweep found nothing, never committed" | Only the given refs were covered; reflog-only, dropped-stash or unreachable objects are outside `--all`, and `gc` may have pruned the proof |
| "Commit unreachable, key gone" | Still in this clone's database until `gc`; `fsck --unreachable` lists it |
| "`gc` will prune it" | Governed by expiry windows (30 days unreachable reflog, 90 reachable); nothing forces it to run |
| "Local repo clean, contained" | Reachability is per clone: remote, other clones, CI caches or forks may still hold it |
| "A later commit removed the file" | The earlier blob stays reachable from the earlier commit |
| "Remote no longer shows the branch" | Deleting a ref does not delete objects; the server may keep them via a pull-request ref or its own reflog |
| "Only ever in a stash" | `--all` reaches a live stash, so it is in history |

A value that was ever pushed is disclosed regardless of what this clone holds; no local sweep proves nobody fetched it. If a secret is in git history, stop and route to `cto` (project rule).

Every finding states the pattern, the exact command, the ref scopes covered and the scopes not covered; a sweep reported without scope reads as exhaustive. "Who committed it": [attribution-honesty.md](attribution-honesty.md). Restoring, rewriting or force-pushing: `git-recovery`.
