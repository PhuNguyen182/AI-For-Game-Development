---
name: review-code-risks
description: "Static C#/Unity review for performance, memory, crash/ANR risk; report only. Use when auditing code for runtime risk."
argument-hint: "[file-or-directory-path...]"
allowed-tools: PowerShell, Read, Grep, Glob, Bash, Skill
---

# Review code for performance, memory, and hidden crash/ANR risk

- **Not for:** correctness (`code-reviewer`), measured verdict (`performance-qa-engineer`), confirmed fault (`/investigate-device-crash`), confirmed build fault (`build-fault-triage`).
- **Additive:** additive to the `Not for:` owners: name matches as risks to verify there, never as confirmed.
- **Input:** `$ARGUMENTS`: optional paths.
- **Final report:** to the GD in Vietnamese, code verbatim.

## References
- **[risk-patterns.md](references/risk-patterns.md):** scanning the scope: every pattern and the filter rules.

## Steps
1. **Scope:** `$ARGUMENTS` paths (`.cs` only), else `git diff --name-only HEAD -- '*.cs'` plus staged.
   - **Both empty:** never scan the whole repo; go to `Missing input`.
2. **Scan and filter:** per [risk-patterns.md](references/risk-patterns.md).
3. **Report:** most severe first, in the `## Output` form.
   - **Clean sweep:** say so, invent nothing.
   - **Fix direction:** names the change without writing it.
   - **Fields:** per `qa-standards` finding format.
4. **Missing input:** paths and diff both empty → dispatched agent `Blocked` or `Needs-decision`; main session `AskUserQuestion`.

## Never
- **Code edits:** edit code.
- **Confirmed claims:** claim a confirmed regression or crash from a static read.
- **Wider review:** widen into a full correctness or security review (route instead).
- **Gated skills:** invoke the gated crash-anr skills (read their reference files).

## Output
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
