---
name: engineering-standard-adr-authoring
description: "Write a lightweight ADR for an engineering standard the CTO sets: number, status, context, decision, scope, consequences, supersession. Use when a decision becomes a project or cross-project standard."
user-invocable: false
---

# Engineering Standard ADR

Not for: feature Tech Specs (`technical-architect`), per-submission Implementation Notes (the engineer), feature-root docs (`feature-docs`), making the decision (domain CTO skills), scoring (`tco-reversibility-scoring`).

`cto` drafts the ADR in its return; the main session writes it to `docs/adr/`.

## Steps
1. **Confirm a decision was made** — a Technical Decision with a non-empty "Standard set", an amendment, a reversal, a retirement, or a repeated review/escalation showing an assumed but unwritten standard. Call still open → status `Proposed`, or do not write it; an Active ADR binds downstream roles.
2. **Ask when the scope or triggering decision is unclear** — a standard bound to the wrong roles is worse than none.
3. **State the rule so a reviewer can fail a submission against it** — "gameplay code calls `IPhysicsProvider`, never the plugin" is checkable; "prefer clean abstractions" is not. An uncheckable principle is not an ADR (coding principles live in `csharp-standards`).
4. **Number it sequentially; never reuse a retired number** — supersession chains reference the numbers.
5. **Record the trigger and each rejected alternative with why it lost**, so a rediscovered option does not reopen the decision.
6. **State applies-to (roles or tracks) and the point-forward date** — existing code is `exempt` or `migrate by <date or trigger>`; never apply a standard retroactively without saying so.
7. **Supersede, never edit in place** — set the old record to `Superseded by ADR-<n>` and write a new one.
8. **Cite the source decision, do not restate it** — no TCO score or trade-off analysis copied in. Keep the record to about one screen.
9. **Name the log location** — no `docs/adr/` in the project → output `open gap` and propose the path.
10. **Write in English** (`core.md` → Language); only the closing reply to the GD is Vietnamese.

## Never
- Leave a binding standard only in a Technical Decision's prose; it gets a numbered record.

## Output
```
## ADR-<number> — <short title>
- Date: <YYYY-MM-DD>
- Status: Proposed | Active | Superseded by ADR-<number>
- Supersedes: ADR-<number> | none
- Source: <Technical Decision or domain skill output this records>
- Context: <trigger — foundational choice, escalation, vendor risk finding>
- Decision: <the checkable rule>
- Applies to: <roles/tracks> — point-forward from <YYYY-MM-DD>
- Existing code: exempt | migrate by <date or trigger>
- Alternatives rejected: <option — why it lost>
- Compliance check: <how a reviewer verifies it>
- ADR log location: <path> | open gap — no central log exists yet
- Routed to: <roles that comply; who checks>
```
On request only, add `Known limitations`, `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Add an ADR: prefer composition over inheritance" → declined: no triggering decision, rejected alternative or scope, and no reviewer can fail a submission against it.
