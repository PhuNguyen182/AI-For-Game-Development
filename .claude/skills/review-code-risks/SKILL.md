---
name: review-code-risks
description: Static review of C#/Unity code for runtime performance, memory and hidden crash/ANR risk — report with fix direction only, never edits code
argument-hint: "[file-or-directory-path...]"
allowed-tools: PowerShell, Read, Grep, Glob, Bash, Skill
---

# Review code for performance, memory, and hidden crash/ANR risk

`$ARGUMENTS`: optional paths. Additive to `code-reviewer` (correctness), `performance-qa-engineer` (measured verdict), `/investigate-device-crash` (confirmed fault), `build-fault-triage` (confirmed build fault): name matches as risks to verify there, never as confirmed. Final report to the GD in Vietnamese, code verbatim.

1. **Scope** — `$ARGUMENTS` paths (`.cs` only), else `git diff --name-only HEAD -- '*.cs'` plus staged. Both empty → ask; never scan the whole repo.
2. **Scan and filter** — every pattern and the filter rules: [risk-patterns.md](references/risk-patterns.md).
3. **Report** — most severe first; clean sweep → say so, invent nothing. Fix direction names the change without writing it. Fields per `qa-standards` finding format.
```
## Code Risk Review — <scope>
- Status: Done | Blocked  |  Files reviewed: <count/paths or diff range>
### Findings
- Category: Performance | Memory | Crash/ANR risk
- Location: <path:line-range>  |  Expected: <clause>  |  Actual: <one line>
- Evidence: <quoted line(s)>  |  Severity: Critical|High|Medium|Low
- Fix direction: <one line, no diff>  |  Owner: <agent-id>
- Confidence: Static signal only — not measured, not reproduced on device
- Not covered: <paths skipped, anything needing measurement or a real device>
```

## Never
- Edit code.
- Claim a confirmed regression or crash from a static read.
- Widen into a full correctness or security review (route instead).
- Invoke the gated crash-anr skills (read their reference files).
