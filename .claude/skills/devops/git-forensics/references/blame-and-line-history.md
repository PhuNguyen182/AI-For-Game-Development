# Blame and Line History — Flags That Decide Which Commit Gets Credited

Sources: [git blame](https://git-scm.com/docs/git-blame), [git log](https://git-scm.com/docs/git-log).
Covers: SKILL.md §4 — "Pick the instrument from the question rather than from habit", "Neutralise whitespace, copies and moves before naming any commit".

`git blame` answers one question only: which commit last wrote the bytes now on
this line. Every flag below exists to move that answer closer to the commit
that changed the *meaning* of the line, by making a reformat, a move, or a copy
transparent to the walk. Where the question is how a line evolved rather than
who touched it last, `git log -L` is the instrument instead; the two are not
interchangeable, and the closing table says why.

- [Blame flags](#blame-flags)
- [Copy and move detection levels](#copy-and-move-detection-levels)
- [Ignoring reformat commits](#ignoring-reformat-commits)
- [Line evolution with git log -L](#line-evolution-with-git-log--l)
- [Blame versus log -L](#blame-versus-log--l)

## Blame flags

| Flag | Effect | Use when | Source |
|---|---|---|---|
| `-w` | Ignores whitespace when comparing the parent's version against the child's to find where a line came from | Always, unless the whitespace itself is the finding — it is the cheapest way to stop crediting a reindent | [git blame](https://git-scm.com/docs/git-blame) |
| `-M[<num>]` | Detects lines moved or copied **within the same file**; both groups are blamed on the parent via extra inspection passes. `<num>` is the lower bound of alphanumeric characters that must match, default 20 | A block was reordered inside one file and `blame` credits the reorder commit | [git blame](https://git-scm.com/docs/git-blame) |
| `-C[<num>]` | Adds cross-file detection on top of `-M`; `<num>` default 40, and the last `-C` given wins when several carry a `<num>` | Code was extracted into, or pulled out of, another file in the same commit | [git blame](https://git-scm.com/docs/git-blame) |
| `-L <start>,<end>` | Annotates only that line range. Accepts `<start>,+<n>` for a count, `/regex/` endpoints, and `:<funcname>` for a function body. May be given more than once | The question names specific lines — it also cuts the output to what can actually be quoted as evidence | [git blame](https://git-scm.com/docs/git-blame) |
| `--ignore-rev <rev>` | Treats the revision as if it never happened; lines it changed are blamed on the previous commit that changed them. Repeatable | A specific commit is known to be a reformat, rename, or licence-header sweep | [git blame](https://git-scm.com/docs/git-blame) |
| `--ignore-revs-file <file>` | Ignores every revision listed in the file, which must be in `fsck.skipList` format. Repeatable | More than one reformat commit pollutes the file, or the exclusions should outlive the single command | [git blame](https://git-scm.com/docs/git-blame) |
| `--reverse <start>..<end>` | Walks history **forward**, reporting the last revision in which each line still existed instead of the one that created it. Requires the path to exist at `<start>`; `--reverse <start>` means `<start>..HEAD` | The question is when a line disappeared, not when it arrived — pair with `-w` so a reformat is not reported as the removal | [git blame](https://git-scm.com/docs/git-blame) |
| `--porcelain` | Machine-readable output: full 40-byte sha, original and final line numbers, group size, author/committer identity and date, filename, subject, then the line prefixed by a TAB. Repeated commit headers are suppressed | The finding will be parsed or aggregated rather than read | [git blame](https://git-scm.com/docs/git-blame) |
| `--line-porcelain` | `--porcelain` with the full commit header repeated for **every** line — simpler to parse, larger output | Counting per-line authorship, where suppressed headers would break the count | [git blame](https://git-scm.com/docs/git-blame) |
| `blame.markIgnoredLines` | Marks lines whose change came from an ignored commit with `?` | Reporting an ignored-rev trace, so the reader can see which lines the exclusion moved | [git blame](https://git-scm.com/docs/git-blame) |
| `blame.markUnblamableLines` | Marks with `*` the lines an ignored commit touched that could not be attributed to any other revision | Same trace — a `*` line is a line the exclusion left with no honest owner, and must be reported as such rather than silently credited | [git blame](https://git-scm.com/docs/git-blame) |

## Copy and move detection levels

| Level | What it additionally scans | Source |
|---|---|---|
| `-M` | Moved or copied lines within the file being blamed | [git blame](https://git-scm.com/docs/git-blame) |
| `-C` | Lines moved or copied from other files **that the same commit also modified** | [git blame](https://git-scm.com/docs/git-blame) |
| `-C -C` | Additionally, copies from other files in the commit **that created the file** — this is the level that survives a file split or an extraction into a new file | [git blame](https://git-scm.com/docs/git-blame) |
| `-C -C -C` | Additionally, copies from other files in **any** commit in history — the widest, slowest level, and the only one that finds a line pasted in from a file the commit never touched | [git blame](https://git-scm.com/docs/git-blame) |

**Critical caveat**: each added `-C` widens the search and changes the answer,
not just the confidence — the level decides whether the reported commit is
where the line was *written* or merely where it was *pasted*. A trace at `-C`
and a trace at `-C -C -C` can name different commits for the same line, so the
finding must record which level produced it; a report that omits the level
cannot be reproduced or challenged.

## Ignoring reformat commits

Setting `blame.ignoreRevsFile` makes the exclusions permanent for everyone who
clones the repository:

```sh
git config blame.ignoreRevsFile .git-blame-ignore-revs
```

The file takes `fsck.skipList` format, and its comment is written in English
per `language-and-comments.md`'s Working language section:

```
# Reindent every C# file to Allman braces; no behavioural change.
89f6a2b4c1d0e7f38a5b6c2d9e0f1a2b3c4d5e6f
```

| Rule | Consequence | Source |
|---|---|---|
| One unabbreviated object name per line | An abbreviated sha is not the documented input form; the man page specifies "unabbreviated object name" and states no fallback | [git blame](https://git-scm.com/docs/git-blame) |
| Whitespace and `#` comments ignored | A comment can carry the reason for the exclusion without breaking the format | [git blame](https://git-scm.com/docs/git-blame) |
| Repeatable, and config is applied first | Command-line exclusions add to the configured list rather than replacing it | [git blame](https://git-scm.com/docs/git-blame) |
| Empty filename resets the list | The way to run a trace deliberately *without* the project's exclusions | [git blame](https://git-scm.com/docs/git-blame) |
| The comment states what the commit did | A later reader can judge whether the exclusion is still correct instead of trusting a bare sha | synthesized |

**Critical caveat**: upstream documents the required form but no error for a
malformed entry. Never conclude from clean output that an exclusion took
effect — enable `blame.markIgnoredLines` and confirm the `?` markers appear on
the lines the ignored commit touched, and report the exclusion as unverified if
they do not.

## Line evolution with git log -L

| Form | What it selects | Source |
|---|---|---|
| `-L` at all | Walks the history of a line range, printing every commit that changed it together with its diff — it implies `--patch` | [git log](https://git-scm.com/docs/git-log) |
| `-L <start>,<end>:<path>` | An absolute line range in that path | [git log](https://git-scm.com/docs/git-log) |
| `-L <start>,+<n>:<path>` | `<n>` lines starting at `<start>` | [git log](https://git-scm.com/docs/git-log) |
| `-L /<regex>/,<end>:<path>` | From the first line matching the regex to `<end>` | [git log](https://git-scm.com/docs/git-log) |
| `-L :<funcname>:<path>` | The body of the named function, tracked as it moves | [git log](https://git-scm.com/docs/git-log) |
| Repeated `-L` | Several ranges in one walk | [git log](https://git-scm.com/docs/git-log) |

## Blame versus log -L

| Axis | `git blame` | `git log -L` | Source |
|---|---|---|---|
| Answers | Which commit last wrote each line now present | Every commit that changed the range, oldest to newest | [git blame](https://git-scm.com/docs/git-blame), [git log](https://git-scm.com/docs/git-log) |
| Output shape | One commit per surviving line | One commit plus its diff per change | [git blame](https://git-scm.com/docs/git-blame), [git log](https://git-scm.com/docs/git-log) |
| Sees a line that was added and later removed | No — only surviving lines are annotated, unless `--reverse` is used | Yes, it appears as a change in the walk | synthesized |
| Whitespace neutralisation | `-w`, and exclusions via `--ignore-rev` | No equivalent exclusion mechanism | [git blame](https://git-scm.com/docs/git-blame) |
| Selects it | The line exists now and the question is its last author | The line changed repeatedly and the question is the sequence | synthesized |

Neither instrument answers a behaviour question. When the line is only a
symptom and the defect could have been introduced anywhere, the trace belongs
in [content-search-and-bisect.md](content-search-and-bisect.md); when the line
is gone entirely, in
[finding-lost-and-deleted-work.md](finding-lost-and-deleted-work.md). What any
of them may honestly be said to prove about a person is governed by
[attribution-honesty.md](attribution-honesty.md).
