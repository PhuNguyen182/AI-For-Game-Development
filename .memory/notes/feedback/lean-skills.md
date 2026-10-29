---
name: lean-skills
description: Skills stay minimal: lean template, no forced reads, Sonnet for bulk parallel agents
type: feedback
tags: [skills, authoring, token-cost]
paths: [framework-docs/skill-template.md, framework-docs/skill-reference-template.md]
status: active
updated: 2026-10-29
---

Every .claude skill follows framework-docs/skill-template.md and skill-reference-template.md: scope once in Not for:, no Objective/Role/When/Out-of-scope sections, no guardrail restating a step, no root-links.md, no per-row Source columns, TOCs or API indexes, no reference forced with 'starting any task', no generic knowledge; unreferenced references/scripts are deleted. **Why:** the GD ordered all skills minimised for token cost (2026-10-29); pilot + full pass cut skill docs ~67% with every decision-relevant fact kept. **How to apply:** write or edit any skill to the lean template; keep safety/gate rules and cited headings; for bulk parallel work across many files, run the parallel agents on Sonnet, each batch reviewed independently against git HEAD before fixes are accepted.
