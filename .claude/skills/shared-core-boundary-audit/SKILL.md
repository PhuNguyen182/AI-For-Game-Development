---
name: shared-core-boundary-audit
description: "Audit Game.Core vs Game.Client: UnityEngine/asmdef leaks into Core, determinism violations (Random, Time, DateTime), rules reimplemented in MonoBehaviours, reversed dependencies. Use when reviewing rule or boundary changes."
user-invocable: false
---

# Shared Core Boundary Audit

Not for: authoring the rule (`csharp-engineer`), asserting it in tests (`unity-test-framework`), a standing compile-time diagnostic for a recurring violation (`roslyn-analyzer-codefix`), secrets (`secret-and-supply-chain-scan`), performance (`unity-profiler-diagnostics`). This skill reports and routes; it never rewrites code.
Rules: `csharp.md` Boundaries; `csharp-standards` → `coding-principles.md` Shared Core integrity, `naming-convention.md` Namespace boundary.

## Steps
1. **Classify each changed file's layer by namespace and asmdef, not folder** — a `Game.Core` namespace whose asmdef references a `UnityEngine` module is already a finding.
2. **Grep Core for `UnityEngine` leaks** — `using UnityEngine`, `MonoBehaviour`, `ScriptableObject`, `GameObject`, `Transform`, `Vector3`. A Core class using a `UnityEngine` type belongs in `Game.Client.*`; report file and type.
3. **Grep Core for non-determinism the compiler cannot catch** — `UnityEngine.Random`, `Random.Range`, `Time.time`, `Time.deltaTime`, `Time.realtimeSinceStartup`, `DateTime.Now`, `DateTime.UtcNow`, `Stopwatch`, `Guid.NewGuid`, `Environment.TickCount`. Each must arrive via an injected seed or clock. Highest-value step: none fail a build, all break client/server agreement.
4. **Find rules restated in the Client** — MonoBehaviour arithmetic that decides an outcome (health subtraction, threshold compare, cost accumulation, state advance). If Core has the decision, the MonoBehaviour must call it; if only the MonoBehaviour has it, the rule is in the wrong layer. If the diff cannot show whether Core has it, read the Core module; do not assume.
5. **Check dependency direction** — Client may depend on Core; Core never on Client or Server.
6. **Report reach-through chains** (`a.GetB().GetC().Value`, Law of Demeter) with the single method the owner should expose.
7. **Open every hit and cite `path:line`** — a match in a comment, string or editor-only assembly is not a violation; dismiss it by name. An `#if UNITY_EDITOR` `UnityEngine` symbol in a Core assembly is still an asmdef question for `technical-architect`, not a determinism finding.
8. **Ambiguous placement: report a question** routed to `technical-architect`; the Tech Spec decides where a decision lives.
9. **Same mechanically decidable violation across submissions: say so** — that is `roslyn-analyzer-codefix`'s entry condition.

## Never
- Approve Core that reads wall-clock time or unseeded randomness because "it is only used on the client today" — the server runs the same code later.
- Accept "the rule is two lines, leave it in the MonoBehaviour" — size is not the criterion; small rules are the ones quietly restated.
- Widen into design intent, security or performance — note it, name the owner.

## Output
```
## Boundary Audit — CLEAN | VIOLATIONS FOUND
- Layers touched: <per changed file>
- UnityEngine leaks into Core: <path:line, type | none>
- Determinism violations in Core: <path:line, symbol | none>
- Rule duplication: <decision, Core location, restated location | none>
- Dependency direction: one-way | inverted at <path:line>
- Reach-through chains: <path:line, method that should exist | none>
- Decision: approve | request changes | needs placement decision
- Routed to: <csharp-engineer | gameplay-engineer | technical-architect | none>
```
On request only, add `Known limitations`, `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- Crit-hit diff: `DamageCalculator` rolls `UnityEngine.Random.value` and `PlayerAttack` recomputes `damage * critMultiplier` → VIOLATIONS FOUND on both, `path:line` cited, routed to `csharp-engineer`.
