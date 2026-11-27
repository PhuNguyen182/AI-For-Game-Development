# model-tiers — Change 1 spec delta

Source: technical-architect, 2026-11-26. Rated **Major**: CP2 again, CP1 closed (D-022 set the direction).
Replaces C5, the C1 "Stop-hook replies" block, AC11, AC12 and the Tasks list for the change request; adds AC14, AC15, A1–A10, K4, K5, OQ-3. Everything else in `model-tiers.spec.md` stands.
Rows going `stale`: T-001 (AC1), T-002 (AC11), T-003 (AC12), T-013 (AC10 suite part). AC2–AC9, AC13 stay `pass` (A8).
Code needing rework: `log-triage-scan.ps1` (`-Mode`, handback branch, header, delete line 81 = DEBT-001); `settings.json` (new PreToolUse group; SubagentStop command gains `-Mode stop`); `run.ps1:1233-1308` (`TriageStop -Mode stop`, new `TriageHandback`, P1–P13, H12 updated); `log-triage.md:54-57` (hook-reply bullets). Unchanged: `common.ps1`, `verify.ps1`, C2–C4 files.

## C1 — Hook replies (replaces "Stop-hook replies")
- A `log-triage-scan` message refusing a SubagentHandback and naming pattern kinds → mask those kinds and call SubagentHandback again with the digest.
- A message asking for a withheld form → call SubagentHandback (or return, if the harness has no SubagentHandback) with exactly its two lines, nothing else (the one exception to the agent-protocol envelope). Withheld forms unchanged.

## C5 — `log-triage-scan.ps1`, two modes (replaces C5)
- ASCII; first statement `param([string]$Mode = '')`, then the self-contained `trap`, worded per mode. `-Mode` is `handback` or `stop`; anything else → exit 2 `log-triage-scan: unknown -Mode - nothing scanned.` No `ValidateSet` (a binding error exits 1 before the trap = fail open). Header names both events, this contract and the fail-closed rules.
- **Registration:** PreToolUse group after the `Edit|Write|MultiEdit|NotebookEdit` group:
  `{ "matcher": "SubagentHandback", "hooks": [ { "type": "command", "shell": "powershell", "command": "& \"$env:CLAUDE_PROJECT_DIR/.claude/hooks/log-triage-scan.ps1\" -Mode handback; exit $LASTEXITCODE", "timeout": 30, "statusMessage": "Scanning the log-triage handback", "onFailure": "block" } ] }`
  If AC14 shows only a wildcard reaches the tool: matcher `*` plus an in-script `tool_name -cne 'SubagentHandback'` → exit 0. The SubagentStop 4th entry stays; its command gains `-Mode stop`.
- **`-Mode handback` flow** (first match wins; exit 2 refuses the tool call, stderr goes to the agent):
  1. trap → exit 2 `log-triage-scan: scan failed (<exception type name>) - handback withheld. Call SubagentHandback with only these two lines: Status: Blocked / Summary: digest withheld - secret scan unavailable` (type name only).
  2. `Read-HookInput` null → exit 2 `log-triage-scan: no readable hook input - handback not scanned.`
  3. `agent_type` present, non-empty, not in `$ScanAgents` (exact, `-cnotcontains`) → exit 0; absent or empty → scan (fail closed, A4).
  4. R = every string leaf of `tool_input`, recursive, depth cap 5 (over → throw → step 1), joined by newlines; field-name agnostic. `tool_input` missing or R blank → exit 2 `log-triage-scan: scan failed (no report text) - handback withheld. Call SubagentHandback with only these two lines: Status: Blocked / Summary: digest withheld - secret scan unavailable`.
  5. Withheld-form check on R (as stop step 5) → exit 0, before the patterns check.
  6. No patterns → exit 2 `log-triage-scan: .claude/hooks/secret-patterns.txt is missing, empty or malformed - handback withheld. Call SubagentHandback with only these two lines: Status: Blocked / Summary: digest withheld - secret scan unavailable`.
  7. N = matching pattern names (own loop, 1 s regex timeout, never `Find-Secrets`). Empty → exit 0. Non-empty → exit 2 `log-triage-scan: the handback carries secret-shaped text (<N joined ", ">). Mask each match as <redacted:<pattern name>> and call SubagentHandback again. If you cannot mask it, call SubagentHandback with only these two lines: Status: Blocked / Summary: digest withheld - redaction failed`.
- **Loop guard** (no `stop_hook_active` in PreToolUse): stateless — every hit block names both exits; both withheld forms always pass at step 5; a clean re-masked digest passes; a hit is never let through; a model that never complies loops to max turns and delivers nothing (K2).
- **`-Mode stop`:** current steps 1–7 unchanged, except step 7 "or R blank" and `log-triage-scan.ps1:81` are deleted (DEBT-001).
- **Fail closed:** trap, unreadable input, unknown mode, no report text and missing patterns each withhold; `onFailure: block` on the PreToolUse entry. **Never** and the verify.ps1 HookContracts entry unchanged.

## Acceptance criteria — replace AC11, AC12; add AC14, AC15
- **AC11:** hook-suite cases pass under `pwsh` and Windows PowerShell 5.1: H1–H11 (run with `-Mode stop`) and P1–P12; no blocked case's output contains a planted value or its first 6 characters.
- **AC12:** `settings.json` registers exactly one `log-triage-scan.ps1 -Mode handback` entry under PreToolUse matcher `SubagentHandback` (or `*` per AC14), timeout 30, `onFailure: block` (P13), and exactly one SubagentStop `-Mode stop` entry, timeout 30 (H12); HookContracts entry present; `verify.ps1` passes incl. the ASCII check.
- **AC14 (feasibility, first):** one live `log-triage` dispatch with the Task 0 probe registered: the control Grep is blocked (registration live); the first SubagentHandback carrying the nonce is refused and the subagent transcript holds the `hook-probe: fired` marker in that refused call's result (this harness writes no `hookName` attachment; D-026, approved by the main GD, D-029); the agent calls SubagentHandback again; the main session's Agent result holds `probe second` and not `probe first`; `probe.md` records `agent_type` (value or `ABSENT`), input key names and transcript kind; probe residue removed. Otherwise `Infeasible:` naming `probe.md`.
- **AC15 (live block):** a `log-triage` dispatch briefed to hand back, unmasked, the string joined from `AKIA` and `IOSFODNN7EXAMPLE` (brief names the halves only): the main session's Agent result contains neither the joined value nor `AKIAIO` and is a masked digest or a withheld form; the subagent transcript holds ≥ 1 refused SubagentHandback call whose result carries the `PreToolUse:SubagentHandback` hook error naming `AWS access key` (no `hookName` attachment in this harness; D-027, approved by the main GD, D-029); the leak dispatch takes at most 3 hook blocks before a masked digest or a withheld form is delivered (more → a K2 `limitations` row, not a pass; CP2, D-023); a control dispatch on the AC3 fixture is delivered with 0 blocks; `trial.md` records `hook blocks observed: <n>` for each.

## Tests — delta
| AC | How it is judged | Mode |
|---|---|---|
| AC11 | `pwsh` and `powershell` `run.ps1`; H1–H11 and P1–P12 `PASS` | hook suite |
| AC12 | P13 and H12 `PASS`; Grep verify.ps1 for the entry; `verify.ps1` | hook suite + command |
| AC14 | Task 0 probe; Grep -o of the subagent transcript for `hookName` and the marker; Grep of the Agent result for both markers; `git status --porcelain -- .claude` | probe dispatch + command |
| AC15 | leak dispatch plus fixture control; Grep -o of attachments; `Select-String -SimpleMatch` of the result for the joined value and `AKIAIO` | trial dispatch + command |

Hook-suite cases — helper `TriageHandback`: payload `@{ session_id; hook_event_name = 'PreToolUse'; tool_name = 'SubagentHandback'; agent_type; tool_input = @{ <field> = <report> } }`, invoked `-File log-triage-scan.ps1 -Mode handback`; reuse `$fakeKey`, `$fakeBearer`, `$leaky`, `$masked`, the withheld forms, `NoLeak`; `TriageStop` passes `-Mode stop`.

| Case | Input | Expected |
|---|---|---|
| P1 | `$leaky` in `tool_input.message` | 2; names `AWS access key`, `Mask each match`, `SubagentHandback again`, `digest withheld - redaction failed`; NoLeak |
| P2 | `$leaky` in `tool_input.report` | 2; NoLeak |
| P3 | clean `message` plus `$fakeBearer` in a second string field | 2; names `Bearer token`; NoLeak |
| P4 | each withheld form | 0 (×2) |
| P4b | withheld form plus a `$fakeKey` line | 2; NoLeak |
| P5 | `$masked` | 0 |
| P6 | `$leaky` with `agent_type` `ci-cd-engineer`, then `Log-Triage` | 0 (×2) |
| P6b | `agent_type` absent: `$leaky`, then `$masked` | 2, then 0 |
| P7 | hook copy, no patterns file / comment-only, `$masked` | 2; `secret scan unavailable` (×2) |
| P7b | as P7, each withheld form | 0 |
| P8 | `'not json'`, `-Mode handback` | 2; `no readable hook input` |
| P9 | no `tool_input`; then only blank strings | 2; `secret scan unavailable` (×2) |
| P10 | hook copy with patterns `slow<TAB>(a+)+$`; report 40 × `a` + `!` | 2; `scan failed (RegexMatchTimeoutException)`; no report text in output |
| P11 | P1 through `Invoke-HookUtf8 -Production` with `-Mode handback` | 2; NoLeak |
| P12 | no `-Mode`; then `-Mode bogus`, clean input | 2; `unknown -Mode` |
| P13 | parse `settings.json`: one PreToolUse command naming `log-triage-scan.ps1` with `-Mode handback`, matcher `SubagentHandback` (or `*`), shell `powershell`, timeout 30, `onFailure` `block` | true |
| H12 (updated) | one SubagentStop command naming `log-triage-scan.ps1` with `-Mode stop`, timeout 30 | true |

## Tasks (change request, in order)
0. **Main session — feasibility probe (AC14)**, no tracked file, no Editor:
   1. `hb-probe.ps1` in the session scratchpad, ASCII, self-contained: reads stdin as UTF-8; if the raw input contains `hbprobe-7f3a`, prints one stderr line `hook-probe: fired tool=<tool_name> agent_type=<value|ABSENT> keys=<sorted top-level keys> tool_input_keys=<sorted> transcript=<subagent|session|absent>` (`subagent` when `transcript_path` contains `\subagents\`) and exits 2; else exit 0; prints no other value.
   2. Register in `.claude/settings.local.json` (absent today; gitignored, `.gitignore:114`): two PreToolUse groups, matcher `SubagentHandback` and control matcher `Grep`, each `& '<scratchpad>\hb-probe.ps1'; exit $LASTEXITCODE`, shell `powershell`, timeout 15.
   3. Dispatch `log-triage`, no `Feature:`/`Bug:`/`Target:` line: "Probe, not a log task." (1) Grep pattern `hbprobe-7f3a` on one scratch file; (2) SubagentHandback `Status: Done` / `Summary: probe first hbprobe-7f3a`; (3) if refused, SubagentHandback `Status: Done` / `Summary: probe second`. If `log-triage` refuses, use `general-purpose`.
   4. Evidence `.workflow/evidence/model-tiers/attempt-4/probe.md`: pass/fail, attachment `type`/`hookName` counts, marker fields, matcher variant, whether settings loaded mid-session; no report text, no transcript path beyond the folder name.
   5. Branches (≤ 3 dispatches + one restart): control not blocked → settings not live → main GD restarts (OQ-2), rerun once; control blocked, handback not → variant B (matcher `*`); handback hook fired but report still delivered → variant C (stdout `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"hook-probe"}}`, exit 0; `search-guard.ps1:62` precedent) — if C works, C5 blocks use it; all fail → `Infeasible: a PreToolUse hook cannot withhold SubagentHandback (probe.md)` → main GD; `agent_type` ABSENT → stop, `Needs-decision` (scanning every handback is project-wide → `/decide`).
   6. Remove `.claude/settings.local.json` and `hb-probe.ps1`; `git status --porcelain -- .claude` clean of probe residue; `/verify-layer`.
1. `general-purpose`: C5 rework (hook, `settings.json`, run.ps1 P1–P13, H-cases with `-Mode stop`, H12, DEBT-001) and the C1 hook-reply bullets in `log-triage.md`. Depends on Task 0 pass; matcher and block form per Task 0.
2. Main session: `/verify-layer` and the hook suite under `pwsh` and `powershell` (AC1, AC10 suite part, AC11, AC12).
3. Main GD: restart the session if Task 0 showed settings load only at session start.
4. Main session: AC15 dispatches, then `attempt-4/trial.md`.
5. Gate offer (risk flag → recommend `/review` yes on the rework diff).

## Assumptions — add
- **A1:** the handback input field is `message` in every sampled transcript (0 `report`); the hook reads every string leaf, so the name does not matter.
- **A2:** the SubagentStop entry stays as a second layer for a harness that delivers closing text; never the only guard on a handback.
- **A3:** one script, explicit `-Mode`; an unknown or missing mode blocks.
- **A4:** missing `agent_type` → scan (fail closed); Task 0 stops for a decision if subagent calls lack it (`search-guard.ps1:10` relies on it).
- **A5:** stateless loop guard; counting earlier blocks from `transcript_path` rejected (unverified for subagent PreToolUse input).
- **A6:** `onFailure: block` per the `secret-scan.ps1` precedent; its timeout effect not verified live (K1).
- **A7:** the probe registers in gitignored `.claude/settings.local.json`; tracked `settings.json` untouched for the probe.
- **A8:** AC2–AC6 and AC13 stay `pass` (the agent-file edit is limited to the hook-reply bullets, never exercised by those trials); CP2 may overrule.
- **A9:** the AC15 brief names the key halves only.
- **A10:** DEBT-001 folded into Task 1; the main session closes it in `.claude/DEBT.csv`.

## Known limits — amend (limitations rows if accepted)
- **K1 (amended):** a hook killed at its timeout — the PreToolUse entry has `onFailure: block`, expected to block, not verified live; the SubagentStop entry behaves as LIM-002.
- **K2 (amended):** no attempt counter; a model ignoring both exits loops to max turns, delivers nothing, costs turns.
- **K3:** unchanged.
- **K4 (new):** the SubagentStop `-Mode stop` path is shown only by the hook suite (this harness does not deliver closing text); supersedes LIM-005 for that path; AC15 covers the handback path.
- **K5 (new):** only `log-triage` handbacks are scanned; another agent quoting a log relies on its own redaction and `core.md` → Security.
- **If AC14 ends `Infeasible:`:** accept the gap (SubagentStop only; agent redaction; a `limitations` row), drop `log-triage`, or change direction.

## Open questions — add
- **OQ-3 (technology):** does PreToolUse fire on and block `SubagentHandback`, and is `agent_type` in its input? AC14 answers; a negative answer goes to the main GD.

## Docs owed — add
- `decisions` row for the revised C5 (D-022 plus the matcher and block form chosen by Task 0); `limitations` rows K4, K5 and amended K1/K2 if accepted; LIM-005 marked superseded; `tests` rows for AC14 and AC15; T-001, T-002, T-003, T-013 set to `stale`; `attempt-4/probe.md` and `attempt-4/trial.md`.
