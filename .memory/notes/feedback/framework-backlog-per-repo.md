---
name: framework-backlog-per-repo
description: Framework backlog lives per repo, from a template, never tracked in the framework repo
type: feedback
tags: [backlog, workflow, gitignore]
paths: [.claude/templates/framework-backlog.md, .workflow/framework-backlog.md, .claude/skills/new-project/SKILL.md]
status: active
updated: 2026-10-30
---

GD rule (2026-10-30): the framework backlog is created from .claude/templates/framework-backlog.md as .workflow/framework-backlog.md, outside .claude/. The framework repo git-ignores it (each clone starts empty; the session-start hook creates it). A game project commits its own copy (/new-project deletes the Framework-repo-only .gitignore block). Never add framework gaps to a tracked framework file; game work goes to .workflow/backlog.md (/plan-game).
