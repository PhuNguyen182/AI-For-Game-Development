# C1 - live round-cap (criteria 6, 7)

- Feature: `.workflow/features/workflow-state-stores.md`
- Code under test: commit `29a5cbd` (`.claude/` layer extracted with `git archive`; `settings.local.json` absent). Review status: passed (round 3, code Approve, security Clear), CP3 approved.
- Harness: `claude` 2.1.328, Python 3.14.7, Windows. Run: `claude -p <prompt> --setting-sources project --allowedTools "Bash" "Agent" --max-turns 8 --max-budget-usd 1 --output-format stream-json --verbose --include-hook-events`, cwd = scratch repo outside the project. One session, not rerun (the model made all four calls in order).
- Raw log (local only, not committed): `C:\Users\Admin\AppData\Local\Temp\claude\8db747868b6de3cf\9cb5f018-855b-469c-bbce-45f36723e29e\scratchpad\live.jsonl` (63,485 bytes; 48 lines of interest listed by line number below)
- Prompt copy: `...\scratchpad\c1prompt.txt`
- Scratch repo (deleted after the run): 3 features registered via `records.py feature add`, rounds via `feature round`: `wss-live-cap` review 3/3, `wss-live-over` review 4/3, `wss-live-ok` 0/3; plus legacy md `wss-live-md.md` with `- Rounds: review 4/3, QA 0/2, rework 0/8`.

## Setup pre-check (outside claude)

`feature counters <slug> --json`:
- wss-live-cap: `"review": {"used": 3, "cap": 3}`
- wss-live-over: `"review": {"used": 4, "cap": 3}`
- wss-live-ok: `"review": {"used": 0, "cap": 3}`
- `feature round ... +4` was accepted (no refusal past cap), so the `ledger add` fallback was not needed. Rounds are stored as `round` events in `.workflow/features.jsonl`, not in the ledger; `ledger get --json` is `{}` before and after.
- Baseline `features.jsonl` SHA-256: `5EA1548F02B238D113E28784D29E1335C552149A52EC0BD25F8C2AC736DB0825`.

## Results

| # | Expected | Observed (stream log) | Verdict |
|---|---|---|---|
| SessionStart | `Records:` line; un-migrated line for the md feature | L5 `SessionStart:startup` outcome=success exit=0. Output contains `Records: backlog 0 open, framework backlog 0 open, debt 0 open, features 3 open` and `Records: not migrated - 1 feature file(s) with a '- Status:' line. Preview: ... migrate --from-md --dry-run ...`. Lists `wss-live-md - CP: ?` plus the 3 registered features. | pass |
| 1 Bash `feature show wss-live-cap` | at-cap warning, command itself runs | L13 `PostToolUse:Bash` (round-cap `-Mode edit`) exit=2, stderr: `Stop rule (routing.md):\nfeature wss-live-cap: review 3/3 - at the cap: technical-architect root-causes once (run records.py feature stop-rule wss-live-cap review --extra-dispatch unused), the owner gets one more dispatch; another failure stops the work.` L14 tool_result is_error=false, body `wss-live-cap | Open | ... Review rounds: 3/3`. The model saw the warning as a "PostToolUse:Bash hook blocking error" (exit 2 is how the harness delivers the text; the call had already run). | pass |
| 2 Agent code-reviewer, wss-live-over | blocked past cap, no subagent | L19 `PreToolUse:Agent` round-cap `-Mode dispatch` exit=2 (the editor-lock hook before it exit=0). L20 tool_result is_error=true: `PreToolUse:Agent hook error: [...round-cap.ps1 -Mode dispatch...]: Stop rule (routing.md): past the round cap - feature wss-live-over: review 4/3. Report to the main GD: what was tried, last verified state, next best action. Another round only on the main GD's order: ... records.py feature extra-round <slug> <counter> +n ...`. `tool_result_meta`: decision=reject, source=hook. No `task_started`, no `SubagentStop`, no subagent user message with this prompt. | pass |
| 3 Agent general-purpose, wss-live-ok | runs, returns OK | L24/L25 both `PreToolUse:Agent` hooks exit=0. `task_started` for `toolu_01C8StDaZb8M2YzKa8wbCexr` ("Check wss-live-ok feature"). L27 subagent got `Feature: .workflow/features/wss-live-ok.md / Reply with the single word OK.`. L36 result content `OK` (agentType general-purpose, totalDurationMs 4909, 0 tool uses). 3 `SubagentStop` hooks exit=0 (L31-L33). | pass |
| 4 Agent code-reviewer, wss-live-md (md fallback) | blocked | L40 editor-lock hook exit=0; L41 round-cap exit=2. L42 is_error=true: `... Stop rule (routing.md): past the round cap - feature wss-live-md: review 4/3. Report to the main GD ...`. decision=reject, source=hook. No `task_started` for it. | pass |
| Only one subagent in the whole log | exactly one (call 3) | `task_started` appears once, `tool_use_id` = call 3. | pass |
| State unchanged by blocked calls | `ledger get --json`, `feature counters wss-live-over --json` unchanged | After the run: `ledger get --json` = `{}` (same as before); `wss-live-over` review 4/3 (same); `wss-live-cap` 3/3 and `wss-live-ok` 0/3 (same); `features.jsonl` SHA-256 still `5EA1548F...0825` (byte-identical). The completed general-purpose subagent (SubagentStop `-Mode count`) charged nothing. | pass |
| Hook durations | record if present | Not present: `hook_started`/`hook_response` events carry no timestamp or duration field (fields: type, subtype, hook_id, hook_name, hook_event, output, stdout, stderr, exit_code, outcome, uuid, session_id). Only user/tool-result events are timestamped. Coarse data points: session `duration_ms` 44,949 for 5 turns including all PreToolUse/PostToolUse/SubagentStop/Stop hooks; wall time of the `claude -p` process 2 min 0.9 s (includes process and SessionStart startup). No hook was reported killed or timed out (all outcomes success or the intended exit 2). A per-hook figure against the 15 s kill is not available from this harness. | not measurable |

## Judge note

- Verdicts come from the hook/tool_result events above, not from the model summary (the model's summary matched).
- Exact wording matches the intended messages: `at the cap` warning, `past the round cap` block, md feature blocked with the same text (`feature wss-live-md: review 4/3`).
- The md fallback path resolved the feature from `- Rounds: review 4/3, ...` in the legacy file even though the registry had no record of `wss-live-md`.

## Observations (not failures)

- The workspace was untrusted in `-p` mode: stderr `Ignoring 96 permissions.allow entries from .claude/settings.json: this workspace has not been trusted.` Hooks still ran (so the cap fires in a headless session), and the `--allowedTools` entries covered the calls. Nothing in this case depended on the ignored allow entries.
- Call 1's at-cap text reaches the model through a PostToolUse exit 2 ("hook blocking error" label). It does not block the command; the command output was returned intact in the same tool_result. The label may read as an error to a model; wording only.
- The case ran a real model: total cost USD 0.54 (cap 1.00), 5 turns.

## Not covered

- Per-hook latency vs the 15 s kill (harness does not expose it) - owner: none; would need a timed standalone `round-cap.ps1` run.
- Workflow launch path (`matcher: Workflow`) - not exercised in this case.
- Bug-record (`Bug:` line) cap path through the live harness - not exercised here.
