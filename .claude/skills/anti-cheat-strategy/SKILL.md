---
name: anti-cheat-strategy
description: "Choose a game's anti-cheat posture: server authority, server-side detection, client anti-tamper, kernel drivers (EAC, BattlEye) — stakes vs Steam Deck/console and player trust. Use when sizing anti-cheat or a recurring exploit is a posture gap."
user-invocable: false
---

# Anti-Cheat Strategy

Not for: writing one server-side validation check or relevancy culling (`netcode-engineer`), sync model (`netcode-architecture-decision`), the scoring rubric (`tco-reversibility-scoring`), platform-expansion cost (`cross-platform-expansion-assessment`).

## Steps
1. **Establish what cheating costs this game** — casual PvE, ranked ladder, esports ambition and a real-money-adjacent economy are different stakes; stakes decide which tier is worth its price. Player-to-player item trading makes duplication an economy attack even without PvP, so stakes are at least medium; confirm server authority over item creation and transfer as the floor.
2. **Confirm server authority against the Shared Core is the floor** — a precondition at every stakes level, not tier one of a menu. Client anti-tamper over a server that never validates outcomes is a lock on a door with no frame.
3. **Name the cheat classes observed or plausible** — state manipulation (speedhack, duplication): server authority. Input automation (aimbot, macro): statistical detection. Information cheats (wallhack, ESP, map hack): read-only, invisible to server authority.
4. **Fix information cheats in what the server sends** — relevancy culling and server-side fog of war; no tier can un-send data. Route to `netcode-engineer` before buying anything.
5. **Tiers and what each buys** — server authority: outcome correctness. Heuristic detection: input automation, with false positives. User-mode anti-tamper: raises effort for casual cheats, defeated by kernel-level cheats. Kernel driver: strongest deterrence, heaviest cost on every other axis.
6. **A committed platform the tier cannot ship on disqualifies it before price** — kernel-level is generally incompatible with Steam Deck/Proton and carries per-console certification overhead.
7. **Price player trust** — a ring-0 driver asks every player to install it; reputational and review-bombing exposure exists whether or not it works.
8. **Require an owner for bans and appeals before any detection tier** — a false ban with no appeal path costs more retention than the cheating; unowned means not shippable.
9. **Score survivors with `tco-reversibility-scoring`** — kernel-level is Low reversibility (removal after a cheating wave reads as surrender).
10. **Frame platform, vendor-cost and player-trust consequences for the GD**; record the posture via `engineering-standard-adr-authoring`.
11. **Ask when platform commitments, competitive stakes or economy design are open** — mark the tier provisional on the missing input.

## Never
- Default to kernel-level, or buy a tier for a cheat class it cannot address (anti-tamper against ESP changes nothing).
- Let a tier decision substitute for the server-authority floor.
- Ship a heuristic tier with no false-positive appeal owner.

## Output
```
## Anti-Cheat Posture Decision — <game or mode>
- Stakes: low | medium | high — <ladder, esports, tradable economy, none>
- Cheat classes in scope: state manipulation | input automation | information/ESP | account-economy abuse
- Floor: server authority against Shared Core in place | gap: <unvalidated>
- Information-cheat handling: culling / fog of war — in place | gap | n/a
- Tiers considered: server-authority-only | + heuristic | + user-mode anti-tamper | + kernel-level
- Platform compatibility: <pass/fail per platform per tier — fail disqualifies>
- Trust/privacy cost: <...>
- Ban/appeal owner: <who> | unowned — not shippable
- TCO / Reversibility: <score>
- Decision: <tier> — <stakes and constraints tie>
- Needs GD decision: yes/no — <trade-off>
- Routed to: <...>
```
On request only, add `Known limitations`, `Latent concerns` and `Future remediation`, each with its escalation trigger.

## Example
- "Ship Easy Anti-Cheat, it will stop the wallhacks" → declined: a kernel driver does not stop ESP when the server broadcasts full world state, and Steam Deck is committed so kernel-level is disqualified; culling plus heuristic detection instead.
