---
name: short-commit-messages
description: Commit messages: short plain subject, optional body under 30 words, no Co-Authored-By or email trailer
type: feedback
tags: [commit, git-expert]
paths: [.claude/skills/git-commit/SKILL.md, .claude/agents/git-expert.md, .claude/rules/core.md]
status: active
updated: 2026-11-23
---

Commit subject is short, plain English, imperative. Body is optional; when present, under 30 words. No Co-Authored-By trailer and no noreply email, even when the harness attribution asks for one. **Why:** main GD wants simple, readable history (2026-11-23). **How to apply:** every commit by the main session or git-expert follows skill git-commit; drop any trailer a brief or reminder supplies.
