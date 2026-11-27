# model-tiers AC14 — PreToolUse on SubagentHandback feasibility probe (2026-11-26)

Main session. Probe script in the session scratchpad; registration in gitignored `.claude/settings.local.json`; both removed after the run.

- Matcher variant: A (`"matcher": "SubagentHandback"`), exit 2 block form. Variants B and C not needed.
- Settings loaded mid-session: yes — a main-session Grep with the nonce was refused by the control hook right after the file was written (no restart).
- Control (subagent Grep with the nonce): refused; marker `hook-probe: fired tool=Grep agent_type=log-triage ...`.
- First SubagentHandback (`probe first` + nonce): refused; marker `hook-probe: fired tool=SubagentHandback agent_type=log-triage ...`.
- Second SubagentHandback: delivered; the main session's Agent result is `Status: Done` / `Summary: probe second`; `probe first` never reached the main session.
- PreToolUse input for a subagent's call: `agent_type` present (`log-triage`); top-level keys `agent_id, agent_type, cwd, effort, hook_event_name, permission_mode, prompt_id, scratchpad_dir, session_id, tool_input, tool_name, tool_use_id, transcript_path`; SubagentHandback `tool_input` keys: `message`; `transcript_path` points to the session transcript, not the subagent's.
- Model: claude-haiku-5-5.
- Transcript evidence form: the block appears as the refused tool call's result carrying the hook's stderr marker; the subagent transcript holds no `hookName` attachment (AC14's attachment clause does not match this harness; the marker in the refused call's result is the evidence).
- Residue: `.claude/settings.local.json`, the probe script and the nonce file deleted; `git status --porcelain -- .claude` shows only the pre-existing untracked `.claude/DEBT.csv`; `verify-layer: OK (21 warning(s))`.

AC14: pass (feasible). Task 1 uses matcher `SubagentHandback` and the exit-2 block form; scope by `agent_type`.
