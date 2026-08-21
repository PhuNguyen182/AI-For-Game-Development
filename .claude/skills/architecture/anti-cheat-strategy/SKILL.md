---
name: anti-cheat-strategy
description: >
  Strategic framework for choosing a competitive game's anti-cheat posture
  across four tiers — server authority against the Shared Core, server-side
  statistical/heuristic detection, user-mode client anti-tamper, and
  kernel-level drivers (Easy Anti-Cheat, BattlEye, Vanguard) — weighing
  cheating stakes against Steam Deck/Proton compatibility, console
  certification, and player-trust cost. Use when asked how much anti-cheat the
  game needs, or when a repeated exploit escalation turns out to be a posture
  gap rather than one bug.
  Not for: writing a specific server-side validation check (`server-authoritative-engineer`), sync model choice (`netcode-architecture-decision`), the scoring rubric (`tco-reversibility-scoring`), platform-expansion cost (`cross-platform-expansion-assessment`).
---

# Anti-Cheat Strategy — posture tier for a competitive game

## 1. Objective
Decide how much anti-cheat a game actually needs, so the posture is a scored call against real stakes and real platform constraints — not the reflex of buying the strongest available tier, and not the opposite failure of assuming server authority alone closes cheat classes it structurally cannot touch.

## 2. Role
Act as a security-minded CTO who has shipped competitive multiplayer titles and has paid, first-hand, the platform-compatibility and player-trust costs each anti-cheat tier carries.

## 3. When to invoke this skill
- Asked how much anti-cheat protection the game needs, or which vendor/tier to commit to.
- A repeated cheating or exploit escalation arrives from Technical Architect and turns out to be a whole unvalidated category of action rather than one fixable bug.
- A platform commitment (Steam Deck, console, Linux) needs checking against an anti-cheat tier before either is locked in.
- Negative trigger: writing one server-side validation rule, such as checking an ability's cooldown against the Shared Core — that is `server-authoritative-engineer`'s routine work.
- Negative trigger: which synchronization model or netcode foundation the game runs on — that is `netcode-architecture-decision`, decided below this one.
- Negative trigger: the cost/reversibility arithmetic itself — that rubric is `tco-reversibility-scoring`, which this skill calls.
- Negative trigger: the full engineering cost of adding a platform — that is `cross-platform-expansion-assessment`, which consults this decision rather than replacing it.

## 4. How to use this skill
1. **Establish what cheating actually costs this game before any tier is compared** — a cosmetic or casual PvE game, a ranked ladder, an esports ambition, and a real-money-adjacent economy sit at wildly different stakes, and the stakes decide which tier is worth its price.
2. **Confirm server authority against the Shared Core is already the floor, and treat it as a precondition rather than tier one of a menu** — every tier above assumes it. Client anti-tamper layered over a server that never validates outcomes buys a lock for a door with no frame.
3. **Name the cheat classes actually observed or plausible, because the tiers do not all address the same ones** — state manipulation (speedhacks, item duplication) is what server authority stops; input automation (aimbots, macros) needs statistical detection; information cheats (wallhacks, ESP, map hacks) are read-only and completely invisible to server authority.
4. **Fix information cheats in what the server sends, not in what the client runs** — relevancy culling and server-side fog of war stop ESP by never transmitting the data; no anti-cheat tier can un-send it. This is `netcode-engineer` work, and skipping it while buying a kernel driver is the most expensive way to not solve the problem.
5. **Lay out the four tiers with what each actually buys** — server authority (correctness of outcomes), heuristic detection (input automation, at the cost of false positives), user-mode anti-tamper (raises effort for casual cheats, defeated by kernel-level cheats), kernel-level drivers (strongest deterrence, heaviest cost on every other axis).
6. **Treat a committed platform the tier cannot ship on as a disqualifier, not a cost line** — kernel-level anti-cheat is generally incompatible with Steam Deck and Proton, and carries per-console certification overhead. If the GDD commits those platforms, the tier is out before price is discussed.
7. **Price player trust and privacy as a real line item** — a kernel-level driver asks every player to install ring-0 software, which carries genuine reputational and review-bombing exposure independent of whether it works.
8. **Confirm someone owns bans and appeals before committing to any detection tier** — heuristic detection produces false positives, and a false ban with no appeal path is worse for retention than the cheating it prevents. An unowned appeals process makes the tier unshippable, not merely risky.
9. **Score the surviving tiers with `tco-reversibility-scoring`** — kernel-level anti-cheat rates Low reversibility, because removing it after a visible cheating wave reads publicly as surrender regardless of the engineering reason.
10. **Frame the outcome for the GD in product terms whenever it touches a platform commitment, ongoing vendor cost, or player trust** — those are the GD's calls to make, not the CTO's to settle alone.
11. **Record the chosen posture as a durable standard** via `engineering-standard-adr-authoring` — the floor that `server-authoritative-engineer` and `netcode-engineer` build against must outlive the conversation that set it.
12. **Write the decision and its reasoning in English**, per `language-and-comments.md`'s Working language section — only the closing reply to the GD is Vietnamese.
13. **Ask before deciding when the GDD leaves platform commitments, competitive stakes, or economy design open** — mark the tier provisional on the missing input rather than choosing around an assumed one.

## 5. Specific goals / tasks this skill performs
- Decide the anti-cheat tier the game commits to, backed by a named stakes level and a scored trade-off.
- Map each plausible cheat class to the mechanism that actually addresses it, so no tier is bought for a problem it cannot solve.
- Surface platform incompatibility as a hard disqualifier before cost enters the comparison.
- Confirm the server-authority floor is genuinely in place rather than assumed.
- Establish ban/appeal ownership as a shipping precondition for any detection tier.
- Out of scope: implementing validation or detection logic (`server-authoritative-engineer`, `netcode-engineer`), relevancy-culling implementation (`netcode-engineer`), foundation and sync model (`netcode-architecture-decision`), the scoring rubric (`tco-reversibility-scoring`).

## 6. Output format
```
## Anti-Cheat Posture Decision — <game or mode>
- Stakes: low | medium | high — <ranked ladder, esports ambition, tradable economy, or none>
- Cheat classes in scope: state manipulation | input automation | information/ESP | account-economy abuse
- Floor status: server authority against the Shared Core in place | gap: <what is unvalidated>
- Information-cheat handling: relevancy culling / server-side fog of war — in place | gap | not applicable
- Tiers considered: server-authority-only | + heuristic detection | + user-mode anti-tamper | + kernel-level
- Platform compatibility: <pass/fail per committed platform, per tier — a fail disqualifies>
- Trust/privacy cost: <what players are asked to install, and the reputational exposure>
- Ban/appeal ownership: <who runs false-positive appeals> | unowned — tier not shippable
- TCO / Reversibility: <score from tco-reversibility-scoring>
- Rule compliance: decision written in English, per Working language
- Decision: <tier> — <one line tying stakes and constraints to the choice>
- Needs GD decision: yes/no — <framed trade-off>
- Routed to: <role or skill that acts on this next>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Decision` rationale with all three fields:
```
- Known limitations: <cheat classes the chosen tier does not address>
- Latent concerns: <what holds only while stakes, platform list, or population stay as they are>
- Future remediation: <the escalation trigger for each — the cheat prevalence, platform change, or launch milestone>
```

## 7. Examples
**Example 1**
- Input: a ranked PvP shooter with rising ESP/wallhack reports; server authority already validates movement and damage; Steam Deck listed as a committed platform.
- Output: stakes high. The reported class is information cheating, which server authority cannot touch, so the primary fix is relevancy culling routed to `netcode-engineer` — not an anti-cheat purchase. Heuristic detection added for aimbot patterns, with appeals ownership assigned. Kernel-level disqualified outright by the Steam Deck commitment rather than deferred on cost. Recorded via `engineering-standard-adr-authoring`.

**Example 2**
- Input: "just ship Easy Anti-Cheat, every competitive game does — it will stop the wallhacks."
- Output: declined on two counts. A kernel driver does not stop ESP when the server broadcasts full world state to every client; the cheat reads data the game legitimately sent, so the fix is culling what is sent. And the GDD commits Steam Deck, where kernel-level anti-cheat does not ship — making it a disqualified tier, not an expensive one. Recommended culling plus heuristic detection instead, scored via `tco-reversibility-scoring`.

**Example 3**
- Input: a co-op PvE dungeon crawler with no PvP and no leaderboard, but with player-to-player item trading.
- Output: the naive read is low stakes, but tradable items make duplication exploits an economy attack, so stakes are medium, not low. Server authority over item creation and transfer is confirmed as the required floor. Detection and anti-tamper tiers declined as premature (YAGNI); the residual risk and its re-open trigger — the first confirmed dupe in the live economy — are stated explicitly.

## 8. Edge cases & guardrails
- Never treat kernel-level anti-cheat as the default answer — it is the least reversible and most trust-expensive tier, and must be earned against a stated stakes level.
- Never buy a tier for a cheat class it cannot address, per §4 — an anti-tamper purchase against an information cheat spends real money and changes nothing.
- Never let a tier decision substitute for the server-authority floor — that floor is mandatory at every stakes level.
- Never ship a heuristic detection tier with no owner for false-positive appeals — a wrongly banned paying player costs more than the cheater did.
- Never compare tier cost before platform compatibility — an incompatible tier is out, not merely pricey.
- If the GDD's platform commitments or competitive stakes are still open, state the tier as provisional on that input — do not pick a tier around an assumption.
