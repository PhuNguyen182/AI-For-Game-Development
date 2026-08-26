# Shared — Implementation Note Format

Applies to: every code submission that reaches a review gate — from `csharp-engineer`, `unity-engineer`, `ui-ux-programmer`, `technical-artist`, `netcode-engineer`, `server-authoritative-engineer`, and any tech lead submitting its own code. Consumed by `code-reviewer`, `security-reviewer` and `qa-lead`.

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

## Who assembles it

The note is assembled by the pipeline that dispatched the work — `.claude/workflows/feature-development.md` step 5 — rather than returned whole by the agent. No implementing agent's output envelope carries all six fields, and only the pipeline knows which spec clauses it actually sent. Each field has exactly one source:

| Field | Comes from |
|---|---|
| **Spec** | The dispatch brief the pipeline wrote. It is the only party that knows which clauses it sent. |
| **Changed** | The working-tree diff, read against the envelope's `Files:` / `Changed:` / `Authored:` / `Implemented:` — some envelopes report what now works rather than which paths changed. |
| **Assumptions**, **Known limitations** | The envelope's `Assumptions and known limitations:`. |
| **Deliberately out of scope** | A `Routed to:` the agent returned alongside `Status: Done` — it named an owner for something it saw and left alone. **This is the one approximation in the table.** An agent that notices a nearby problem and leaves it alone may instead record it under `Assumptions and known limitations:`, and returns `Routed to:` only when it actually routes — so this field can be empty when something was in fact set aside. Read it as evidence when present, never as proof of absence. |
| **Verification done** | The envelope's own verification field where it has one — `Performance:`, `Responsiveness verified:`, `Cost:`, `Behaviour under loss and latency:`. Where an envelope carries none, record that absence; never a check nobody ran. |

## Rules

- Every submission to a review gate carries an Implementation Note, assembled per the table above. A submission without one is incomplete, not merely undocumented.
- One submission per agent return, not one per feature — the assembling pipeline hands each return on as it lands. `code-reviewer` counts strikes against "the same submission", and it is the checkpoint that aggregates a feature, not the review.
- An assembled note carries one known gap, marked in the table above. Closing it means adding the field to each implementing agent's output envelope; until a real review round trip proves that cost worth paying, the gap is stated rather than hidden.
- State assumptions rather than resolving them silently — an assumption stated is a review finding avoided.
- Never claim verification you did not perform; `verification-standards.md` in the QA rules governs what a claim of verification actually requires.
- Never use the note to argue the design. It records what was built and under what assumptions; a design disagreement is routed to `technical-architect`, not embedded here.
- Keep it proportional to the change — a Simple-tier fix needs a few lines, not a document.