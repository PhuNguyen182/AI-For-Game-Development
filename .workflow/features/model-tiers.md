# Model tiers: Haiku log-triage and Fable escalation

- State: records.py feature show model-tiers
- Bugs: bugs.py list --feature model-tiers

<!-- State, rounds and stop rules live in the feature registry; each table below is a CSV the records CLI writes (skill records). -->

## Request (verbatim)
> giờ bạn và tôi cùng review về bộ agent này, hầu hết đền là sonnet và opus làm, nhưng chưa có vị trí nào là của haiku hay fable cả. Bạn hãy thảo luận cùng tôi xem có những vị trí, vai trò nào có thể dùng fable và haiku để tạo ra agent mới, hoặc dùng thay cho các agent hiện tại

Main GD pick (AskUserQuestion, 2026-11-25): "log-triage + Fable leo thang (Khuyến nghị)" — create the Haiku agent `log-triage` and add the Fable escalation rule to `routing.md` (technical-architect stop-rule root cause, cto on L / hard-to-reverse `/decide`, code-reviewer on risk-flag diffs, netcode-engineer on L tasks); trial on real logs before locking.

Change 1 (2026-11-26): Main GD pick (AskUserQuestion) "Chuyển sang PreToolUse (Khuyến nghị)" — a live probe showed the SubagentStop hook cannot withhold a SubagentHandback report (delivered to the main session before the stop hook runs); move the scan to a PreToolUse hook on SubagentHandback, first checking by a run that the harness lets a PreToolUse hook match that tool.

## Main GD decisions

- Rows: records.py csv render decisions --feature model-tiers

## Spec
Size M · risk flag set (logs can carry credentials and PII). Full spec, 13 acceptance criteria and test rows: `.workflow/features/model-tiers.spec.md`. Change 1 delta (Major; replaces C5, AC11, AC12; adds AC14, AC15): `.workflow/features/model-tiers.change1.spec.md`.

## Log

- Rows: records.py csv render log --feature model-tiers

## Tests

- Rows: records.py csv render tests --feature model-tiers

## Known limitations

- Rows: records.py csv render limitations --feature model-tiers
