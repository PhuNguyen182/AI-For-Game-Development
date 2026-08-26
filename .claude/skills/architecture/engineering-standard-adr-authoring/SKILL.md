---
name: engineering-standard-adr-authoring
description: >
  Lightweight Architecture Decision Record format for recording a cross-project
  engineering standard the CTO sets — ADR number, Status
  (Proposed/Active/Superseded by ADR-n), Context, Decision, Applies-to scope
  with a point-forward date, and rejected alternatives — so the standard is a
  durable, checkable artifact rather than prose buried in one Technical
  Decision. Use whenever a Technical Decision's "Standard set" field is
  non-empty, or when an existing standard is amended or superseded.
  Not for: feature-level Tech Specs (`technical-architect`), per-submission Implementation Notes (individual engineers), feature README files (`feature-documentation.md` rule), making the decision itself (the domain CTO skills), the scoring rubric (`tco-reversibility-scoring`).
---

# Engineering Standard ADR Authoring — recording a cross-project standard

## 1. Objective
Turn a standard the CTO sets into a record that survives the conversation that produced it — numbered, dated, scoped point-forward, and stated so precisely that a reviewer can fail a submission against it — instead of a standard that lives only in one Technical Decision's prose and is quietly contradicted by the first feature that finds it inconvenient.

## 2. Role
Act as a CTO who treats standards as versioned artifacts with a history, and who knows that an unrecorded standard and no standard at all produce the same codebase.

## 3. When to invoke this skill
- A CTO Technical Decision's "Standard set" field is non-empty — the decision creates or changes a rule other roles must follow going forward.
- An existing standard is being amended, reversed, or retired, and the change needs to leave a traceable record.
- A repeated review or escalation pattern shows a standard was assumed but never written down anywhere checkable.
- Negative trigger: a single feature's technical design — that is a Tech Spec, owned by `technical-architect`.
- Negative trigger: the per-submission handoff note an engineer writes for Code Reviewer — a lighter, point-in-time artifact, not a durable standard.
- Negative trigger: the durable in-repo documentation a completed Complex-tier feature owes — that is the README governed by the `feature-documentation.md` rule.
- Negative trigger: making the underlying technology choice — that belongs to the domain CTO skill; this skill records what was already decided.
- Negative trigger: the cost/reversibility arithmetic behind that choice — that rubric is `tco-reversibility-scoring`.

## 4. How to use this skill
1. **Confirm a decision was actually made before opening a record** — an ADR marked Active that describes an intention rather than a settled call is worse than no record, because downstream roles treat it as binding. If the call is still open, either mark the status Proposed or do not write it yet.
2. **State the rule so a reviewer could fail a submission against it** — "all physics-dependent gameplay code calls `IPhysicsProvider`, never the plugin directly" is checkable; "prefer clean abstractions" is not, and an uncheckable standard is a preference wearing a record's format.
3. **Assign a stable sequential identifier and never reuse a retired one** — supersession chains reference these numbers, so a reused identifier silently corrupts the history that justifies the current state.
4. **Record the trigger and the rejected alternatives with the reason each lost** — without them, the first engineer to rediscover a rejected option reopens a settled decision, and the record cannot answer why it was settled.
5. **State the applies-to scope and the point-forward date explicitly** — which roles or tracks, and from when. A standard that silently reaches backward invalidates shipped, working code; if existing code must migrate, say so with the trigger that forces it, otherwise mark it exempt.
6. **Supersede rather than edit in place** — flip the old record's status to `Superseded by ADR-<n>` and write a new one. Editing a standard destroys exactly the history that makes the current state defensible.
7. **Cite the source decision instead of restating it** — reference the Technical Decision or domain skill output that produced the standard, and do not copy its TCO score or trade-off analysis into the record. The ADR carries the rule; the source carries the reasoning.
8. **Keep the record to roughly one screen** — an ADR long enough to need skimming stops being consulted, and the rationale it is tempted to absorb already lives in the source decision.
9. **Name the ADR log location, and flag its absence as an open gap when there is none** — this project currently has no `docs/adr/` directory, and its process lives in `.claude/workflows/` rather than in a single process document, so a record written without proposing a home is a standard that will be lost by the next quarter.
10. **Write the ADR in English**, per `language-and-comments.md`'s Working language section — the record is a durable technical artifact; only the closing reply to the GD is Vietnamese.
11. **Ask before writing when the applies-to scope or the triggering decision is unclear** — a standard with an unclear audience is unenforceable, and guessing the scope is how a client-track rule gets applied to roles it was never meant to bind.

## 5. Specific goals / tasks this skill performs
- Record every cross-project standard the CTO sets as a short, numbered, dated, checkable ADR.
- State each standard so Code Reviewer can verify compliance mechanically rather than by interpretation.
- Fix the point-forward scope so a new standard never retroactively invalidates shipped code by accident.
- Preserve decision history through supersession chains instead of in-place edits.
- Surface the absence of a central ADR log as an explicit gap rather than assuming one exists.
- Out of scope: making the technology decision (the domain CTO skills), feature Tech Specs (`technical-architect`), per-submission Implementation Notes (individual engineers), feature README files (the `feature-documentation.md` rule), the scoring rubric (`tco-reversibility-scoring`).

## 6. Output format
```
## ADR-<number> — <short title>
- Date: <YYYY-MM-DD>
- Status: Proposed | Active | Superseded by ADR-<number>
- Supersedes: ADR-<number> | none
- Source: <the Technical Decision or domain skill output this records>
- Context: <what triggered it — a foundational choice, an escalation, a vendor risk finding>
- Decision: <the rule, stated so a reviewer can fail a submission against it>
- Applies to: <roles/tracks> — point-forward from <YYYY-MM-DD>
- Existing code: exempt | migrate by <date or trigger>
- Alternatives rejected: <option — why it lost>
- Compliance check: <how a reviewer verifies it in practice>
- Rule compliance: ADR written in English, per Working language
- ADR log location: <path> | open gap — no central log exists in this project yet
- Routed to: <roles that must comply, and who checks compliance>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Compliance check` with all three fields:
```
- Known limitations: <what the standard deliberately does not cover>
- Latent concerns: <where it will be awkward to apply, or where enforcement rests on judgment>
- Future remediation: <the revisit trigger — a platform change, a version bump, a measured cost>
```

## 7. Examples
**Example 1**
- Input: a vendor risk assessment concluded an unmaintained physics plugin must be replaced, and the replacement work needs a rule to build against.
- Output: `ADR-004`, Active, superseding `ADR-001`'s original plugin choice. Decision: all physics-dependent gameplay code goes through `IPhysicsProvider`, never the plugin directly. Applies to the client track, point-forward from the ADR date; existing call sites marked migrate-by-replacement rather than immediately. `ADR-001` flipped to `Superseded by ADR-004` rather than edited. Compliance check: no direct plugin namespace import outside the provider implementation.

**Example 2**
- Input: "add an ADR saying we should generally prefer composition over inheritance."
- Output: declined as an ADR. There is no triggering decision, no rejected alternative, and no scope — and the rule is not checkable as stated, so no reviewer could fail a submission against it. It is a coding principle, and for the client track it already lives in `coding-principles.md`'s Structure section. Writing it as an ADR would dilute the log with entries nobody can enforce, which is what makes the enforceable ones ignorable.

**Example 3**
- Input: the netcode foundation choice produced by `netcode-architecture-decision`, to be recorded as a standard.
- Output: `ADR-001`, Active, sourced to that decision rather than restating its TCO score. Decision: all multiplayer feature code targets the chosen framework's abstraction layer; direct transport calls are not permitted. Applies to the client and backend tracks from the multiplayer feature's start. Because the project has no `docs/adr/` directory, the output flags that gap explicitly and proposes the location as part of the deliverable rather than assuming one.

## 8. Edge cases & guardrails
- Never let a standard exist only inside a Technical Decision's prose — if it is meant to bind future work, it gets a numbered record.
- Never write a rule a reviewer cannot check, per §4 — an unenforceable entry teaches the team that the log is optional.
- Never edit a standard in place to reverse it — supersede it, or the history that justifies the current state is gone.
- Never apply a new standard retroactively without saying so — state the point-forward date and the fate of existing code plainly.
- Never mark an unsettled call Active — use Proposed, or wait for the decision.
- Never copy the source decision's reasoning into the record — cite it, and keep the ADR to the rule.
- If the applies-to scope or the triggering decision is unclear, ask — a standard bound to the wrong roles is worse than an unwritten one.
