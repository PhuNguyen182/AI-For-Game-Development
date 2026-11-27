# Spec — model-tiers

Source: technical-architect, Spec mode, 2026-11-25 (attempt 2; revision before CP2 sign-off, no counter). Attempt 1 superseded.

## Changes from attempt 1
- **F1 (D-004):** new contract C5, the `log-triage-scan.ps1` SubagentStop hook: withheld return forms in C1, AC11 (behaviour), AC12 (registration), Task 2, hook-suite cases H1–H12, Known limits K1–K3.
- **F2 (D-003):** AC6 and the Evidence rule record, per AC3/AC5 dispatch, the log's total lines, the digest's line count and the transcript's token-usage totals (counts only).
- **F3 (D-003):** AC9: one `{ riskFlag: true }` run with no gates filter (also the task-8 review if the gate is taken) and one `{ gates: ['code'] }` run without `riskFlag` as the negative case.
- **F4 (D-005):** C2 threshold: more than 2,000 lines, or more than 300 lines with the error not yet located.
- **F5 (D-003):** C1 Status: a refused read → `Blocked`, naming the path. New AC13.
- **F6 (D-003):** `Route hint` and the route-hint map removed; the main session routes from `Class`.
- **F7 (D-003, LIM-001):** no Profiler source; OQ-1 closed.
- **Product-owner test note:** `Counts:` holds per-pattern matching-line counts; AC3 compares with `Select-String -CaseSensitive` without `-AllMatches`.
- **Follow-on:** C2 bullet 2 adds "a `digest withheld` return is `Blocked`"; tasks reordered (hook before C2–C4 edits, session restart before trials); verify.ps1 HookContracts entry for the withheld lines.

**Size:** M · **Risk flag:** set
**Why:**
- Size: `routing.md` → Size → M, "a new contract" (the digest and the hook's withheld forms, read by the main session, `ci-cd-engineer`, `/fix`, `/investigate-device-crash`).
- Not L: no new Core system, no netcode, no project-wide migration; direction locked (D-001/D-002).
- Risk flag: `routing.md` → Risk flag → "credential/signing … player PII": logs can carry tokens, keys, device ids, emails and user paths.
- Effect: verification means running (trials and hook suite); the gate offer recommends yes.

**Depth:** acceptance criteria + Contracts + Tasks + Tests (framework repo; Profile n/a). No Mermaid (M).
**Feature root:** `.claude/`. **Assemblies:** none. **Boundaries:** n/a.

## Contracts

### C1 — `log-triage` agent file
File: `.claude/agents/log-triage.md`.

**Frontmatter:** `name: log-triage` · `model: haiku` · `tools: Read, Grep, Glob` (exactly; no shell, Write, Edit, WebFetch or Skill) · `skills: [agent-protocol]` · `color: gray` · description (< 250 chars): "Reads a large log (Unity Editor/import, CI console, logcat, IL2CPP/Gradle/Xcode, UTF XML) and returns a redacted digest: first blocking error, counts, excerpt. Never a cause or fix."

**Why these tools:** no shell (the code-search guard lets a shell-less subagent Grep, `hooks/tests/run.ps1:774-786`); not an `editor-lock.ps1` holder (list unchanged); no Write/Edit (a digest never reaches a file); no WebFetch (nothing leaves the machine).

**Body sections:** Role / Inputs / Method / Checklist / Return extras / Never. Target ≤ 55 lines; one soft over-length warning acceptable.

**Inputs:** one or more absolute log paths; optional source type (`unity` | `ci` | `logcat` | `il2cpp` | `gradle` | `xcode` | `utf-xml`; else inferred) and the caller's question. Reads only the paths named; never walks `Library/`, `Temp/`, `Logs/` or `UserSettings/` with Glob.

**Method:**
1. Read `.claude/hooks/secret-patterns.txt` first (the redaction source).
2. One Grep `count`-mode call per signature, each reported separately — never an alternation, never a combined count (D-014); matching-line counts exactly as Grep returns them:
   - unity: `error CS\d+`, `Scripts have compiler errors`, `Exception`, `BuildFailedException`, licence failures
   - utf-xml: `result="Failed"`, plus the `<test-run` totals line (read, not counted)
   - logcat: `FATAL EXCEPTION`, `ANR in`, `Fatal signal`
   - gradle: `FAILURE: Build failed`, `What went wrong`
   - xcode: `error:`, `\*\* BUILD FAILED \*\*`
   - il2cpp: `il2cpp.*error`
3. Grep with line numbers and a capped hit count to find the first blocking hit.
4. Read only `offset`/`limit` windows of ≤ 200 lines; never a file of more than 2,000 lines whole.

**Redaction rule** (every line of the return — envelope fields and every digest line, `Log:` and `Not read:` included, not only quoted log lines; fail closed; amended after the attempt-1 trials, D-014):
- every `secret-patterns.txt` match → `<redacted:<pattern name>>`
- user token: the home-folder name taken from any path in the brief or the log (`C:\Users\<name>\`, `/Users/<name>/`, `/home/<name>/`) → `<user>` everywhere in the return, case-insensitive, also inside another token; counted as `user`
- email → `<redacted:email>`; IPv4/IPv6, device serial, Android ID, IDFA/GAID, `ro.serialno`-style values → `<redacted:id>`; URL query values for `token`, `access_token`, `key`, `sig`, `signature`, `auth`, `code` → `<redacted:query>`; `Authorization:`, `Cookie:`, `Set-Cookie:` values → `<redacted:header>`; Unity licence serial/ULF content → `<redacted:licence>`
- a line it cannot judge → `<line omitted: possible secret>`
- every mask and drop counted in `Redactions:`

**Return extras** (digest ≤ 40 lines inside the envelope):
```
Log: <path> · <total lines> · <source type> · <run id / commit / build if the log states it>
Read ranges: <line ranges actually read>
Counts (matching lines): <pattern> <n> · <pattern> <n> …   (utf-xml: total / passed / failed / skipped from <test-run>)
First blocking: line <n> · Class: <enum> · Location: <file:line | —>
Excerpt: ≤ 20 lines, each ≤ 300 chars, verbatim except redactions, around the first blocking hit
Other distinct errors: ≤ 5, one line each — line · class · first 120 chars, redacted
Redactions: <n> — <count per kind> | 0
Not read: <what was not examined; truncated / rotated / wrong-run log>
```
**Class enum:** compile | import | package | licence | test-failed | test-run-missing | il2cpp | gradle | xcode | signing | managed-exception | native-crash | anr | oom | unknown.

**Status:** `Done` (digest complete) · `Partial` (truncated, wrong run, or count cap hit; `Not read` says which) · `Blocked`, naming each path (masked): no path given, missing or empty file, refused read (permission denied).

**Stop-hook replies** (C5):
- a `log-triage-scan` message naming pattern kinds → mask those kinds and return the digest again
- a message asking for a withheld form → return exactly its two lines, nothing else (the one exception to the agent-protocol envelope)
- withheld forms: `Status: Blocked` / `Summary: digest withheld - redaction failed`; `Status: Blocked` / `Summary: digest withheld - secret scan unavailable`

**Never:** name a root cause, verdict or fix · quote an unredacted line · copy the log, transcript or a digest into any file · read paths the brief did not name · invent a count Grep did not return.

### C2 — routing.md Dispatch, two new bullets
Insert right after the `routing.md:60` bullet ("An agent's `model:` frontmatter is its default…"), in this order:
- `` `model: fable` `` (tiers: haiku < sonnet < opus < fable) only for: `technical-architect` root cause under the Stop rule; `cto` in `/decide` on an L or hard-to-reverse foundation (netcode, backend build-vs-buy, anti-cheat); `code-reviewer` on a risk-flag diff (workflow `review-gate`: `args.riskFlag: true`); `netcode-engineer` on an L task. Reason beside it.
- A log of more than 2,000 lines, or of more than 300 lines whose error is not yet located (CI console, Editor/import, logcat dump, IL2CPP/Gradle/Xcode, UTF XML) → `log-triage` first, in a brief with no `Feature:`/`Bug:`/`Target:` line; route from its `Class`. The next brief carries its digest and the raw log's path, never the log. A `digest withheld` return is `Blocked`.

### C3 — `review-gate.js` argument
- Header comment: add `riskFlag?: true`.
- Code: `const riskFlag = Boolean(args?.riskFlag)`.
- `runReview` passes `model: 'fable'` in the `agent()` options only when `riskFlag && gate.key === 'code'`.
- Security gate, skeptic and scope agent unchanged.

### C4 — consumer pointers, one bullet each
- `ci-cd-engineer.md` → Inputs → Run log: "the run's log, or a `log-triage` digest plus the log path. Absent → `Blocked`."
- `/fix` step 1 → **Evidence:** "a log over the `routing.md` threshold → `log-triage` digest; cite the raw path, never paste the log."
- `/investigate-device-crash` step 3 → **Full dump:** "`adb logcat -d` saved under `.workflow/evidence/<slug>/attempt-<n>/` (raw, gitignored) → `log-triage` digest when the filtered greps find nothing or the dump itself is the evidence."
- `/review` step 2 → under **Large diff** → **Risk-flag arg:** "`args.riskFlag: true` when the diff carries the risk flag (`routing.md` → Dispatch)."

### C5 — `log-triage-scan.ps1` SubagentStop hook
**File:** `.claude/hooks/log-triage-scan.ps1`, ASCII only (Windows PowerShell 5.1; verify.ps1 enforces). Header comment states the event, this contract and the fail-closed rules.

**Registration:** `.claude/settings.json` → `SubagentStop[0].hooks`, 4th entry after advisory-capture; no matcher (filters in-script):
```
{ "type": "command", "shell": "powershell", "command": "& \"$env:CLAUDE_PROJECT_DIR/.claude/hooks/log-triage-scan.ps1\"; exit $LASTEXITCODE", "timeout": 30 }
```

**Input fields used:** `agent_type`, `last_assistant_message`, `agent_transcript_path`, `stop_hook_active` (as `advisory-capture.ps1:8-9`, `editor-lock.ps1:142`).

**Scan set:** `$ScanAgents = 'log-triage'`, exact, case-sensitive (`-cnotcontains`).

**Flow** (first match wins; exit 2 returns the subagent with stderr as its instruction):
1. Unexpected error, caught by `trap` → exit 2: `log-triage-scan: scan failed (<exception type name>) - return withheld. Return only these two lines: Status: Blocked / Summary: digest withheld - secret scan unavailable`. Prints the exception type name only, never `$_` or its message.
2. `Read-HookInput` returns `$null` → exit 2: `log-triage-scan: no readable hook input - return not scanned.`
3. `agent_type` not in `$ScanAgents` → exit 0.
4. R = `(Read-SubagentExchange $in).Return` (SubagentHandback plus `last_assistant_message`, after the last prompt; `common.ps1:929-954`). If R is blank (no handback and `last_assistant_message` missing, empty or blank), the hook appends the transcript's last assistant text after the last prompt (fallback local to the hook; `common.ps1` unchanged); a non-blank R (a handback was found) gets no fallback, so a withheld form delivered by handback still passes step 5. Blank R and no transcript text → exit 2 with the step-1 text (`secret scan unavailable`). (Amended after review rounds 1–2, D-016.)
5. Every non-blank trimmed line of R is `Status: Blocked` or one of the two `Summary: digest withheld - …` lines, with a `Status: Blocked` line present → exit 0 (runs before the pattern check so the missing-patterns loop can end).
6. `$script:SecretPatterns.Count -eq 0` (file missing, empty or malformed; loader `common.ps1:5-14`) → exit 2: `log-triage-scan: .claude/hooks/secret-patterns.txt is missing, empty or malformed - return withheld. Return only these two lines: Status: Blocked / Summary: digest withheld - secret scan unavailable`.
7. N = pattern names whose regex matches R; the hook loops `$script:SecretPatterns` itself, never `Find-Secrets` (its hit lines carry a 6-char value prefix, `common.ps1:162`).
   - N empty or R blank → exit 0
   - N non-empty, `stop_hook_active` not true → exit 2: `log-triage-scan: the return carries secret-shaped text (<N joined ", ">). Mask each match as <redacted:<pattern name>> and return again.`
   - N non-empty, `stop_hook_active` true → exit 2: `log-triage-scan: still secret-shaped (<N>). Return only these two lines: Status: Blocked / Summary: digest withheld - redaction failed`

**Fail closed with the guard active:** the guard never lets a hit through; it switches the instruction to a fixed withheld form, which ends the loop because it carries no log text. A clean re-masked digest also passes while the guard is active.

**Never:** write a file · call mem, records or adv · print or log R, a match or any part of one · send anything but stderr naming pattern kinds.

**verify.ps1:** HookContracts entry `'.claude/agents/log-triage.md' = @('Summary: digest withheld - redaction failed', 'Summary: digest withheld - secret scan unavailable')`.

## Acceptance criteria
- **AC1:** `.claude/agents/log-triage.md` exists with the C1 frontmatter (`model: haiku`, `tools` exactly `Read, Grep, Glob`, `skills: agent-protocol`); `verify.ps1` passes with no new FAIL; any new warning is at most a soft agent-length one.
- **AC2:** A `log-triage` return has every C1 digest field and no `Route hint`; ≤ 40 digest lines; excerpt ≤ 20 lines; no root-cause or fix field.
- **AC3:** On the synthetic fixture: `First blocking` names the planted `error CS0246` line number and file:line; each `Counts` n equals `@(Select-String -LiteralPath <fixture> -Pattern <pattern> -CaseSensitive).Count`; `Read ranges` never cover the whole file.
- **AC4:** On the fixture: the final digest contains none of the 9 planted values; every `secret-patterns.txt` regex returns 0 hits on it; `Redactions:` ≥ 1.
- **AC5:** On the real logs (`%LOCALAPPDATA%/Unity/Editor/Editor.log`, `Editor-prev.log`, `upm.log`, one `aga001-night99/Logs/AssetImportWorker*-prev.log`): each return `Done` or `Partial`; `secret-patterns.txt` scan 0 hits; neither the OS username nor `C:\Users\<name>` appears; `First blocking` matches the first ripgrep hit of a blocking signature (compile error, `BuildFailedException`, fatal) — not the first hit of any signature, since a non-blocking `Exception` stack frame is not the blocker — or both report none (reworded by the main GD, D-013).
- **AC6:** For each AC3/AC5 dispatch, the transcript's assistant `message.model` is a `claude-haiku-*` id; `trial.md` records the log's total lines, the digest's line count and the token-usage totals (input, output, cache-creation, cache-read, summed by unique `message.id`).
- **AC7:** The C2 bullets sit right after the `routing.md:60` bullet, worded as C2; `git diff` shows no `model:` line changed in any existing `.claude/agents/*.md`.
- **AC8:** A `model: fable` dispatch of `technical-architect` (minimal read-only brief) has a `claude-fable-*` `message.model`.
- **AC9:** `review-gate` `{ riskFlag: true }` (no gates filter) runs `code-reviewer` on a `claude-fable-*` id and `security-reviewer` on its frontmatter model; `{ gates: ['code'] }` without `riskFlag` runs `code-reviewer` on its frontmatter model.
- **AC10:** The C4 pointers are present in all four files; the hook suite passes; a `log-triage` dispatch with no marker line is not blocked by `round-cap.ps1`.
- **AC11:** Hook-suite cases H1–H11 pass under `pwsh` and Windows PowerShell 5.1; no blocked case's output contains a planted value or its first 6 characters.
- **AC12:** `settings.json` registers the C5 entry (H12); verify.ps1 holds the C5 HookContracts entry; `verify.ps1` passes (incl. its ASCII check of the hook).
- **AC13:** A dispatch on a missing path returns `Blocked`; one on a read-denied path returns `Blocked` naming it.

## Tests
All rows owned by the main session; the implementer never signs off its own work.

| AC | How it is judged | Mode |
|---|---|---|
| AC1 | `verify.ps1`, diffed against the skill-pruning baseline (OK, 20 warnings) | command |
| AC2 | field list and line counts of the AC3 and AC5 returns | trial dispatch |
| AC3 | `log-triage` on the fixture; per-pattern `Select-String -CaseSensitive` line counts vs `Counts` | trial dispatch + command |
| AC4 | digest saved in the scratchpad; `Select-String -SimpleMatch` per planted value; each `secret-patterns.txt` regex | trial dispatch + command |
| AC5 | four dispatches; AC4 scans plus `$env:USERNAME`; first-hit comparison | trial dispatch + command |
| AC6 | AC3/AC5 transcripts: first `message.model`, summed `message.usage` by unique `message.id`; log lines via `(Get-Content).Count`; digest lines from the saved digest | command |
| AC7 | read `routing.md` 58-64; `git diff -U0 -- .claude/agents/` | command |
| AC8 | `Agent(subagent_type: technical-architect, model: fable)`, minimal brief; model id as AC6 | trial dispatch + command |
| AC9 | `review-gate` on this feature's diff `{ riskFlag: true }`, then `{ gates: ['code'] }`; model ids from gate transcripts | workflow run + command |
| AC10 | Grep the four C4 strings; `run.ps1`; the AC3 dispatch was not blocked | command |
| AC11 | `pwsh` and `powershell` `.claude/hooks/tests/run.ps1`; H1–H11 `PASS` | hook suite |
| AC12 | H12 `PASS`; Grep verify.ps1 for the entry; `verify.ps1` | hook suite + command |
| AC13 | dispatch on a nonexistent scratch path; dispatch on a scratch file under `icacls <f> /deny "$env:USERNAME:(R)"`, then `icacls <f> /remove:d "$env:USERNAME"` and delete | trial dispatch + command |

**Hook-suite cases** (new `# log-triage-scan` section in `.claude/hooks/tests/run.ps1`; `TriageStop` helper modelled on `SubStop`, `run.ps1:1178`; reuse `$fakeKey` (`run.ps1:13`), add `$fakeBearer = 'Bear' + 'er ' + ('x' * 24)`; every fake value built by concatenation):

| Case | Input | Expected |
|---|---|---|
| H1 | `agent_type: log-triage`, `$fakeKey` in `last_assistant_message`, guard false | 2; names `AWS access key`; contains neither `$fakeKey` nor its first 6 chars |
| H2 | as H1, value in a SubagentHandback transcript line, `last_assistant_message` `''` | 2 |
| H3 | as H1, guard true | 2; contains `digest withheld - redaction failed`; value absent |
| H4 | each withheld form, guard true | 0 |
| H5 | clean digest with `<redacted:AWS access key>`, `Bearer <redacted:Bearer token>`, `password=<redacted:credential assignment>` | 0 |
| H6 | `$fakeKey` return with `agent_type` `ci-cd-engineer`, then `Log-Triage` | 0 |
| H7 | hook copy (`common.ps1` + hook) with no `secret-patterns.txt`, clean return; same with a comment-only file | 2; contains `secret scan unavailable` |
| H7b | as H7, withheld form | 0 |
| H7c | withheld form via handback plus an extra assistant text line in the transcript, no-patterns hook copy | 0 |
| H8 | `'not json'` on stdin | 2 |
| H9 | no `last_assistant_message` key, transcript path missing | 2 |
| H9b | `last_assistant_message` `''`, no handback, transcript missing | 2; `secret scan unavailable` |
| H10 | no `last_assistant_message` key; transcript's last assistant text carries `$fakeBearer` | 2 |
| H10b | `last_assistant_message` `''`, no handback; transcript's last assistant text carries `$fakeBearer` | 2; no leak |
| H11 | H1 through `Invoke-HookUtf8 -Production` | 2 |
| H12 | parse `settings.json`: `SubagentStop` holds exactly one command naming `log-triage-scan.ps1`, timeout 30 | true |

**Fixtures:**
- AC3/AC4: built at runtime by one PowerShell command in the session scratchpad (never Write, never in the repo); ~5,000 noise lines; one `Assets/_Project/Scripts/Foo/Bar.cs(12,5): error CS0246` line; one later line with two `error CS` matches; within 10 lines of the CS0246 line, one fake value each built by concatenation: AWS-shape key, `Bearer` token, JWT, `password=` assignment (≥ 12 chars), email, `C:\Users\<name>\` path, IPv4, `ro.serialno` value, `?access_token=` URL. Deleted after the test.
- AC13 scratch file: deleted after its ACL is restored.

**Evidence:** `.workflow/evidence/model-tiers/attempt-<n>/trial.md` holds only `AC<n>: pass | fail`, counts, model ids, the AC6 line/token/digest-line counts, and `hook blocks observed: <n>` per dispatch (observed only). No excerpt, digest, transcript content, or transcript-folder path beyond its name.

## Tasks (in order)
1. `general-purpose`: `.claude/agents/log-triage.md` per C1, incl. Stop-hook replies (shape: `crash-anr-investigator.md`).
2. `general-purpose`: C5 — hook, `settings.json` entry, run.ps1 H1–H12, verify.ps1 HookContracts entry. Depends on 1.
3. Main session: `/verify-layer` and the hook suite under `pwsh` and `powershell` (AC1, AC11, AC12).
4. `general-purpose`: C2 `routing.md`, C3 `review-gate.js`, C4 `ci-cd-engineer.md`, `fix/SKILL.md`, `investigate-device-crash/SKILL.md`, `review/SKILL.md`. Depends on 1.
5. Main session: `/verify-layer` and the hook suite again (AC7, AC10).
6. Main GD: restart the session so `log-triage` loads and the SubagentStop entry is live (OQ-2).
7. Main session: trials AC2–AC6, AC8, AC13, then `trial.md`.
8. Gate offer (risk flag → recommend `/review` yes), then the AC9 runs; the `{ riskFlag: true }` run is the review if the gate is taken.

## Lanes
serial only — framework repo, mirror not adopted, no lane A body; tasks 2 and 4 depend on 1; every path under `.claude/`.

## Assumptions
- Large log: > 2,000 lines, or > 300 lines with the error not located (D-005); ≤ 300 lines read directly by the main session.
- Digest caps: 40 lines, 20 excerpt lines, 300 chars per line, 5 other errors. `Counts:` = matching-line counts per pattern, case-sensitive.
- Several paths: one refused or missing path makes the return `Blocked`, naming each. A withheld return is `Blocked`; the main session cites the raw path without a digest and tells the main GD.
- Redaction: `secret-patterns.txt` plus the C1 PII set; unclear line dropped. Backstops: `log-triage-scan.ps1` (secret shapes only), `secret-scan.ps1`, `pre-commit.ps1`, `bugs.py`/`journal.py` scans. PII relies on agent redaction plus AC4/AC5 checks; extending the hook to PII is a Minor change request.
- Hook: redaction tokens start with `<`, so `credential assignment` and `Bearer token` patterns do not match them (H5). Withheld forms are the only agent-protocol exception. A hook-input fault (H8) blocks every subagent stop (loud by design, `secret-scan.ps1:7` precedent). `Read-SubagentExchange` unchanged. `stop_hook_active` is true on every hook-caused continuation; only this hook sets it for `log-triage`.
- Trials: evidence keeps pass/fail, counts, model ids; digests stay in the scratchpad and are deleted. Model confirmed from transcript `message.model`; absent → `Not verified`. Token totals deduplicated by `message.id`. Gate declined → the AC9 `{ riskFlag: true }` run still runs both gates; findings shown as test output; `limitations` row "review offered and declined; AC9 run findings shown, not acted on".
- Wiring: `log-triage` briefs carry no `Feature:`/`Bug:`/`Target:` line (round-cap never charges them). Subagents have no Agent tool; the main session triages first. Unchanged: `build-release-engineer.md`, `/qa`, `ci-pipeline-failure-triage`, `build-fault-triage`, `common.ps1`, `editor-lock.ps1`, `round-cap.ps1`, `advisory-capture.ps1`. Fable sites need no edit beyond C2/C3; `review-gate` gives Fable only to the code gate. C2 adds 2 always-loaded lines (130 → 132).
- Fallbacks: workflow `agent()` rejects `model: 'fable'` → `/review` step 2 direct dispatch with `model: fable` (Minor). Reading `%LOCALAPPDATA%` and `aga001-night99/Logs/` may raise a permission prompt.

## Known limits (main GD acceptance at CP2 → `limitations` rows)
- **K1:** A hook killed at its timeout does not block (harness behaviour, `round-cap.ps1:52`); 30 s and a ≤ 40-line scan make it unlikely.
- **K2:** A model that keeps ignoring the withheld-form instruction loops until max turns or a user interrupt; leaks nothing, costs turns.
- **K3:** The hook does not catch PII shapes; that stays with agent redaction and the trial checks.

## Open questions
- **OQ-2 (technology):** new agents and `settings.json` hook changes may load only at session start; if `log-triage` is not dispatchable or the hook does not fire after tasks 1–2, the main GD restarts the session (task 6).

## Docs owed
- `log-triage.md` is the agent's doc; the C5 header comment is the hook's doc.
- Feature `tests` rows AC1–AC13; `decisions` rows for C3 and C5; `limitations` rows K1–K3 if accepted (LIM-001 exists); `/verify-layer` output after tasks 2 and 4.
