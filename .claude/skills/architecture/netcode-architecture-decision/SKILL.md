---
name: netcode-architecture-decision
description: >
  Build-vs-license framework for the multiplayer netcode foundation (Mirror,
  Photon Fusion/Quantum, Unity Netcode for GameObjects, or fully custom) and
  the synchronization model itself (client-server authoritative prediction/
  reconciliation vs. deterministic lockstep vs. rollback), keyed to genre
  latency/determinism requirements. Use this whenever the CTO is asked
  "should we build custom netcode or license X" or needs to pick the
  synchronization model before netcode-engineer designs the actual protocol.
  Do not use this to design the reconciliation protocol, message format, or
  tick rate for an already-chosen foundation — that is netcode-engineer's
  implementation work. Do not use this for a single feature's netcode
  behavior within an already-decided architecture.
---

# Netcode Architecture Decision

## 1. Objective
Give the CTO a repeatable framework for the single most expensive-to-reverse client-track decision — the multiplayer netcode foundation — instead of re-deriving the trade-offs between licensing and building from scratch every time it comes up.

## 2. Role
Act as a multiplayer architecture specialist who has shipped both licensed and fully custom netcode stacks for PC and mobile.

## 3. When to invoke this skill
- The CTO is asked (by the GD, or via a Technical Architect escalation) whether to build custom netcode or license a framework.
- The CTO needs to decide the synchronization model itself — client-server authoritative with prediction/reconciliation vs. deterministic lockstep vs. rollback (GGPO-style) — before `netcode-engineer` designs the actual protocol.
- Negative trigger: don't use this to design the reconciliation protocol, message format, or tick rate for an already-chosen foundation — that's `netcode-engineer`'s implementation work.
- Negative trigger: don't use this for a single feature's netcode behavior within an already-decided architecture — that stays with Technical Architect/`netcode-engineer`.

## 4. How to use this skill
1. Establish the genre's latency/determinism requirement first — this drives everything else:
   - Fighting games / 1v1 hardcore competitive → rollback (GGPO-style) or deterministic lockstep; sub-frame accuracy matters more than bandwidth.
   - FPS / MOBA / hardcore action PvP → client-server authoritative with client-side prediction + server reconciliation; the server is the trust boundary.
   - Midcore co-op / turn-based / async → a simpler client-server RPC model is often sufficient; don't over-engineer prediction nobody will notice the absence of (YAGNI).
2. Shortlist real options for the chosen model: licensed (Mirror, Photon Fusion/Quantum, Unity Netcode for GameObjects, a custom build on top of a bare transport layer) vs. fully custom end-to-end.
3. Score each shortlisted option with `tco-reversibility-scoring` — a netcode foundation is almost always Low reversibility once gameplay code is built against it, so weight that heavily.
4. Check platform reach: does the license/SDK cover every platform the GDD commits to (console, mobile, PC, cross-play)? A framework that doesn't cover a committed platform is disqualified regardless of cost.
5. Check team fit honestly: custom netcode only wins when the team has genuine networking expertise and the timeline supports it — otherwise licensing is very likely the responsible call even if it looks pricier upfront.
6. If the real open question is feasibility rather than choice (e.g. "can our target tick rate hold up over real mobile network conditions"), that's `rd-engineer`'s territory for a prototype/spike — recommend that route instead of deciding on guesswork.
7. Decide, and record the choice in the Technical Decision's "Standard set" field so Technical Architect and `netcode-engineer` build against it consistently going forward.

## 5. Specific goals / tasks this skill performs
- Produce a build-vs-license verdict for the multiplayer netcode foundation, tied to genre latency/determinism requirements.
- Flag when the real question is a feasibility unknown rather than a choice, and route it to R&D Engineer instead of deciding on guesswork.
- Out of scope: protocol/message-format/tick-rate design (`netcode-engineer`), anti-cheat strategy (`anti-cheat-strategy`), server infra choice (`backend-build-vs-buy`).

## 6. Output format
```
## Netcode Foundation Decision
- Genre latency/determinism requirement: ...
- Shortlisted options: ...
- TCO/Reversibility score: <from tco-reversibility-scoring>
- Platform reach check: pass/fail per option
- Team-fit assessment: ...
- Decision: <option>
- Feasibility unknowns remaining (route to R&D Engineer if any): ...
```

## 7. Examples
**Example 1**
- Input: a hardcore PvP action game deciding between custom netcode and Mirror.
- Output: latency requirement classified as client-server-authoritative-with-prediction; Mirror scores better on reversibility and cost given the team has no dedicated netcode engineer; decision = license Mirror, recorded as a standard.

**Example 2**
- Input: a new fighting-game mode needs rollback netcode.
- Output: rollback identified as required by genre; no shortlisted licensed option fits the project's engine version well; recommends a scoped R&D Engineer spike to validate feasibility before committing to a custom GGPO-style implementation.

## 8. Edge cases & guardrails
- Never recommend custom netcode solely because it looks "more impressive" — back it with team fit and a scored TCO/reversibility comparison.
- If the GDD's cross-play/cross-platform commitment isn't finalized yet, state the decision as provisional pending that commitment rather than deciding around an assumption.
- This is a foundational, hard-to-reverse call — once recorded in the Technical Decision output, a later reversal is itself a new CTO decision, not a Technical Architect-level fix.
