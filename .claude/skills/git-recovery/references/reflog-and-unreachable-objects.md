# Reflog and Unreachable Objects

Sources: `git-reflog`, `gitrevisions`, `git-fsck`, `git-gc`, `git-cat-file` under the `Docs:` base.

## What still points at a lost commit

| Instrument | Fact that decides |
|---|---|
| `git reflog` | `HEAD` only — misses a commit left on another branch |
| `git reflog --all`, `git log -g --all --format='%gd %h %ad %gs'` | Every ref with a reflog; the `log -g --format=` form is the parseable one |
| `git reflog show <ref>` | Deleting a branch deletes its reflog — find its last tip in `HEAD`'s reflog instead |
| `git reflog list`, `git reflog exists <ref>` | Whether a ref currently has a reflog in this clone |
| `<ref>@{<date>}` | The **local** ref's value at that time, never the remote's history |
| `ORIG_HEAD` | `HEAD` before the last `am`/`merge`/`rebase`/`reset`. A single slot: the next such command overwrites it, and only the reflog keeps the earlier position |

**Caveat:** a fresh clone has no reflog for anything before it was cloned. An older clone's reflog is a different artifact and must be read in that clone.

## Expiry — how long it stays findable

| Setting | Default | Governs |
|---|---|---|
| `gc.reflogExpireUnreachable` | 30 days | Entries unreachable from the ref's tip — a reset-away commit. **The operative window** |
| `gc.reflogExpire` | 90 days | Entries still reachable from the tip only |
| `gc.pruneExpire` | 2 weeks | Unreferenced loose objects. If the requester already ran `gc --prune=now`, assume they are gone |

## `fsck` — objects no ref reaches

| Flag / command | Fact that decides |
|---|---|
| `--unreachable` | Includes objects whose reflog entry already expired — the object outlives the entry |
| `--no-reflogs` | Counts reflog-only commits as unreachable: shows exactly what the reflog can no longer save |
| `--lost-found` | Writes dangling objects to `lost-found/commit/` and `lost-found/other/`; a blob arrives as contents with no filename or path |
| `--cache` | Index entries count as roots — finds staged-but-uncommitted work, never unstaged edits |
| `git cat-file -t` / `-p <sha>` | `fsck` lines carry no interface guarantee: identify every sha before offering it |
| `git update-ref refs/heads/<name> <sha>` | Makes a confirmed sha reachable without a checkout, so `gc` cannot prune it |

```sh
git fsck --unreachable --no-reflogs --no-progress | awk '$2 == "commit" { print $3 }' |
  while read -r sha; do git log -1 --format='%h %ad %an %s' --date=short "$sha"; done
```
