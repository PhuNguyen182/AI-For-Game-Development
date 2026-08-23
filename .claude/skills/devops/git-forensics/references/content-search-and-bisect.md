# Content Search and Bisect — Finding the Commit That Introduced Something

Sources: [diffcore-pickaxe](https://git-scm.com/docs/gitdiffcore#_diffcore_pickaxe_for_detecting_additiondeletion_of_specified_string), [git log](https://git-scm.com/docs/git-log), [git bisect](https://git-scm.com/docs/git-bisect), [Debugging with Git](https://git-scm.com/book/en/v2/Git-Tools-Debugging-with-Git).
Covers: SKILL.md §4 — "Pick the instrument from the question rather than from habit", "Give `bisect` a deterministic pass/fail test before starting it", "Distinguish `-S` from `-G` on a content search".

Two instruments answer the same question — which commit introduced this — from
opposite directions. The pickaxe searches history for a **string** and needs no
running build; `bisect` searches history for a **behaviour** and needs a
pass/fail test that never lies. Both inherit the history simplification
described in [root-links.md](root-links.md), so both need `--all` before a
negative result means anything.

- [Choosing between the two](#choosing-between-the-two)
- [Pickaxe options](#pickaxe-options)
- [Scoping the pickaxe walk](#scoping-the-pickaxe-walk)
- [Bisect subcommands](#bisect-subcommands)
- [The git bisect run exit-code contract](#the-git-bisect-run-exit-code-contract)
- [What the test must guarantee](#what-the-test-must-guarantee)

## Choosing between the two

| The question | Instrument | Why the other one fails it | Source |
|---|---|---|---|
| When did this exact text enter or leave the repository | Pickaxe `-S` / `-G` | `bisect` needs a test that distinguishes the two halves; a string's presence rarely has one | synthesized |
| When did this behaviour start failing, with no idea which file is involved | `git bisect run` | The pickaxe can only search for text somebody already guessed | synthesized |
| A string is present but the defect is in how it is used | `git bisect run`, after the pickaxe narrows the suspect surface | Neither alone; the pickaxe finds candidates, `bisect` confirms which one changed behaviour | synthesized |
| Behaviour changed but no deterministic test exists | Neither — the pickaxe over the suspect surface, with the limitation stated | A flaky test makes every bisection step unreliable and the final answer discloses nothing about it | [git bisect](https://git-scm.com/docs/git-bisect) |

## Pickaxe options

| Option | What it matches | Use when | Source |
|---|---|---|---|
| `-S<block-of-text>` | Filepairs whose preimage and postimage contain a **different number of occurrences** of the text. Does not detect in-file moves | The text was added or removed and the count therefore changed — introduction and deletion of a symbol, a key, a call site | [diffcore-pickaxe](https://git-scm.com/docs/gitdiffcore#_diffcore_pickaxe_for_detecting_additiondeletion_of_specified_string) |
| `-G<regex>` | Filepairs whose textual diff contains an **added or deleted line matching** the regex. Does detect in-file moves, which upstream calls noise | A line containing the text was edited without changing how many times it occurs — exactly the case `-S` cannot see | [diffcore-pickaxe](https://git-scm.com/docs/gitdiffcore#_diffcore_pickaxe_for_detecting_additiondeletion_of_specified_string) |
| `--pickaxe-regex` | Reinterprets `-S`'s argument as an extended POSIX regular expression instead of a literal string | The target is a pattern rather than a fixed string, and the count-change semantics of `-S` are still what is wanted | [diffcore-pickaxe](https://git-scm.com/docs/gitdiffcore#_diffcore_pickaxe_for_detecting_additiondeletion_of_specified_string) |
| `--pickaxe-all` | Keeps the **entire changeset** when even one filepair matches, instead of only the matching filepairs | The finding needs the surrounding change for context — a one-file diff hides that the same commit also edited the caller | [diffcore-pickaxe](https://git-scm.com/docs/gitdiffcore#_diffcore_pickaxe_for_detecting_additiondeletion_of_specified_string) |

```sh
git log --all -p --pickaxe-all -S'MaxHealth' -- .
git log --all -p -G'MaxHealth' -- .
```

**Critical caveat**: `-S` is not a weaker `-G`, it is a different question. A
commit that changes `damage * 2` to `damage * 3` leaves the occurrence count of
`damage` unchanged and is therefore **invisible** to `-S'damage'` while
`-G'damage'` reports it. Reporting an `-S` result as an exhaustive content
search is the single most common wrong answer this instrument produces.

## Scoping the pickaxe walk

| Option | Effect on the walk | Source |
|---|---|---|
| `--all` | Substitutes every ref under `refs/` plus `HEAD`, so a commit that only ever lived on another branch is included. Excludes reflogs | [git rev-list](https://git-scm.com/docs/git-rev-list) |
| `--reflog` | Adds every object mentioned by a reflog — the only way a commit no longer on any ref enters the walk | [git rev-list](https://git-scm.com/docs/git-rev-list) |
| `-p` | Prints each matching commit's diff, which is what makes the result quotable as evidence rather than a bare sha | [git log](https://git-scm.com/docs/git-log) |
| `--follow` | Continues the walk across a rename of a **single** file; requires exactly one pathspec | [git log](https://git-scm.com/docs/git-log) |
| `--full-history` | Stops merges TREESAME to one parent from pruning the other side, so a string introduced on a merged branch is not skipped | [History Simplification](https://git-scm.com/docs/git-log#_history_simplification) |
| `-i` | Case-insensitive matching for the pickaxe and other regex options | [git log](https://git-scm.com/docs/git-log) |

## Bisect subcommands

| Subcommand | What it does | Source |
|---|---|---|
| `start` | Begins a session; optionally takes the bad and good revisions and a pathspec to limit the search | [git bisect](https://git-scm.com/docs/git-bisect) |
| `bad [<rev>]` | Marks a revision as containing the fault | [git bisect](https://git-scm.com/docs/git-bisect) |
| `good [<rev>]` | Marks a revision as free of it | [git bisect](https://git-scm.com/docs/git-bisect) |
| `new` / `old` | The same two marks under neutral terms, for hunting a change that is not a defect — a performance shift, an added behaviour | [git bisect](https://git-scm.com/docs/git-bisect) |
| `terms` | Prints the terminology in use, so a resumed or replayed session cannot be read with the polarity reversed | [git bisect](https://git-scm.com/docs/git-bisect) |
| `skip` | Excludes the current revision as untestable; accepts a range such as `v2.5..v2.6` | [git bisect](https://git-scm.com/docs/git-bisect) |
| `reset` | Ends the session and restores the original `HEAD`, or checks out a given commit instead | [git bisect](https://git-scm.com/docs/git-bisect) |
| `log` | Prints every mark made so far — this is the audit trail the finding cites as evidence | [git bisect](https://git-scm.com/docs/git-bisect) |
| `replay <logfile>` | Re-runs a session from a saved `log`, which is how a result is reproduced or a mis-mark is corrected without starting over | [git bisect](https://git-scm.com/docs/git-bisect) |
| `run <cmd>` | Automates the search, marking each revision from the command's exit code | [git bisect](https://git-scm.com/docs/git-bisect) |
| `visualize` / `view` | Opens `gitk`, or `git log` with no graphical environment, on the remaining suspects | [git bisect](https://git-scm.com/docs/git-bisect) |
| `next` | Requests the next step explicitly; normally automatic | [git bisect](https://git-scm.com/docs/git-bisect) |
| `--no-checkout` | Leaves the working tree alone and moves `BISECT_HEAD` instead; assumed for a bare repository | [git bisect](https://git-scm.com/docs/git-bisect) |
| `--first-parent` | Follows only first parents, so a merge is named as the introduction point rather than a commit inside the merged branch | [git bisect](https://git-scm.com/docs/git-bisect) |

## The git bisect run exit-code contract

| Exit code | Recorded as | Source |
|---|---|---|
| `0` | good / old | [git bisect](https://git-scm.com/docs/git-bisect) |
| `1`–`124` | bad / new | [git bisect](https://git-scm.com/docs/git-bisect) |
| `125` | cannot be tested — the revision is skipped | [git bisect](https://git-scm.com/docs/git-bisect) |
| `126`–`127` | bad / new, because the documented bad range is 1–127 except 125. These are also the shell's own "not executable" and "not found" codes, so a broken script path is silently recorded as a real failure | [git bisect](https://git-scm.com/docs/git-bisect) |
| `128` and above | Aborts the session. A program terminating via `exit(-1)` leaves 255, which aborts | [git bisect](https://git-scm.com/docs/git-bisect) |

**Critical caveat**: `run` reads nothing but the exit code, so a script that
prints a diagnosis and exits 0 is recorded as good — and the 126/127 overlap is
therefore a silent-failure mode, not a curiosity. A typo in the script path, a missing interpreter, or a lost
executable bit exits 127, which `bisect` faithfully records as **bad** at every
revision — producing a confident first-bad-commit that is simply the oldest
revision tested. Confirm the script exits 0 on a known-good revision and
non-zero on a known-bad one before handing it to `run`.

## What the test must guarantee

| Requirement | Consequence when it does not hold | Source |
|---|---|---|
| Deterministic verdict for a given revision | Every step compounds the flake, and the reported first-bad-commit carries no signal about it — the result looks identical to a sound one | [git bisect](https://git-scm.com/docs/git-bisect) |
| Exit code, not output text, carries the verdict | `run` never reads output; a script that reports failure in prose and exits 0 marks the revision good | [git bisect](https://git-scm.com/docs/git-bisect) |
| `125` for a revision that cannot build or run | Without it, an unbuildable revision exits non-zero and is recorded as bad, moving the answer to the wrong side of the range | [git bisect](https://git-scm.com/docs/git-bisect) |
| Independent of leftover state between revisions | A cache, generated file, or database left behind makes the verdict depend on the order revisions were tested, which `bisect` does not control | synthesized |
| No dependence on the working tree surviving checkout | Untracked build output persists across checkouts and can make an old revision pass or fail for reasons that have nothing to do with its code | synthesized |
| A reproducible verdict recorded before starting | Without a `good` revision that genuinely passes, the search range is wrong and every subsequent step is wasted | [git bisect](https://git-scm.com/docs/git-bisect) |

The commit `bisect` names is the first revision at which the test fails, which
is not the same claim as the commit that caused the fault; the distinction and
how to report it are in [attribution-honesty.md](attribution-honesty.md).
Whether the search range is even intact — a rewritten or force-pushed history
can have removed the real culprit — is settled first, per
[finding-lost-and-deleted-work.md](finding-lost-and-deleted-work.md).
