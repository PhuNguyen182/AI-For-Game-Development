# Shared — Implementation Note Format

Applies to: every agent that submits work to a review gate — C# Software Engineer, Unity Engineer, UI/UX Programmer, Technical Artist, Netcode Engineer, Server-Authoritative Logic Engineer, and every Tech Lead submitting its own code. Consumed by Code Reviewer, Security Reviewer and QA Lead.

This file sits above the group rule folders, alongside `language-and-comments.md`. It defines the note that accompanies every code submission — the handoff `.claude/rules/client/coding-principles.md` requires under Handoff.

## Why it exists

Review agents are isolated and stateless: `code-reviewer` sees only the prompt it was dispatched with, never the reasoning that produced the code. Everything the reviewer needs to judge the submission has to travel with it. Without this note the reviewer either guesses at intent — and reports findings against a spec reading the author never held — or blocks and costs a round trip. The note is what makes a single-pass review possible.

## Required fields

Written in English, per `language-and-comments.md`. Keep it short: this is a handoff, not a document.

```
## Implementation Note — <feature or submission>
- Spec: <the Tech Spec, or the direct notes for a Simple-tier change, and the clauses this submission satisfies>
- Changed: <the files and what each one now does>
- Assumptions: <every decision made where the spec was silent — or "none">
- Known limitations: <what this submission does not do, and what breaks if a caller assumes otherwise>
- Deliberately out of scope: <what was noticed and left alone, with the agent-id that owns it — or "none">
- Verification done: <what the author actually ran, and what they did not>
```

| Field | What makes it correct |
|---|---|
| **Spec** | Names the clauses, not just the document. A reviewer checking "correct" against the whole spec reviews the wrong thing. |
| **Changed** | Real paths. A description of the change is not a substitute — `code-reviewer` blocks without the code or diff in scope. |
| **Assumptions** | Every gap the author filled themselves. This is the single highest-value field: an unstated assumption is indistinguishable from a bug at review time. |
| **Known limitations** | Survives past the review. For a Complex-tier feature these carry into the feature's `README.md`, per `.claude/rules/client/feature-documentation.md`. |
| **Deliberately out of scope** | Proves a nearby problem was seen and left alone on purpose, rather than missed — this is what keeps the "stay scoped, flag separately" rule from looking like an oversight. |
| **Verification done** | Distinguishes "I ran it" from "it compiles". Never claim a check you did not run; QA reads this to decide what still needs covering. |

## Rules

- Every submission to a review gate carries an Implementation Note. A submission without one is incomplete, not merely undocumented.
- State assumptions rather than resolving them silently — an assumption stated is a review finding avoided.
- Never claim verification you did not perform; `verification-standards.md` in the QA rules governs what a claim of verification actually requires.
- Never use the note to argue the design. It records what was built and under what assumptions; a design disagreement is routed to `technical-architect`, not embedded here.
- Keep it proportional to the change — a Simple-tier fix needs a few lines, not a document.