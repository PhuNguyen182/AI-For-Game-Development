# Attribution Honesty — What Each Instrument Reports Versus What It Means

Sources: [git blame](https://git-scm.com/docs/git-blame), [git log](https://git-scm.com/docs/git-log#_pretty_formats), [git bisect](https://git-scm.com/docs/git-bisect), [git shortlog](https://git-scm.com/docs/git-shortlog), [Rewriting History](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History).
Covers: SKILL.md §4 — "Separate the commit that exposed a fault from the commit that caused it", "Report the commit, and report a person only when explicitly asked", "Treat ownership data as routing information, never as an assessment of a person".

Every instrument in this skill reports a fact that reads as a stronger claim
than it is. `blame` names the last hand on the bytes and is read as the origin;
`bisect` names the first failing revision and is read as the cause; a name
recorded on a commit is read as the person who wrote it. The tables below pair
each report with what it actually establishes, so a finding states the narrower
claim. Rows marked `synthesized` are reasoning from documented mechanics rather
than an upstream statement.

- [What the tool reports versus what it means](#what-the-tool-reports-versus-what-it-means)
- [Author versus committer](#author-versus-committer)
- [Cause versus exposure](#cause-versus-exposure)
- [Shortlog counts after a rewrite](#shortlog-counts-after-a-rewrite)
- [Ownership data as routing information](#ownership-data-as-routing-information)

## What the tool reports versus what it means

| The tool reports | What it actually means | Source |
|---|---|---|
| `git blame` names a commit for a line | The last commit to write those **bytes**, found by comparing parent and child. A reindent, a rename, an encoding change, or a licence-header sweep is the last writer as much as a logic change is | [git blame](https://git-scm.com/docs/git-blame) |
| The same line under `-w -C -C -C` names a different commit | The detection level, not the truth, changed. The level used is part of the finding; a report that omits it cannot be reproduced | [git blame](https://git-scm.com/docs/git-blame) |
| `--ignore-rev` moved the blame to an earlier commit | The line is now blamed on the previous commit that changed it — which may itself be another reformat that was not on the ignore list | [git blame](https://git-scm.com/docs/git-blame) |
| A line marked `*` under `blame.markUnblamableLines` | An ignored commit touched it and no other revision could be credited. This line has **no** honest author and must be reported as unattributed rather than assigned to the nearest commit | [git blame](https://git-scm.com/docs/git-blame) |
| `%an` on a commit | The author identity recorded in the commit object — which is metadata, overridable, and not evidence that this person typed the line | [git log](https://git-scm.com/docs/git-log#_pretty_formats) |
| `bisect` prints a first bad commit | The oldest tested revision at which the test failed, given the marks supplied and the test's verdicts | [git bisect](https://git-scm.com/docs/git-bisect) |
| `git shortlog -sn` ranks contributors | Commit counts grouped by author within the revision range walked — a count of commits, not of lines, effort, or ownership | [git shortlog](https://git-scm.com/docs/git-shortlog) |
| A `blame` result on a file that was moved | With no `-C`, the rename commit is the last writer of every line in the new path | [git blame](https://git-scm.com/docs/git-blame) |

## Author versus committer

| Operation | Author (`%an`) | Committer (`%cn`) | Source |
|---|---|---|---|
| The two fields themselves | `%an`/`%ae` is the author identity | `%cn`/`%ce` is the committer identity, and `git shortlog` groups by author unless `-c` / `--group=committer` is given | [git log](https://git-scm.com/docs/git-log#_pretty_formats) |
| Ordinary commit | The person committing | The same person | [git log](https://git-scm.com/docs/git-log#_pretty_formats) |
| Rebase | Preserved from the original commit | Whoever ran the rebase, with a new commit date | [Rewriting History](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History) |
| Cherry-pick | Preserved from the source commit | Whoever cherry-picked | [Rewriting History](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History) |
| Amend | Preserved unless explicitly reset | Whoever amended — so the sha changes while the author does not | [Rewriting History](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History) |
| `--author` override | Whatever string was passed, with no verification | The person who ran the command | synthesized |
| Applied patch or emailed series | Taken from the patch's `From:` header | The maintainer who applied it | synthesized |
| Squash of several commits | The **squashing** commit's author — the individual authors of the collapsed commits survive only in the message, if at all | synthesized |
| Filtered or rewritten history | Whatever the rewrite wrote; original identities may be gone entirely | [Rewriting History](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History) |

```sh
git log -5 --pretty=format:'%h | author %an | committer %cn | %s'
```

**Critical caveat**: when the two identities diverge, one of the operations
above happened and neither field by itself says who wrote the code. A squash is
the worst case — it makes the collapsed commits' authorship unrecoverable from
the commit object. After a squash, `blame` credits the
squashing commit's author for every line in it — which is why an attribution
claim on a squash-merge repository is a claim about the merge process, not about
who wrote the code.

## Cause versus exposure

| Claim a report can make | What justifies it | Source |
|---|---|---|
| "This is the first revision at which the test fails" | The `bisect` marks and the test's verdicts, reproducible from `git bisect log` | [git bisect](https://git-scm.com/docs/git-bisect) |
| "This commit caused the fault" | Reading the commit's diff and confirming it introduced the faulty logic — an additional step `bisect` does not perform | synthesized |
| "This commit exposed a latent fault" | The diff is innocent on its own but made a pre-existing defect reachable: a new call site into an already-broken function, a config change crossing a threshold, a timing change surfacing an existing race | synthesized |
| "The merge introduced it" | `bisect --first-parent` names the merge rather than a commit inside the merged branch, which answers "which merge brought it in", not "which commit wrote it" | [git bisect](https://git-scm.com/docs/git-bisect) |
| "Nothing before this commit was affected" | Only if every revision marked good was tested by the same deterministic check; a `skip`ped range is untested and appears in `git bisect log` | [git bisect](https://git-scm.com/docs/git-bisect) |
| "This commit is the cause", when the test was flaky | Nothing. A non-deterministic verdict corrupts the search silently and the result looks identical to a sound one | [git bisect](https://git-scm.com/docs/git-bisect) |

**Critical caveat**: the two route to different owners — a causing commit to
whoever owns the code it changed, an exposing commit to whoever owns the latent
defect it revealed. A report that does not say which of the two it named sends
the wrong agent after the wrong code.

## Shortlog counts after a rewrite

| Option | What it changes about the count | Source |
|---|---|---|
| `-s` | Suppresses descriptions, leaving a per-group commit count | [git shortlog](https://git-scm.com/docs/git-shortlog) |
| `-n` | Sorts by commit count instead of alphabetically by name | [git shortlog](https://git-scm.com/docs/git-shortlog) |
| `-e` | Adds the email, which is what separates two identities that share a display name | [git shortlog](https://git-scm.com/docs/git-shortlog) |
| `-c` / `--group=committer` | Groups by committer rather than author — the two rankings differ on any repository that rebases or applies patches | [git shortlog](https://git-scm.com/docs/git-shortlog) |
| `--group=trailer:<field>` | Groups by a commit-message trailer such as `Reviewed-by`; commits without the trailer are **not counted**, and a commit with several distinct values is counted once per value | [git shortlog](https://git-scm.com/docs/git-shortlog) |
| `--no-merges` | Excludes commits with more than one parent, equivalent to `--max-parents=1` | [git shortlog](https://git-scm.com/docs/git-shortlog) |

```sh
git shortlog -sne --no-merges HEAD
```

| Distortion | Effect on the ranking | Source |
|---|---|---|
| Squash-merge workflow | One commit per merged branch, credited to the squasher — contributor counts collapse toward whoever merges | synthesized |
| Rebase-heavy workflow | Author counts survive, committer counts concentrate on whoever rebases | [Rewriting History](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History) |
| History rewrite or filtered import | Counts describe the rewritten history only; pre-rewrite commits are not in the walk at all | [Rewriting History](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History) |
| Same person, several identities | Appears as separate groups unless a mailmap consolidates them; `-e` at least makes the split visible | [git shortlog](https://git-scm.com/docs/git-shortlog) |
| Path-limited range | History simplification prunes commits before `shortlog` ever groups them, so a per-file count is a lower bound, not a total | [History Simplification](https://git-scm.com/docs/git-log#_history_simplification) |
| Formatting, generated-file, and vendored-import commits | Inflate counts with commits nobody authored in any meaningful sense | synthesized |

## Ownership data as routing information

| Question asked | What ownership data can answer | What it cannot answer | Source |
|---|---|---|---|
| "Who should fix this file" | Which identities have commits in it recently, so the fix reaches someone with context | Whether that person is the right owner **now** — they may have left the area or the project | [git shortlog](https://git-scm.com/docs/git-shortlog) |
| "Who knows this code" | Where the commits cluster, as a starting point for routing | Knowledge held by a reviewer, a designer, or a pair who never appears as author | synthesized |
| "Who broke this" | Which commit changed the line, and under which detection level | Intent, competence, or fault — the commit may have implemented a spec, a review comment, or a decision made elsewhere | [git blame](https://git-scm.com/docs/git-blame) |
| "Whose performance is at fault" | Nothing. This is not a history question, and the routing for it is `gd` | Anything at all | synthesized |
| "Who owns the decision this commit encodes" | Nothing in the commit object records it; a commit implementing a spec is not the origin of the spec | The origin of the decision, which lives in the Tech Spec, not in history | synthesized |

Report the commit by default and a person only when the requester asked for
one; when a person is named, name the identity field it came from (`%an` or
`%cn`), the operations that could have changed it, and the detection level the
trace ran at. Findings carry the five elements `defect-reporting.md`'s "Every
finding carries five things" section requires, and every claim here that rests
on a git property rather than an upstream statement is marked `synthesized` so
a reader can weigh it accordingly.
