# Shared — Implementation Note Format

Applies to: every code submission that reaches a review gate — from any implementing agent or tech lead.
Consumed by `code-reviewer`, `security-reviewer`, `qa-lead`, `assurance-evaluator` and, where no gate ran, the
GD at CP4 (G82). Review agents are stateless: they see the dispatch, never the reasoning behind the code. The
note is what makes a single-pass review possible.

## Required fields

Written in English. A handoff, not a document — proportional to the change.

```
## Implementation Note — <feature or submission>
- Spec: <the Tech Spec, or the direct notes for a D1–D2 change, and the clauses this submission satisfies>
- Tier: <A1–A5, and the verification floor it owes — V1/V2/V3/V4>
- Attempts: <used / budget. Past the first, what the last attempt materially improved>
- Changed: <the files and what each one now does>
- Assumptions: <every decision made where the spec was silent — or "none">
- Known limitations: <what this submission does not do, and what breaks if a caller assumes otherwise>
- Deliberately out of scope: <what was noticed and left alone, with the agent-id that owns it — or "none">
- Verification done: <what the author actually ran, and what they did not, and why>
```

| Field | What makes it correct |
|---|---|
| **Spec** | Names the clauses, not just the document |
| **Tier** | What `Verification done:` is measured against |
| **Attempts** | The real count, never a default `1`, plus what improved — a bare count cannot evidence iteration |
| **Changed** | Real paths; a description is not a substitute |
| **Assumptions** | Every gap the author filled — an unstated assumption is indistinguishable from a bug at review |
| **Known limitations** | Carries into the feature root's `DEBT.md` from **A3** upward |
| **Deliberately out of scope** | Proves a nearby problem was seen and left alone on purpose |
| **Verification done** | "I ran it" vs "it compiles"; an impossible check is stated as impossible, with why |

The pipeline that dispatched the work assembles the note from the brief it sent and the agent's return;
where each field comes from is in `workflows/references/dispatch-brief.md`.

## Rules

- Every submission to a review gate carries a note; without one it is incomplete, not merely undocumented.
  One note per agent return, not per feature.
- **The note is owed whether or not a gate runs.** A declined gate means nobody independently checked the
  claim — never that the claim was not owed.
- Never claim verification you did not perform (`qa/verification-standards.md`).
- Never use the note to argue the design — a disagreement goes to `technical-architect`.
