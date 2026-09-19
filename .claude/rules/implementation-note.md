# Shared — Implementation Note Format

Applies to: every code submission that reaches a review gate — from `csharp-engineer`, `unity-engineer`, `ui-ux-programmer`, `technical-artist`, `netcode-engineer`, `server-authoritative-engineer`, and any tech lead submitting its own code. Consumed by `code-reviewer`, `security-reviewer` and `qa-lead`.

This file sits above the group rule folders, alongside `language-and-comments.md`. It defines the note that accompanies every code submission — the handoff `.claude/standards/client/coding-principles.md` requires under Handoff.

## Why it exists

Review agents are isolated and stateless: `code-reviewer` sees only the prompt it was dispatched with, never the reasoning that produced the code. Everything the reviewer needs to judge the submission has to travel with it. Without this note the reviewer either guesses at intent — and reports findings against a spec reading the author never held — or blocks and costs a round trip. The note is what makes a single-pass review possible.

## Required fields

Written in English, per `language-and-comments.md`. Keep it short: this is a handoff, not a document.

```
## Implementation Note — <feature or submission>
- Spec: <the Tech Spec, or the direct notes for a D1–D2 change, and the clauses this submission satisfies>
- Tier: <A1–A5, and the verification floor it owes — V1/V2/V3/V4>
- Attempts: <used / budget — or "1 / n" when the first attempt stood. Past the first, also what the last
  attempt materially improved over the one before it>
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
| **Tier** | What the reviewer measures `Verification done:` against. Without it, "verified" means whatever the author took it to mean, and a claim complete at V1 reads as a finding at V3. |
| **Attempts** | What `assurance-evaluator` scores iteration on. Absent, it assumes Attempt 1 and silently scores an iterated submission as a first pass. **The count alone is not enough**: `execution-loop.md` requires every retry to state what materially improved, and the gate scores exactly that — handed only `2 / 3`, it has a dimension it is told to score and nothing that can evidence it. A live assurance gate reported the iteration unevidenced and declined to assume improvement, which is correct and is a gap in the note rather than in the work. An exhausted budget is reported as a Continuation Debt Record per `execution-loop.md`, never as a quiet partial result. |
| **Known limitations** | Survives past the review. These carry into the feature root's `DEBT.md` — owed from **A3** upward the moment a limitation is carried past review — per `.claude/standards/client/feature-documentation.md`. |
| **Deliberately out of scope** | Proves a nearby problem was seen and left alone on purpose, rather than missed — this is what keeps the "stay scoped, flag separately" rule from looking like an oversight. |
| **Verification done** | Distinguishes "I ran it" from "it compiles". Never claim a check you did not run; QA reads this to decide what still needs covering. |

## Who assembles it

The note is assembled by the pipeline that dispatched the work — `.claude/workflows/feature-development.md` step 5 — rather than returned whole by the agent. No implementing agent's output envelope carries all eight fields — two of them, `Attempts:` and `Verification done:`, are carried by **no** envelope at all, which is why `workflows/references/development-brief.md` asks the agent to state both back. Only the pipeline knows which spec clauses it actually sent. Each field has exactly one source:

| Field | Comes from |
|---|---|
| **Spec** | The dispatch brief the pipeline wrote. It is the only party that knows which clauses it sent. |
| **Tier** | The feature's ledger and the dispatch brief — the caller's, because no agent holds a tier across runs. |
| **Attempts** | **What the agent stated back**, because the brief asked for it: no envelope has an attempts field, and attempts-used is knowable only at the moment of the return. Never a default `1` — `assurance-evaluator` reads that as a first pass and scores an iterated submission as one. Past the first attempt the brief asks for **what improved** alongside the count, for the reason in the table above; where the agent did not state it, record that it did not rather than leaving the field to read as a bare count. |
| **Changed** | The working-tree diff, read against the envelope's `Files:` / `Changed:` / `Authored:` / `Implemented:` — some envelopes report what now works rather than which paths changed. |
| **Assumptions**, **Known limitations** | The envelope's `Assumptions and known limitations:`. |
| **Deliberately out of scope** | A `Routed to:` the agent returned alongside `Status: Done` — it named an owner for something it saw and left alone. **This is the one approximation in the table.** An agent that notices a nearby problem and leaves it alone may instead record it under `Assumptions and known limitations:`, and returns `Routed to:` only when it actually routes — so this field can be empty when something was in fact set aside. Read it as evidence when present, never as proof of absence. |
| **Verification done** | The envelope's own verification field where it has one — `Performance:`, `Responsiveness verified:`, `Cost:`, `Behaviour under loss and latency:`. **`csharp-engineer`, `server-authoritative-engineer` and `tech-lead-sdk-platform` have none**, so the brief asks them directly; record what they state, including *why* a check was impossible where it was. Never a check nobody ran, and never left blank while the account of it sits under `Known limitations:` — a review gate reported exactly that split as a finding. |

## Rules

- Every submission to a review gate carries an Implementation Note, assembled per the table above. A submission without one is incomplete, not merely undocumented.
- One submission per agent return, not one per feature — the assembling pipeline hands each return on as it lands. `code-reviewer` counts strikes against "the same submission", and it is the checkpoint that aggregates a feature, not the review.
- An assembled note carries one known gap, marked in the table above. Closing it means adding the field to each implementing agent's output envelope; until a real review round trip proves that cost worth paying, the gap is stated rather than hidden.
- State assumptions rather than resolving them silently — an assumption stated is a review finding avoided.
- Never claim verification you did not perform; `.claude/standards/qa/verification-standards.md` governs what a claim of verification actually requires.
- **The note is owed whether or not a gate runs.** Review and QA are optional per `workflows/references/optional-gates.md`, and a declined gate means nobody independently checked the claim — never that the claim was not owed. Where no gate runs, the GD reads `Verification done:` against the floor at CP4, and the note is the only record that survives.
- Never use the note to argue the design. It records what was built and under what assumptions; a design disagreement is routed to `technical-architect`, not embedded here.
- Keep it proportional to the change — an A1/A2 fix needs a few lines, not a document. `effort-allocation.md`'s artifact budget applies to this note as much as to anything else it governs.