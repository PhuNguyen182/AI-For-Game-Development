---
name: git-forensics
description: >
  Trace a change to the commit that caused it, and attribute it without
  naming the wrong one. Instruments: `git blame -w -C -C -C --ignore-rev`,
  `.git-blame-ignore-revs`, `git log -L`, pickaxe `-S` and `-G`,
  `git bisect run`, `--diff-filter=D` with `--full-history`,
  `git reflog --all`, `git fsck --lost-found`, `git shortlog -sn`,
  `git rev-list --all`. Answers which commit introduced a line, a string, a
  behaviour or a credential, where deleted work went, and who holds context
  on a file. Not for: backing up before a command runs
  (`git-safety-anchor`), restoring lost state (`git-recovery`), Unity asset
  specifics (`git-unity-repo`).
---

# Git Forensics — Tracing a Change to Its Commit, and Attributing It Honestly

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short. "Read when" is a real condition, not a restatement of the topic.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Upstream git documentation roots and the history-simplification model every query below inherits | Starting any task here, or confirming a flag against the installed git version |
| [blame-and-line-history.md](references/blame-and-line-history.md) | `blame` flags that neutralise whitespace, copies and moves; `--ignore-rev` and `.git-blame-ignore-revs`; `git log -L` line evolution | Asking which commit last changed a line, or a `blame` result points at a commit that looks like a reformat |
| [content-search-and-bisect.md](references/content-search-and-bisect.md) | Pickaxe `-S` vs `-G`, `--pickaxe-regex`, `git log --all -p`, and the full `git bisect` procedure including `run`, `skip` and `replay` | Searching history for a string, or hunting the commit that introduced a behaviour rather than a line |
| [finding-lost-and-deleted-work.md](references/finding-lost-and-deleted-work.md) | `--diff-filter=D`, `--full-history`, `git show <sha>^:<path>`, `git reflog --all`, `git fsck --lost-found --unreachable`, `git stash list` | Code is gone and nobody knows which commit removed it, or a commit is no longer on any branch |
| [secret-history-archaeology.md](references/secret-history-archaeology.md) | Sweeping every reachable object for a credential pattern, `git rev-list --all` with `git grep`, stash and remote-ref coverage, and what reachability does not prove | Asking whether a credential ever entered history and whether it is still reachable |
| [attribution-honesty.md](references/attribution-honesty.md) | Why `blame` names the last hand not the origin; author vs committer after rebase, cherry-pick and amend; squash collapse; exposing vs causing commit; ownership data framing | Before naming any commit or author in a report, and whenever asked who is responsible |

## 1. Objective
Answer "which commit caused this" with evidence that survives challenge, and stop short of the two confident-sounding wrong answers this domain produces by default: naming a reformat, a file move, or a merge as the origin of a line, and presenting the commit `bisect` landed on as the cause when it only exposed a fault that had been latent for months. Also establishes whether the evidence is still reachable at all, so an investigation reports "the commit was rewritten away" instead of quietly blaming the nearest surviving one.

## 2. Role
Act as the repository forensics specialist for the devops track — the skill reached for whenever a defect, a deletion, a credential, or a file's ownership has to be traced back through history to a specific commit.

## 3. When to invoke this skill
- A defect exists and the question is which commit introduced it, by line, by string, or by behaviour.
- Code, a file, or a whole directory is gone and nobody knows which commit removed it.
- A credential or key may have been committed, and the question is whether it is still reachable in history.
- A file needs an owner for routing a fix, and the question is who has actually worked in it.
- Negative trigger: creating a backup ref before a command runs — that's `git-safety-anchor`.
- Negative trigger: restoring the lost commit once it is found — that's `git-recovery`; this skill locates and attributes, it does not repair.
- Negative trigger: why a `.unity` scene or `.meta` file changed the way it did — that's `git-unity-repo`.

## 4. How to use this skill
1. **Frame the question as a line, a string, a behaviour, a deletion, a credential, or an ownership question** — each resolves to a different instrument, and running `blame` on a behaviour question or `bisect` on a line question returns a confident answer to a question nobody asked.
2. **Confirm the evidence is still reachable before reading any of it** — a rebase, a squash, or a force-push can have removed the real commit, and `git reflog --all` plus `git fsck --lost-found` decide whether history still holds it, per [finding-lost-and-deleted-work.md](references/finding-lost-and-deleted-work.md). Report unreachable evidence as unreachable rather than blaming what survived.
3. **Pick the instrument from the question rather than from habit** — line to `git blame` or `git log -L`, string to pickaxe `-S`/`-G`, behaviour to `git bisect run`, deletion to `--diff-filter=D --full-history`, credential to a reachable-object sweep, ownership to `git shortlog -sn`. The selection tables live in [blame-and-line-history.md](references/blame-and-line-history.md) and [content-search-and-bisect.md](references/content-search-and-bisect.md), and the credential sweep in [secret-history-archaeology.md](references/secret-history-archaeology.md). Every path-scoped query inherits history simplification, which [root-links.md](references/root-links.md) explains.
4. **Neutralise whitespace, copies and moves before naming any commit** — run `blame` with `-w -C -C -C` and `--ignore-rev` for known reformat commits, because the default output credits the last hand that touched the bytes, which is routinely a formatter or a file rename.
5. **Give `bisect` a deterministic pass/fail test before starting it** — a flaky or manual check makes every subsequent bisection step unreliable in a way the final answer does not disclose; if no such test exists, say so and fall back to pickaxe over the suspect surface.
6. **Distinguish `-S` from `-G` on a content search** — `-S` reports commits that change how many times a string occurs, so a change that edits a line without altering the count is invisible to it, and `-G` is the one that matches the diff text itself.
7. **Separate the commit that exposed a fault from the commit that caused it** — `bisect` finds the first commit where the test fails, which is frequently an innocent change that made a pre-existing latent fault reachable; state which of the two the report is naming, per [attribution-honesty.md](references/attribution-honesty.md).
8. **Report the commit, and report a person only when explicitly asked** — author and committer diverge after rebase, cherry-pick and amend, a squashed commit's author is whoever squashed it, and a commit implementing a spec or a review comment is not the origin of the decision it encodes.
9. **Give every finding a location, an expected, an actual, evidence, and an owning agent-id** — adopting the five elements `defect-reporting.md`'s "Every finding carries five things" section requires, so the receiving agent can act without a follow-up question.
10. **Treat ownership data as routing information, never as an assessment of a person** — `git shortlog` answers who holds context on a file so the fix reaches someone who can make it; a question about whose performance is at fault is a decision for `gd`, not an output of this skill.
11. **Report and write in English** — per `language-and-comments.md`'s Working language section, including any `.git-blame-ignore-revs` entry authored along the way.
12. **Ask for the target when the trace has none** — a line range, a string, or a reproducible pass/fail check; `blame` without a target and `bisect` without a test both produce output that looks like a result, so state the gap rather than picking a target.

## 5. Specific goals / tasks this skill performs
- Name the commit that introduced a specific line, string, behaviour, or deletion, with the command that produced the finding.
- State whether the evidence is still reachable, and where it went when it is not.
- Recover the pre-deletion content of a removed file from the commit that removed it.
- Determine whether a credential ever entered history and whether it is still reachable today.
- Produce file-level ownership data for routing a fix to an agent with context.
- Author a `.git-blame-ignore-revs` entry for a known reformat commit so future traces skip it.
- Out of scope: creating backup refs (`git-safety-anchor`), restoring or rewriting anything (`git-recovery`), Unity asset and GUID interpretation (`git-unity-repo`), the verdict on whether found content is a real secret (`security-reviewer`), and the decision to rotate a key or purge history (`cto`).

## 6. Output format
```
## Forensics Finding — <what was traced>
- Question: line | string | behaviour | deletion | credential | ownership
- Reachable: <yes, or what was rewritten away and how that was established>
- Instrument: <the exact command run, verbatim>
- Location: <path:line, or the object/ref the finding sits in>
- Expected: <what should be there, and the source that says so>
- Actual: <what is there, as observed>
- Evidence: <commit sha, author date, and the output that proves it>
- Cause vs exposure: <which of the two this commit is, and how that was decided>
- Owner: <agent-id that owns the fix>
- Layer: Game.Core.* | Game.Client.* | repository metadata
- Known limitations: <what this trace does not establish>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what this trace does not establish — omit this line entirely if there are genuinely none>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "This cooldown line is wrong. Which commit did it?"
- Output: `git blame -w -C -C -C -L 88,92 -- <path>` named a commit whose diff was a whitespace-only reindent, so re-ran with `--ignore-rev` on it and reached the real change two commits earlier. Reported both shas, the instrument, and that a `.git-blame-ignore-revs` entry would make future traces on this file skip the reindent.

**Example 2**
- Input: "Just run `git blame` and tell me who broke the damage falloff, I'll take it up with them."
- Output: declined in that form — the request is a behaviour question, which `blame` cannot answer, and the deliverable is a commit rather than a person. Ran `git bisect run` against a stated pass/fail check instead, reported the first failing commit, noted that it exposed a latent divide-by-zero introduced earlier, and routed the fix to `csharp-engineer`. A question about the person routes to `gd`.

**Example 3**
- Input: "A whole folder of ability configs is gone and nobody knows when."
- Output: `git log --all --full-history --diff-filter=D -- <path>` located the deleting commit, which turned out to be a merge that dropped the directory silently; recovered the pre-deletion content with `git show <sha>^:<path>` and reported both the merge sha and the fact that `--full-history` was required, because history simplification hides exactly this case.

## 8. Edge cases & guardrails
- Never name a person as the cause of a change — `blame` reports the last hand to touch the bytes, and after a rebase or a squash the recorded author may never have written the line at all.
- Never present a `bisect` result as the cause without checking whether it merely exposed a latent fault — the two route to different fixes, and conflating them sends the wrong agent after the wrong code.
- Never run `bisect` on a non-deterministic check; every step compounds the flake, and the final answer carries no signal about it.
- Never conclude a credential is absent from history because `git log -S` on the current branch found nothing — the sweep must cover every reachable object, plus stashes and remote refs, per [secret-history-archaeology.md](references/secret-history-archaeology.md).
- Never omit `--full-history` when hunting a deletion; history simplification routinely hides the merge that removed the path.
- Never report `-S` as exhaustive for a content change — a same-count edit is invisible to it, and `-G` is the flag that sees it.
- If the request has no line range, no string, and no reproducible pass/fail check, ask for one rather than choosing a target — a trace against a guessed target returns a real commit for the wrong question.
- Producing ownership statistics about identifiable people requires that the requester asked for routing data; if the request is an assessment of someone's work, state that and route it to `gd`.
