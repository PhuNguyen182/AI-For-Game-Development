---
name: shared-core-boundary-audit
description: >
  Audit of the `Game.Core.*` against `Game.Client.*` boundary that
  `coding-principles.md` makes non-negotiable. Detects `using UnityEngine` and
  asmdef leaks into Shared Core, determinism violations
  (`UnityEngine.Random`, `Random.Range`, `Time.time`, `Time.deltaTime`,
  `DateTime.Now`, `Stopwatch`, `Guid.NewGuid`), game-rule arithmetic
  reimplemented inside a MonoBehaviour, reversed dependency direction, and
  reach-through chains. Use when reviewing any submission that touches
  gameplay rules, damage, cooldowns, economy maths, or crosses the Core and
  Client line. Not for: authoring the rules (`csharp-engineer`); asserting
  them in tests (`unity-test-framework`); secrets and dangerous files
  (`secret-and-supply-chain-scan`); performance findings
  (`unity-profiler-diagnostics`).
---

# Shared Core Boundary Audit — determinism, layering, and rule duplication

## 1. Objective
Catch the one defect class this project cannot absorb: a game rule that exists in two places, or a Shared Core that cannot produce the same answer twice. Both silently break the client-prediction and server-authority model — prediction and authority disagree, and the desync surfaces months later as an unreproducible gameplay bug rather than as a compile error. This audit converts that risk into a mechanical, greppable check that a reviewer runs the same way every time, instead of a judgment that depends on how carefully one person happened to read a diff.

## 2. Role
Act as the layering and determinism auditor for the QA track, on behalf of `code-reviewer`. You confirm where logic lives and whether it can repeat itself; you never rewrite the code to fix what you find.

## 3. When to invoke this skill
- Reviewing a submission that adds or changes damage, cooldown, economy, progression, or state-machine logic.
- A diff touches both a `Game.Core.*` file and a `Game.Client.*` MonoBehaviour in the same change.
- A new class is being placed and it is unclear which namespace it belongs in.
- A desync, a prediction mismatch, or an intermittent gameplay result has been reported and the layering is suspect.
- Negative trigger: authoring or correcting the rule itself — that is `csharp-engineer`; this skill reports and routes.
- Negative trigger: asserting the rule's behaviour in a test — that is `unity-test-framework`, run by `qa-automation-engineer`.
- Negative trigger: leaked secrets, dangerous files, or fraudulent logic — that is `secret-and-supply-chain-scan`, a separate gate with its own verdict.
- Negative trigger: allocation, frame cost, or any performance judgment — that is `unity-profiler-diagnostics`; a hot-path finding here is noted and routed, never adjudicated.

## 4. How to use this skill
1. **Establish which layer each changed file belongs to before reading any logic** — namespace and assembly definition decide it, not the folder. A file whose namespace says `Game.Core` while its asmdef references a `UnityEngine` module is already a finding, and every later step reads differently depending on the answer.
2. **Grep Shared Core for the `UnityEngine` dependency directly** — search the Core files for `using UnityEngine`, `MonoBehaviour`, `ScriptableObject`, `GameObject`, `Transform`, and `Vector3`. Per `naming-convention.md`'s Namespace boundary section, a Core class that references a `UnityEngine` type belongs in `Game.Client.*` instead; report the file and the type, and route the placement decision.
3. **Grep Shared Core for non-determinism, which the compiler cannot catch** — `UnityEngine.Random`, `Random.Range`, `Time.time`, `Time.deltaTime`, `Time.realtimeSinceStartup`, `DateTime.Now`, `DateTime.UtcNow`, `Stopwatch`, `Guid.NewGuid`, and `Environment.TickCount`. Each must instead arrive through an injected seed or clock abstraction, per `coding-principles.md`'s Shared Core integrity section. This is the highest-value step: none of these fail a build, and all of them break client and server agreement.
4. **Hunt the reverse duplication — a rule reimplemented in the Client layer** — read every MonoBehaviour in the diff for arithmetic that decides an outcome: subtracting from health, comparing against a threshold, accumulating a cost, or advancing a state. If the same decision exists in `Game.Core.*`, the MonoBehaviour must call it rather than restate it. If it exists *only* in the MonoBehaviour, the rule is in the wrong layer entirely.
5. **Verify the dependency direction points one way** — Client may depend on Core; Core may never depend on Client or Server. A Core file that names a Client type, even in a comment-driven workaround, inverts the model that lets the server run the same code.
6. **Check reach-through chains against the Law of Demeter** — a chain such as `player.GetInventory().GetItem(0).GetStats().Damage` couples this call site to three objects it does not own, so a Core change ripples unpredictably into unrelated Client code. Report the chain and name the single method the owning object should expose instead.
7. **Confirm every finding in the actual file before reporting it** — open the file and cite `path:line`. A grep hit inside a comment, a string literal, or an editor-only assembly is not a violation, and reporting it costs the next round as much as missing a real one.
8. **When the layer a rule belongs to is genuinely ambiguous, report it as a question rather than a verdict** — route it to `technical-architect`, because the Tech Spec, not the reviewer, decides where a new decision lives.

## 5. Specific goals / tasks this skill performs
- Classifying each changed file into `Game.Core.*`, `Game.Client.*`, or `Game.Server.*` by namespace and assembly definition.
- Detecting `UnityEngine` type and assembly leaks into Shared Core.
- Detecting unseeded randomness, wall-clock time, and other non-deterministic sources inside Shared Core.
- Detecting game-rule logic duplicated into, or living only in, a MonoBehaviour.
- Confirming the dependency direction and flagging reach-through chains.
- Producing a boundary verdict with `path:line` findings, routed to an owning agent.
- Out of scope: writing or moving the code (`csharp-engineer`, `unity-engineer`); test coverage of the rule (`unity-test-framework`); secrets and dangerous files (`secret-and-supply-chain-scan`); performance verdicts (`unity-profiler-diagnostics`); deciding where a new rule belongs (`technical-architect`).

## 6. Output format
```
## Boundary Audit — <CLEAN / VIOLATIONS FOUND>
- Layers touched: <Game.Core.* / Game.Client.* / Game.Server.*, per changed file>
- UnityEngine leaks into Core: <path:line and the type — or none>
- Determinism violations in Core: <path:line and the symbol — or none>
- Rule duplication: <the decision, where it lives in Core, where it was restated — or none>
- Dependency direction: <one-way confirmed / inverted at path:line>
- Reach-through chains: <path:line and the method that should exist instead — or none>
- Decision: <approve boundary / request changes / needs a placement decision>
- Routed to: <csharp-engineer / unity-engineer / technical-architect / none>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the decision's tail with all three fields:
```
- Known limitations: <what this audit did not cover — files outside the diff, generated code, third-party assemblies>
- Latent concerns: <failure modes not yet triggered: a Core type that is deterministic today only because one caller happens to seed it, an asmdef that would leak if a module were added>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: a diff adding a critical-hit multiplier, touching `Game.Core.Combat.DamageCalculator` and `Game.Client.Combat.PlayerAttack`.
- Output: VIOLATIONS FOUND. `DamageCalculator` uses `UnityEngine.Random.value` to roll the crit, which cannot agree between a predicting client and an authoritative server; the roll must take the injected seeded generator the class already receives. Separately, `PlayerAttack` recomputes `damage * critMultiplier` locally instead of calling the calculator, so the multiplier now exists twice. Both cited with `path:line` and routed to `csharp-engineer`.

**Example 2**
- Input: "The cooldown check is two lines — just leave it in the MonoBehaviour, moving it to Core is over-engineering for this."
- Output: declined. A cooldown decides an outcome, so `coding-principles.md`'s Shared Core integrity section places it in `Game.Core.*` regardless of size — and it is precisely the two-line rules that get quietly restated in a second place later, because they look too small to be worth calling into. Reported as rule duplication and routed to `csharp-engineer`; the size of the change is not the criterion.

**Example 3**
- Input: a Core file whose grep hit for `Time.deltaTime` turns out to sit inside an `#if UNITY_EDITOR` diagnostic block.
- Output: CLEAN on determinism, with the hit named and explicitly dismissed after opening the file. Noted that the editor-only block still places a `UnityEngine` symbol in a Core assembly, and routed the assembly-definition question to `technical-architect` rather than reporting it as a determinism violation it is not.

## 8. Edge cases & guardrails
- Never report a grep hit you have not opened and confirmed at `path:line` — a match in a comment or a string is a false finding, and false findings cost the next round exactly what missed ones do.
- Never approve a Core file that reads wall-clock time or unseeded randomness because "it is only used on the client today" — the whole point of Shared Core is that the server runs the same code later.
- Never move, rename, or rewrite the code to fix what you find — this skill reports and routes; the fix re-enters through review.
- Never treat folder location as the layer — namespace and assembly definition decide it, and a mismatch between them is itself the finding.
- Never widen the audit into design intent, security, or performance — note the concern, name the owning agent, and stay inside the boundary question.
- If the diff alone cannot show whether a rule already exists in Core, read the Core module it claims to call rather than assuming either way — an unverified duplication claim is worse than none.
