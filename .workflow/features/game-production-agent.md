# Game production agents

- State: records.py feature show game-production-agent

## Request (verbatim)
> tôi muốn thảo luận với bạn về đội agent, hiện tại, đang chỉ tập trung vào phần đội ngũ kỹ sư nhưng chưa có đội ngũ GD, PO và MO cùng thảo luận với người dùng để có hướng đi phát triển tốt hơn về game design, product quality. Đồng thời, cố vấn tôi workflow làm việc với đội PO, GD và MO đấy. Mục tiêu là cải thiện, cố vấn về chất lượng sản phẩm, tính năng, độ hoàn thiện, và khả năng kiếm tiền. Sau khi có các workflow, tùy vào công việc sẽ trigger workflow riêng biệt cho sản phẩm, monet và quá trình thực hiện sản phẩm

## Main GD decisions

- Rows: records.py csv render decisions --feature game-production-agent

## Spec
`docs/superpowers/specs/2026-11-05-product-advisory-team-design.md`

### Acceptance criteria
- AC1 Rename: role term is `main GD` across `.claude/`, `CLAUDE.md`, `README.md`, `framework-docs/`; old `## GD decisions` still counted by `round-cap.ps1`; hook and bug tests green.
- AC2 Store: `adv.py` stores, queries, decides and marks findings; refuses to write when its path is not git-ignored; refuses secret shapes.
- AC3 Leak: adviser briefs, returns and marked assistant text leave no figure in a captured trace; an unterminated marker strips; `pre-commit` blocks a staged `measured` label or an advisory marker.
- AC4 Not blocked: an adviser dispatch passes on a past-cap feature and with a corrupt ledger; `code-reviewer` is still blocked.
- AC5 Simulator: golden output; weakest-label propagation; `proposed` excluded.
- AC6 Data pack: rejects a PII header; accepts an aggregated pack.
- AC7 Layer: 3 agents, 4 method and protocol skills, 3 workflow skills; `/verify-layer` passes.
- AC8 Pipeline: routing rows, `core.md` exception, `/plan-game`, `/feature`, `/new-project`, `CLAUDE.md` template updated.
- AC9 Spike: `SendMessage` continuation, SubagentStop firing and transcript shape recorded; the follow-up default follows the result.
- AC10 Pilot: each workflow run once on the test game; main GD marks findings.

## Log

- Rows: records.py csv render log --feature game-production-agent

## Tests

- Rows: records.py csv render tests --feature game-production-agent

## Bugs

- Bugs: bugs.py list --feature game-production-agent

## Known limitations

- Rows: records.py csv render limitations --feature game-production-agent

<!-- Label syntax is written as "(open bracket)measured:" here: pre-commit blocks the literal label outside the framework's own files. -->
