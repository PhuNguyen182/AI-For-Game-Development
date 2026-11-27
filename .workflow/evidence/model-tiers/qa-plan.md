# model-tiers QA plan (qa-lead, Plan mode, 2026-11-25) — verbatim summary of record

Written before Change 1. Change 1 (D-022..D-028) replaced AC11/AC12 and added AC14/AC15; the plan's per-AC rows for AC11/AC12 apply to the replaced criteria, and AC14/AC15 are judged against `model-tiers.change1.spec.md`.

- Size M, risk flag set, full treatment. Profile n/a (`.claude/` framework repo). Platforms: Windows, `pwsh` and Windows PowerShell 5.1. No open bugs. No Unity executors (qa-automation-engineer, playtest-tester, performance-qa-engineer, build-release-engineer own nothing). The spec's Tests table assigns every AC to the main session; that is the floor.
- Partitions: the 5,000-line fixture (one `error CS0246`, a later two-match line, 9 planted values) is the only input partition; boundaries covered: digest ≤ 40 lines, excerpt ≤ 20 lines, missing path, read-denied path. Routing thresholds are prose, not tested behaviour.

| AC | Existing evidence | Sufficient? | Run needed |
|---|---|---|---|
| AC1 | T-001 bare row | No | verify.ps1 at HEAD, warning diff vs baseline recorded |
| AC2 | attempt-2 trial.md | Yes, if log-triage.md unchanged since 2c898cd | git diff check |
| AC3 | attempt-2 | Yes, same check | covered by AC2 check and AC10 dispatch |
| AC4 | attempt-2 | Yes, same check | none |
| AC5 | attempt-2 | Yes (cite attempt 2 only) | none |
| AC6 | attempt-2 | Yes; add the `message.id` summation line | one line in trial.md |
| AC7 | T-004 bare row | No | routing.md 58-64 read + `git diff -U0 develop..HEAD -- .claude/agents/` |
| AC8 | attempt-1 | Yes | confirm technical-architect.md unchanged since 0d170dc |
| AC9 | attempt-2 + T-012 | Yes | confirm review-gate.js unchanged since afc5907; gate frontmatter `opus` |
| AC10 | T-013 | Partly | one live log-triage dispatch at HEAD (0 hook blocks, not blocked by round-cap) |
| AC11 | T-002 | Partly | attach named log-triage-scan PASS lines from the main-session runs |
| AC12 | T-003 | Same as AC11 | H12 line + verify result |
| AC13 | attempt-2 | Yes | none |

Exit criteria: AC1 verify at HEAD, no FAIL, only the agent-length warning new; AC2-AC6/AC13 attempt-2 figures with the unchanged-agent check; AC7 no existing `model:` changed; AC8 fable row + unchanged file; AC9 two workflow runs' model ids + unchanged review-gate.js + frontmatter; AC10 4/4 pointers + suite + one live dispatch; AC11/AC12 named PASS lines both shells + settings parse + HookContracts. QA cap: 6 rounds this session (D-020).
Sign-off gaps named then: LIM-005 unaccepted (since superseded by the live probe and Change 1, D-022, LIM-005 text); DEBT-001 noted debt (since Paid, 7a40d8d).
