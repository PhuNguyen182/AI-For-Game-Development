---
name: engineering-standard-adr-authoring
description: >
  Lightweight Architecture Decision Record (ADR) format for recording a
  cross-project engineering standard the CTO sets, so it's a durable,
  versioned, checkable artifact Technical Architect and Tech Leads can track
  compliance against — instead of a standard that only lives in one
  Technical Decision's prose and gets forgotten. Use this whenever a CTO
  Technical Decision's "Standard set" field is non-empty. Do not use this
  for a routine, single-feature Tech Spec — that's Technical Architect's
  format. Do not use this for a one-off Implementation Note handoff between
  an Engineer and Code Reviewer — that's a different, lighter-weight
  artifact.
---

# Engineering Standard ADR Authoring

## 1. Objective
Give the CTO a consistent, lightweight format for recording a cross-project engineering standard as an Architecture Decision Record, so Technical Architect and Tech Leads have something durable to check compliance against.

## 2. Role
Act as a CTO who treats standards as living, versioned artifacts, not one-off pronouncements.

## 3. When to invoke this skill
- Whenever a CTO Technical Decision's "Standard set" field is non-empty — i.e. the decision creates or changes a standard Architect/Tech Leads must follow going forward.
- Negative trigger: don't use this for a routine, single-feature Tech Spec — that's Technical Architect's format, not a cross-project standard.
- Negative trigger: don't use this for a one-off Implementation Note handoff between an Engineer and Code Reviewer — that's a different, lighter-weight artifact.

## 4. How to use this skill
1. State the standard as a short, unambiguous rule — something Code Reviewer could actually check a submission against, not a vague principle.
2. Record the decision context briefly: what triggered it (a Technical Decision, a 3-strikes escalation, a vendor risk finding), and what alternative(s) were rejected and why — future readers need to know a standard was a deliberate choice, not an accident.
3. State who the standard applies to (which roles/tracks) and from what point forward — a new standard should not retroactively invalidate already-shipped, working code unless explicitly stated.
4. Give the standard a stable identifier (e.g. a sequential ADR number) so it can be referenced later (superseded, amended) without ambiguity.
5. If a later decision changes or reverses an earlier standard, mark the old one as superseded rather than silently contradicting it — the record should show the history, not just the current state.
6. Since no `TEAM_STRUCTURE.md` or equivalent authoritative process document currently exists in this project, recommend that ADRs be kept together in one place (e.g. a `docs/adr/` log) so they collectively become that reference over time — flag this gap explicitly rather than assuming the standard will be remembered informally.

## 5. Specific goals / tasks this skill performs
- Every cross-project engineering standard the CTO sets gets recorded as a short, checkable, dated, uniquely-identified ADR.
- Superseded standards are marked as such, not silently overwritten.
- Out of scope: writing feature-level Tech Specs (Technical Architect) or routine Implementation Notes (individual Engineers).

## 6. Output format
```
## ADR-<number> — <short title>
- Date: ...
- Status: Active / Superseded by ADR-<n>
- Context: <what triggered this standard>
- Decision: <the rule, stated so it's checkable>
- Applies to: <roles/tracks, and from what point forward>
- Alternatives rejected: <brief>
```

## 7. Examples
**Example 1**
- Input: replacing an unmaintained physics plugin after a vendor risk assessment.
- Output: `ADR-004` — "All physics-dependent gameplay code must go through the abstracted `IPhysicsProvider` interface, not call the underlying plugin directly" — marked as superseding `ADR-001`'s original plugin choice.

**Example 2**
- Input: the netcode foundation choice (Mirror vs. custom).
- Output: `ADR-001` recording the decision, applying to all client/backend tracks from the multiplayer feature's start.

## 8. Edge cases & guardrails
- Never let a standard exist only inside a single Technical Decision's prose — if it's meant to persist, it gets an ADR entry per this format.
- Don't retroactively apply a new standard to already-shipped code without saying so explicitly — state the point-forward scope plainly.
- If this project still has no central ADR log location, say so as an open gap in the output rather than silently assuming one exists.
