---
name: git-forensics
description: "Trace a change to the commit that caused it: blame with ignore-revs, log -L, pickaxe -S/-G, bisect run, where deleted work went, whether a secret entered history. Use when attributing a defect or a leak."
user-invocable: false
---

# Git Forensics

Not for: backups before a command (`git-safety-anchor`), restoring lost state (`git-recovery`), Unity asset/`.meta` specifics (`git-unity-repo`), whether a match is a real secret (`security-reviewer`), rotating a key or deciding a purge (`cto` plans it; `git-recovery` runs it).
Docs: https://git-scm.com/docs (unversioned: check `git --version` and `git <cmd> -h` before relying on a flag; `--help` opens a browser on Git for Windows). Pro Git: https://git-scm.com/book/en/v2.

| Reference | Read when |
|---|---|
| [blame-and-line-history.md](references/blame-and-line-history.md) | Which commit last changed a line, or `blame` lands on a reformat/move; `git log -L` |
| [content-search-and-bisect.md](references/content-search-and-bisect.md) | Searching history for a string, or hunting the commit that introduced a behaviour |
| [finding-lost-and-deleted-work.md](references/finding-lost-and-deleted-work.md) | Code is gone and the removing commit is unknown, or a commit is on no branch |
| [secret-history-archaeology.md](references/secret-history-archaeology.md) | Whether a credential ever entered history and is still reachable |
| [attribution-honesty.md](references/attribution-honesty.md) | Before naming a commit or author, or when asked who is responsible |

## Steps
1. **Frame the question**: line, string, behaviour, deletion, credential or ownership. Each has its own instrument; `blame` on a behaviour or `bisect` on a line returns a confident answer to the wrong question. No target (line range, string, or reproducible pass/fail check) -> ask; never pick one.
2. **Check the evidence is still reachable**: `git reflog --all` and `git fsck --unreachable --no-reflogs` (read-only; `--lost-found` writes under the git dir), per [finding-lost-and-deleted-work.md](references/finding-lost-and-deleted-work.md). A rebase, squash or force-push may have removed the real commit; report that, not the nearest survivor.
3. **Pick the instrument**: line -> `git blame` / `git log -L`; string -> pickaxe `-S`/`-G`; behaviour -> `git bisect run`; deletion -> `--diff-filter=D --full-history`; credential -> reachable-object sweep; ownership -> `git shortlog -sn`.
4. **Never trust a path-limited log's silence.** Default history simplification follows only one parent of a merge TREESAME to it, so a negative result proves nothing until re-run with `--full-history --all`.
5. **Blame with `-w -C -C -C`** plus `--ignore-rev` for known reformat commits; the default credits the last hand on the bytes, often a formatter or rename.
6. **`bisect` needs a deterministic pass/fail test first.** None exists -> say so and fall back to pickaxe over the suspect surface. `bisect start`/`run` checks out every step: radius 2, Editor closed, anchored. The script lives outside the working tree; in a Unity project it runs batchmode per step (`unity-batchmode-cli`) and exits `125` when a step cannot compile or license, never `1`. Every tool call must finish inside the 600 s foreground limit: when one check can take minutes (Unity batchmode), step instead of `bisect run` — run the check alone, then `git bisect good|bad|skip` from its exit code, one call each. A check that can pass 600 s (a cold batchmode reimport) runs with `run_in_background`; the agent resumes on its completion notice and reads the exit code from its output, never ending its turn with the session open for any other reason. `git bisect log` is saved, then `git bisect reset`, before returning; a session interrupted mid-way is reported with that log as the resume point.
7. **`-S` vs `-G`**: `-S` only sees a change in occurrence count; a same-count edit needs `-G`.
8. **Separate exposure from cause.** `bisect` lands on the first failing commit, often an innocent change that made a latent fault reachable. State which one the report names ([attribution-honesty.md](references/attribution-honesty.md)).
9. **Report the commit; a person only when asked**, with the identity field (`%an`/`%cn`) it came from. Ownership data (`shortlog`) is routing information, never an assessment: a question about someone's performance routes to `gd`.
10. **Every finding carries** location, expected, actual, evidence, and an owning agent-id (`qa-standards`).

## Never
- Name a person as the cause of a change: after rebase or squash the recorded author may never have written the line.
- Call a credential absent from history on the strength of `git log -S` over the current branch.
- Present a `bisect` result as the cause without checking for a latent fault, or run it on a non-deterministic check.
- Present `-S` as exhaustive.

## Output
```
## Forensics Finding — <what was traced>
- Question: line | string | behaviour | deletion | credential | ownership
- Reachable: <yes, or what was rewritten away and how that was established>
- Instrument: <exact command, verbatim, incl. blame detection level and ref scope>
- Location: <path:line, or the object/ref>
- Expected: <what should be there, and the source>
- Actual: <as observed>
- Evidence: <sha, author date, proving output>
- Cause vs exposure: <which, and how decided>
- Owner: <agent-id>
- Known limitations: <what this trace does not establish>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Run `git blame` and tell me who broke the damage falloff" -> declined in that form: a behaviour question. `git bisect run` on a stated check found the first failing commit, which only exposed a latent divide-by-zero introduced earlier; fix routed to `csharp-engineer`.
