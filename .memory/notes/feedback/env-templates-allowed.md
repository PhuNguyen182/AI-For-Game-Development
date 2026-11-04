---
name: env-templates-allowed
description: GD 2026-11-02: .env.example/.sample/.template and *.pub may be committed; real .env*, id_rsa, keystores stay blocked
type: feedback
tags: [security, git, hooks]
paths: [.claude/hooks/common.ps1, .gitignore]
status: active
updated: 2026-11-02
---

The GD allowed committing secret-free templates: .env.example, .env.sample, .env.template and public keys (*.pub). pre-commit/pre-push skip them in the path rule (common.ps1 SecretPathRegex) and .gitignore un-ignores them; their content is still secret-scanned. The Read/Edit deny rules for **/.env.* in settings.json stay as they are. Also decided: commit the workflow audit fixes grouped by area, no push.
