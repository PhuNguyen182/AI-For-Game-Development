---
description: Summarize the current session's work into WORKMEMORY.md at the feature root — create if missing, update if present
argument-hint: "[feature-root-path]"
allowed-tools: Powershell, Read, Write, Edit, Glob, Grep, Bash
---

# Save work memory

`$ARGUMENTS`: feature root path, else infer from the files touched this session. Write in English.
Summarize this session: goal, decisions made, files changed, open issues, next step. If `WORKMEMORY.md`
exists at that root, update it in place (merge, don't duplicate); else create it. Keep it under one page —
this is a resume pointer for the next session, not a full log.
