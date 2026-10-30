# Content Search and Bisect

Pickaxe searches history for a **string** with no build; `bisect` searches for a **behaviour** and needs a test that never lies. A string present but misused: pickaxe narrows the suspect surface, then `bisect run` confirms. No deterministic test: pickaxe only, limitation stated.

## Pickaxe
| Option | Matches |
|---|---|
| `-S<text>` | Filepairs whose pre/postimage contain a different **count** of the text; no in-file moves |
| `-G<regex>` | Filepairs whose diff has an added/deleted line matching; also in-file moves |
| `--pickaxe-regex` | Treats `-S` argument as an extended POSIX regex (count semantics kept) |
| `--pickaxe-all` | Keeps the whole changeset when any filepair matches |

```sh
git log --all -p --pickaxe-all -S'MaxHealth' -- .
git log --all -p -G'MaxHealth' -- .
```
`damage * 2` -> `damage * 3` leaves the count of `damage` unchanged: invisible to `-S'damage'`, found by `-G'damage'`.

Walk scope: `--all` (every ref + `HEAD`, no reflogs), `--reflog` (adds objects only a reflog mentions), `-p` (quotable evidence), `--follow` (renames of a single file, exactly one pathspec), `--full-history` (do not prune merged sides), `-i`.

## Bisect
| Command | Notes |
|---|---|
| `start [bad] [good] [-- paths]`, `bad`, `good` | Mark revisions |
| `new` / `old` | Neutral terms for a non-defect change (performance, added behaviour); `terms` prints the polarity in use |
| `skip [range]` | Untestable revision |
| `log` / `replay <logfile>` | Audit trail; reproduce or correct a mis-mark |
| `run <cmd>` | Automate from exit code |
| `visualize`/`view`, `next`, `reset` | Inspect, step, end (restores `HEAD`) |
| `--no-checkout` | Moves `BISECT_HEAD`, leaves the tree alone |
| `--first-parent` | Names the merge that brought it in, not the commit inside |

## `run` exit codes
| Code | Recorded as |
|---|---|
| `0` | good/old |
| `1`-`124`, `126`, `127` | bad/new |
| `125` | skip (cannot test) |
| `128`+ (incl. `exit(-1)` = 255) | aborts the session |

126/127 are the shell's "not executable"/"not found". git 2.56 aborts the run on them (`error: bogus exit code 127`, checked with a missing script), but a script that hits a missing tool and exits `1` is still recorded as bad at every revision, yielding the oldest tested revision as a confident answer. First confirm the script exits 0 on a known-good and non-zero on a known-bad revision.

## Test requirements
- Deterministic per revision; a flake compounds silently.
- Verdict via exit code, not output (prose plus exit 0 = good).
- Exit `125` for a revision that cannot build or run, else it counts as bad.
- No state left between revisions (caches, generated files, untracked build output persist across checkouts).
- A genuinely passing `good` revision recorded first.

`bisect` names the first failing revision, not necessarily the cause: [attribution-honesty.md](attribution-honesty.md). Confirm the range is intact first ([finding-lost-and-deleted-work.md](finding-lost-and-deleted-work.md)).
