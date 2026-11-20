---
name: framework-backlog-journal-per-repo
description: Framework backlog is the records fwbacklog store, a journal per repo, never tracked in the framework repo
type: feedback
tags: [backlog, workflow, gitignore, records]
paths: [.workflow/framework-backlog.jsonl, .claude/skills/records/SKILL.md, .claude/skills/new-project/SKILL.md]
status: active
updated: 2026-11-20
---

Framework gaps go to the fwbacklog store: records.py fwbacklog add (skill records), journal .workflow/framework-backlog.jsonl with a gitignored records.db cache. The framework repo git-ignores the journal (each clone starts empty; session-start creates it); a game project tracks its own (/new-project). Game work goes to records.py backlog (.workflow/backlog.jsonl, /plan-game). There is no md template any more. **Why:** workflow-state-stores (2026-11-20) moved project-scope state from markdown to SQLite journals; supersedes feedback/framework-backlog-per-repo. **How to apply:** never write framework gaps to a tracked framework file or a .md backlog; use the records CLI.
