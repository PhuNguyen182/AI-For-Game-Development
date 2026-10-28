---
name: terse-framework-content
description: Agent, rule, skill and CLAUDE.md content must be maximally terse; plans in English
type: feedback
tags: [framework, style]
paths: [CLAUDE.md, .claude/rules/core.md]
status: active
updated: 2026-10-28
---

Agent, rule, skill and CLAUDE.md content: bullets/tables, short imperatives, no long prose, no rationale unless
omitting it causes wrong behaviour. Plans are 100% English.

**Why:** the GD found the old framework (12 rules, prose workflows, G/B/E ids) bloated; always-loaded context was ~160KB.

**How to apply:** any file under `.claude/` or `CLAUDE.md` — cut prose, never restate a fact that lives elsewhere, no ids
except CP1-CP4. Line budgets (CLAUDE.md 30, rules 100, agent body 25, pipeline 120) are targets, not limits; the
verifier warns, never fails, on line counts (GD decision 2026-10-28). Review and QA are optional gates the GD chooses
when asked — never auto-run them. Related: m:feedback/ask-via-multiple-choice.
