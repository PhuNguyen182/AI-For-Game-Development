---
name: save-workmemory
description: "Summarize the session into WORKMEMORY.md at the feature root. Use when ending a session."
argument-hint: "[feature-root-path]"
allowed-tools: PowerShell, Read, Write, Edit, Glob, Grep, Bash
---

# Save work memory

## Steps
1. **Feature root:** `$ARGUMENTS`: feature root path, else infer from the files touched this session.
2. **Summary:** summarize this session: goal, decisions made, files changed, open issues, next step.
3. **File:** `WORKMEMORY.md` exists at the feature root → update it in place (merge, don't duplicate); else create it.
4. **Language:** write in English.
5. **Length:** keep `WORKMEMORY.md` under one page — it is a resume pointer for the next session, not a full log.
