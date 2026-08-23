# Reflog and Unreachable Objects — What Still Points at Lost Work

Sources: [git-reflog](https://git-scm.com/docs/git-reflog), [gitrevisions](https://git-scm.com/docs/gitrevisions), [git-fsck](https://git-scm.com/docs/git-fsck), [git-gc](https://git-scm.com/docs/git-gc), [git-cat-file](https://git-scm.com/docs/git-cat-file), [Pro Git — Maintenance and Data Recovery](https://git-scm.com/book/en/v2/Git-Internals-Maintenance-and-Data-Recovery).

Covers: SKILL.md §4 — "Say plainly when uncommitted work is unrecoverable", "Search every reflog before concluding a commit is gone", "Fall back to `git fsck --lost-found` only for objects that were once written".

Two independent instruments can find a commit nothing currently references: the
reflog, which records where a ref used to point, and `git fsck`, which walks the
object store for objects no ref reaches. They cover overlapping but different
sets, and neither covers content that never became an object at all — the
[coverage table](#coverage--what-each-instrument-can-and-cannot-surface) below
is the load-bearing part of this file. Anchoring the broken state before any of
this runs belongs to `git-safety-anchor`.

## Contents

- [Reflog listing](#reflog-listing)
- [Revision syntax that reads a reflog](#revision-syntax-that-reads-a-reflog)
- [Expiry — the window in which a reflog entry still exists](#expiry--the-window-in-which-a-reflog-entry-still-exists)
- [`git fsck` — walking the object store instead of the reflogs](#git-fsck--walking-the-object-store-instead-of-the-reflogs)
- [Triaging a bare sha](#triaging-a-bare-sha)
- [Coverage — what each instrument can and cannot surface](#coverage--what-each-instrument-can-and-cannot-surface)

## Reflog listing

`git reflog` with no subcommand means `git reflog show`, and `show` accepts any
option `git log` accepts — which is why `--all` works on it at all, and why the
machine-readable form of a reflog is a `git log -g --format=` invocation rather
than the default rendering.

| Invocation | What it lists | Source |
|---|---|---|
| `git reflog` | The reflog of `HEAD` only — every `checkout`, `commit`, `reset`, `merge` and `rebase` that moved it | [git-reflog](https://git-scm.com/docs/git-reflog) |
| `git reflog show <ref>` | That one ref's reflog; a branch deleted after the fact leaves this ref with no log to read | [git-reflog](https://git-scm.com/docs/git-reflog) |
| `git reflog --all` | Every ref that has a reflog, not just `HEAD` — this is the listing that finds a commit left on a branch other than the current one | [git-reflog](https://git-scm.com/docs/git-reflog) |
| `git log -g --all` | The same set as above with full `git log` formatting, including `%gd` (the `ref@{n}` selector) and `%gs` (the reflog subject) | [git-reflog](https://git-scm.com/docs/git-reflog) |
| `git reflog list` | Which refs have a reflog at all — answers "was this branch ever here" before searching its entries | [git-reflog](https://git-scm.com/docs/git-reflog) |
| `git reflog exists <ref>` | Exit status only; the scriptable form of the previous row | [git-reflog](https://git-scm.com/docs/git-reflog) |
| `git reflog expire`, `git reflog delete`, `git reflog drop` | Destructive — they remove entries, single entries, and a whole reflog respectively. Nothing in a recovery runs these | [git-reflog](https://git-scm.com/docs/git-reflog) |

```sh
git reflog --all --date=iso
git log -g --all --format='%gd %h %ad %gs'
git update-ref refs/heads/recovered "$(git rev-parse 'HEAD@{1}')"
```

## Revision syntax that reads a reflog

| Syntax | Resolves to | Source |
|---|---|---|
| `<refname>@{<n>}` | "the n-th prior value of that ref" — `master@{1}` is the immediate prior value, `master@{5}` the fifth. Requires that the ref have an existing log under the git directory's `logs/` | [gitrevisions](https://git-scm.com/docs/gitrevisions) |
| `HEAD@{1}` | Where `HEAD` pointed one move ago — the shortest undo for a single `reset`, `checkout` or `commit --amend` | [gitrevisions](https://git-scm.com/docs/gitrevisions) |
| `<refname>@{<date>}` | The ref's value at a past time (`master@{yesterday}`, `HEAD@{2 hours ago}`). Upstream is explicit that this "looks up the state of your **local** ref at a given time" — it is not the remote's history | [gitrevisions](https://git-scm.com/docs/gitrevisions) |
| `@{-<n>}` | The n-th branch or commit checked out before the current one; `@{-1}` is what `git checkout -` means | [gitrevisions](https://git-scm.com/docs/gitrevisions) |
| `ORIG_HEAD` | Written by commands "that move your `HEAD` in a drastic way (`git am`, `git merge`, `git rebase`, `git reset`), to record the position of the `HEAD` before their operation". This is the first thing to read after a `reset --hard` | [gitrevisions](https://git-scm.com/docs/gitrevisions) |
| `<rev>^<n>` | The n-th parent — `HEAD^1` and `HEAD^2` are how a merge's two sides are addressed, used in [interrupted-and-overwritten-state.md](interrupted-and-overwritten-state.md) | [gitrevisions](https://git-scm.com/docs/gitrevisions) |

**Critical caveat**: `ORIG_HEAD` is a single slot, overwritten by the next
drastic move. A second `reset` after the first destroys the pointer to the
pre-first-reset position, and only the reflog still holds it — which is the
whole reason a repair is anchored before it runs rather than after.

## Expiry — the window in which a reflog entry still exists

| Setting | Default | What it governs | Source |
|---|---|---|---|
| `gc.reflogExpire` | 90 days — "`git reflog expire` removes reflog entries older than this time; defaults to 90 days" | Entries for commits still reachable from the ref's current tip | [git-gc](https://git-scm.com/docs/git-gc) |
| `gc.reflogExpireUnreachable` | 30 days — entries "older than this time and are not reachable from the current tip; defaults to 30 days" | The entries a recovery actually depends on: a reset-away commit is unreachable, so it is the 30-day clock that applies, not the 90-day one | [git-gc](https://git-scm.com/docs/git-gc) |
| `gc.pruneExpire` | 2 weeks ago — `git gc` "will call `prune --expire 2.weeks.ago`" | How long a loose object that nothing references survives in the object store | [git-gc](https://git-scm.com/docs/git-gc) |
| `git gc --prune=now` | Immediate | Prunes loose objects regardless of age; upstream warns it "increases the risk of corruption if another process is writing to the repository concurrently". A recovery never runs this, and if the requester already did, assume the objects are gone | [git-gc](https://git-scm.com/docs/git-gc) |

## `git fsck` — walking the object store instead of the reflogs

| Flag | Effect | Source |
|---|---|---|
| `--unreachable` | Prints objects that exist but "aren't reachable from any of the reference nodes" | [git-fsck](https://git-scm.com/docs/git-fsck) |
| `--dangling` | Prints objects "never *directly* used" — an unreachable object with nothing, not even another unreachable object, pointing at it. On by default | [git-fsck](https://git-scm.com/docs/git-fsck) |
| `--lost-found` | Writes dangling objects into the git directory's `lost-found/commit/` and `lost-found/other/`; for a blob it writes the **contents** into the file rather than the object name, which is what makes a recovered file directly readable | [git-fsck](https://git-scm.com/docs/git-fsck) |
| `--no-reflogs` | Stops treating a commit referenced only by a reflog entry as reachable. This is the flag that separates the two instruments: with it, `fsck` reports exactly what the reflog can no longer save | [git-fsck](https://git-scm.com/docs/git-fsck) |
| `--full` | Also checks alternate object pools and packfiles, not only loose objects in the git directory. Now the default; `--no-full` disables it | [git-fsck](https://git-scm.com/docs/git-fsck) |
| `--cache` | Treats any object recorded in the index as a reachability root — relevant when work was staged but never committed | [git-fsck](https://git-scm.com/docs/git-fsck) |

## Triaging a bare sha

`fsck` output is a type and a sha with no message, date or branch, so every
candidate has to be identified before it can be offered as a recovery.

| Command | Answers | Source |
|---|---|---|
| `git cat-file -t <sha>` | Which of `commit`, `tree`, `blob`, `tag` this is — a dangling blob is staged-but-uncommitted content, a dangling commit is a whole lost tip | [git-cat-file](https://git-scm.com/docs/git-cat-file) |
| `git cat-file -p <sha>` | The pretty-printed object: a blob's text, a commit's tree/parent/author/message | [git-cat-file](https://git-scm.com/docs/git-cat-file) |
| `git log -1 --format='%h %ad %an %s' <sha>` | The human identity of a dangling commit, so the requester can confirm it is the one they want | [git-log](https://git-scm.com/docs/git-log) |
| `git update-ref refs/heads/<name> <sha>` | Makes a confirmed sha reachable again without a checkout, which stops the next `gc` from pruning it | [git-update-ref](https://git-scm.com/docs/git-update-ref) |

```sh
git fsck --unreachable --no-reflogs --no-progress > /tmp/git-unreachable.txt
for sha in $(awk '$2 == "commit" { print $3 }' /tmp/git-unreachable.txt); do
  git log -1 --format='%h %ad %an %s' --date=short "$sha"
done
```

## Coverage — what each instrument can and cannot surface

| Instrument | Can surface | Cannot surface | Source |
|---|---|---|---|
| `git reflog` / `git log -g` | Every position a ref held while its reflog entry survives: pre-`reset` tips, pre-`rebase` tips, the tip of a branch deleted after its last commit, the commit left behind on a detached `HEAD` | Anything for a ref that never had a reflog in this clone; entries already past `gc.reflogExpireUnreachable`; the working-tree contents at any of those positions — a reflog records **ref positions**, never file content | [git-reflog](https://git-scm.com/docs/git-reflog), [gitrevisions](https://git-scm.com/docs/gitrevisions) |
| `ORIG_HEAD` | The single position `HEAD` held immediately before the last `am`, `merge`, `rebase` or `reset` | Any earlier position, once a second drastic command has overwritten the slot | [gitrevisions](https://git-scm.com/docs/gitrevisions) |
| `git fsck --unreachable` | Commits, trees, blobs and tags that exist in the object store with nothing reaching them — including objects whose reflog entry has already expired, since the object outlives the entry | Anything `gc --prune` has already removed; anything that was never written to the object store | [git-fsck](https://git-scm.com/docs/git-fsck) |
| `git fsck --lost-found` | The same set, materialised as files on disk — blob contents recoverable without knowing which commit they belonged to | Any grouping into a commit or a path: a recovered blob arrives with no filename and no ordering | [git-fsck](https://git-scm.com/docs/git-fsck) |
| `git fsck --cache` | Objects reachable from the index — staged work not yet committed | Unstaged working-tree modifications, which the index does not reference | [git-fsck](https://git-scm.com/docs/git-fsck) |
| Nothing in git | — | A file edited and never `git add`-ed, never stashed, and then destroyed by `reset --hard`, `checkout`, or `clean -xdf`. It was never hashed, so **no object exists**, and neither reflog nor `fsck` has anything to find | [Pro Git — Maintenance and Data Recovery](https://git-scm.com/book/en/v2/Git-Internals-Maintenance-and-Data-Recovery) |

**Critical caveat**: a fresh clone has **no local reflog for history it never
had**. Cloning creates reflog entries only from the moment of the clone forward,
so a clone taken after a destructive push holds no entry for the pre-push
position — the reflog of a different, older clone is a genuinely different
artifact and must be read there, not here.

The consequence for reporting: the honest answer to "can you get it back" has
three forms, and they are not interchangeable. A commit found in a reflog is
recoverable now. A dangling object found by `fsck` is recoverable now but on a
clock, so it is made reachable with `git update-ref` in the same session.
Content that was never staged is not recoverable at all, and saying so is the
result — never a search offered in its place.
