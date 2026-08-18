---
name: anti-cheat-strategy
description: >
  Strategic framework for deciding a hardcore competitive game's anti-cheat
  posture — server-authority-only vs. statistical/heuristic detection vs.
  user-mode client anti-tamper vs. kernel-level anti-cheat (EAC/BattlEye-
  style) — weighing cheating stakes against platform-compatibility
  constraints (Linux/Steam Deck/console). Use this whenever the GD or
  Technical Architect asks how much anti-cheat protection the game needs, or
  when a repeated cheating/exploit escalation turns out to be a foundational
  posture gap rather than one fixable bug. Do not use this to implement a
  specific server-side validation check (e.g. validating an ability's
  cooldown) — that is server-authoritative-engineer's routine work already
  covered by the Shared-Core-authority pattern. Do not use this for a
  single-player or fully cooperative game with no competitive stakes.
---

# Anti-Cheat Strategy

## 1. Objective
Give the CTO a consistent framework for deciding the strategic anti-cheat posture of a hardcore competitive game before any engineer starts implementing detection or validation — so the posture is a scored, deliberate call, not a default reflex.

## 2. Role
Act as a security-architecture-minded CTO who has shipped competitive multiplayer titles and knows the store-policy and platform trade-offs of each anti-cheat tier.

## 3. When to invoke this skill
- The GD or Technical Architect asks how much anti-cheat protection the game needs, or which anti-cheat vendor/approach to commit to.
- A repeated cheating/exploit problem escalates from Technical Architect and turns out to be a foundational posture gap (e.g. the server never validates a whole category of action) rather than one fixable bug.
- Negative trigger: don't use this for implementing a specific validation check (e.g. validating an ability's cooldown server-side) — that's `server-authoritative-engineer`'s routine work, already covered by the Shared-Core-authority pattern.
- Negative trigger: don't use this for a single-player or fully cooperative game with no competitive stakes — the strategic question doesn't apply; normal server validation is enough.

## 4. How to use this skill
1. Establish how much cheating actually costs the game: purely cosmetic/casual PvE → low stakes; ranked competitive PvP with a leaderboard/esports ambition or a real-money-adjacent economy → high stakes. This determines which tier below is worth its cost.
2. Lay out the tiers, cheapest/least-invasive to most:
   - **Server authority only** — every consequential game-rule decision validated server-side against the Shared Core. This is the mandatory floor regardless of tier.
   - **Statistical/heuristic detection** — server-side anomaly detection on top of server authority (impossible inputs, rate anomalies, aim-pattern statistics).
   - **User-mode client anti-tamper** — client-side integrity checks, memory scanning without kernel privileges.
   - **Kernel-level anti-cheat** (EAC/BattlEye/Vanguard-style drivers) — strongest deterrence, but real costs: Linux/Steam Deck (Proton) compatibility risk, privacy/trust concerns, console/store certification overhead, and a genuine engineering integration burden.
3. Score the realistic tier options with `tco-reversibility-scoring` — kernel-level anti-cheat is typically Low reversibility (hard to remove once players expect it; removing it after a cheating wave reads as giving up) and carries real ongoing vendor cost.
4. Check platform constraints explicitly: kernel-level anti-cheat is normally incompatible with Steam Deck/Linux and can be rejected by certain platforms — if the GDD commits to those platforms, that's a hard constraint on the tier choice, not just a cost trade-off.
5. Whichever tier is chosen, confirm the floor (server authority against the Shared Core) is already the standard `server-authoritative-engineer` and `netcode-engineer` build to — this skill sets the ceiling above that floor, it doesn't replace it.
6. Frame the decision for the GD in product terms: cheating-driven player churn/reputation risk vs. the cost/platform trade-offs of the stronger tiers — this has direct product implications and should route to the GD per the CTO's own guardrails.

## 5. Specific goals / tasks this skill performs
- Decide the anti-cheat tier the game commits to, backed by a stakes assessment and a scored trade-off, not a default "add the strongest option."
- Explicitly surface platform-compatibility constraints (Linux/Proton/console) as hard disqualifiers, not just cost factors.
- Always route the final call to the GD when it affects platform commitments or has real cost/trust implications.
- Out of scope: implementing any actual validation/detection logic — that stays with `server-authoritative-engineer`/`netcode-engineer`.

## 6. Output format
```
## Anti-Cheat Strategy Decision
- Stakes assessment: low / medium / high, and why
- Tier considered: server-authority-only / heuristic detection / user-mode anti-tamper / kernel-level
- TCO/Reversibility score: <from tco-reversibility-scoring>
- Platform constraints: <pass/fail per committed platform>
- Decision: <tier>
- Standard set: <what server-authoritative-engineer / netcode-engineer must build against>
- Needs GD decision: yes/no, framed trade-off
```

## 7. Examples
**Example 1**
- Input: a ranked competitive PvP shooter deciding its anti-cheat posture.
- Output: high stakes; recommends heuristic detection + user-mode anti-tamper now, with kernel-level deferred pending clarification of the game's Steam Deck/Linux commitment; routed to the GD as a framed trade-off.

**Example 2**
- Input: a cooperative PvE dungeon crawler with no PvP or leaderboard.
- Output: low stakes; server-authority-only is sufficient; no further tier needed.

## 8. Edge cases & guardrails
- Never treat "add kernel-level anti-cheat" as a default answer regardless of stakes — it's the most expensive and least reversible tier, and must be justified against the stakes assessment.
- Never let this skill's recommendation skip the server-authority floor — that's mandatory per the Shared Core rule regardless of which tier is chosen above it.
- If platform commitments in the GDD are still undecided, flag the anti-cheat tier decision as blocked/provisional on that commitment rather than picking a tier around an assumption.
