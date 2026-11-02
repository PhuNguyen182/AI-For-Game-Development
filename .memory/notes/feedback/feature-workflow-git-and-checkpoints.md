---
name: feature-workflow-git-and-checkpoints
description: GD decisions 2026-10-30: one local branch per feature, local commits allowed in /feature step 4 and the CP4 closure commit, push only on order, CP1 pick unranked
type: feedback
tags: [workflow, git, feature, cp1]
paths: [.claude/rules/core.md, .claude/skills/feature/SKILL.md]
status: active
updated: 2026-10-30
---

Decided by the GD on 2026-10-30 while fixing the workflow audit:
- Every M/L feature runs on a local branch feature/<slug> (git-expert creates it at /feature step 4); CP4 asks whether to merge it; Abandon asks delete (recommended) or keep with a DEBT entry.
- core.md commit exception: the main session may make the per-implementer commits of /feature step 4 and the CP4 closure commit (DEBT.md, feature file, backlog.md). /new-project's bootstrap commit still asks once. Push always waits for the GD's order.
- The CP1 direction pick is the one AskUserQuestion with no (Khuyen nghi) option: options unranked, in the researcher's order.
- Evidence policy: only .md and .png are committed under .workflow/evidence/; raw device dumps stay local; traces stay committed with wider redaction.
- Required UTF Edit/Play Mode tests per acceptance criterion for every M/L feature; per-feature folder layout and path-derived namespaces (asmdef rootNamespace + relative path).
