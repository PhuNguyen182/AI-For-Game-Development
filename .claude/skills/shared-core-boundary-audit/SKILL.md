---
name: shared-core-boundary-audit
description: "Core vs Client audit: UnityEngine leaks, Random/Time/DateTime, rules in MonoBehaviours. Use when reviewing boundaries."
user-invocable: false
---

# Shared Core Boundary Audit

- **Not for:** authoring the rule (`csharp-engineer`).
- **Not for:** asserting it in tests (`unity-test-framework`).
- **Not for:** a standing compile-time diagnostic for a recurring violation (`roslyn-analyzer-codefix`).
- **Not for:** secrets (`secret-and-supply-chain-scan`).
- **Not for:** performance (`unity-profiler-diagnostics`).
- **Rules:** `csharp.md` Boundaries.
  - **Also:** `csharp-standards` → `coding-principles.md` Shared Core integrity, `naming-convention.md` Folders.

## Steps
1. **Classify each changed file's layer by its asmdef, not namespace or folder:** Core = an assembly with `noEngineReferences: true` (`<Feature>/Core`, `<Feature>/DataModels`).
   - **Already a finding:** a Core-layer asmdef with the flag off, or referencing a `UnityEngine` module or a feature root.
2. **Grep Core for `UnityEngine` leaks:** `using UnityEngine`, `MonoBehaviour`, `ScriptableObject`, `GameObject`, `Transform`, `Vector3`.
   - **A Core class using a `UnityEngine` type:** belongs in the feature root (`DataControllers/` or `Views/`); report file and type.
3. **Grep Core for non-determinism the compiler cannot catch:** the sources below.
   - **Random:** `UnityEngine.Random`, `Random.Range`, `new System.Random()` without a seed.
   - **Time:** `Time.time`, `Time.deltaTime`, `Time.realtimeSinceStartup`, `DateTime.Now`, `DateTime.UtcNow`, `Stopwatch`, `Environment.TickCount`.
   - **Identity:** `Guid.NewGuid`.
   - **Random, Time and Identity hits:** each must arrive via an injected seed or clock.
   - **Collection order:** `Dictionary`/`HashSet` iteration order that decides an outcome or is serialized.
   - **Hash codes:** `string.GetHashCode()` persisted, sent or used as a seed (Mono and .NET differ).
   - **Float agreement:** `float`/`double` results client and server must agree on → question for `technical-architect` (fixed-point or tolerance).
   - **Priority:** highest-value step; none fail a build, all break client/server agreement.
4. **Find rules restated in the Client:** MonoBehaviour arithmetic that decides an outcome (health subtraction, threshold compare, cost accumulation, state advance).
   - **Core has the decision:** the MonoBehaviour must call it.
   - **Only the MonoBehaviour has it:** the rule is in the wrong layer.
   - **Diff cannot show whether Core has it:** read the Core module; do not assume.
5. **Check dependency direction in the asmdef references:** Client may depend on Core; Core never on Client or Server; features one-way, never a cycle.
6. **Report reach-through chains (`a.GetB().GetC().Value`, Law of Demeter):** with the single method the owner should expose.
7. **Open every hit and cite `path:line`:** a match in a comment, string or editor-only assembly is not a violation; dismiss it by name.
   - **`#if UNITY_EDITOR` `UnityEngine` symbol in a Core assembly:** still an asmdef question for `technical-architect`, not a determinism finding.
8. **Ambiguous placement: report a question:** routed to `technical-architect`; the Tech Spec decides where a decision lives.
9. **Same mechanically decidable violation across submissions: say so:** that is `roslyn-analyzer-codefix`'s entry condition.

## Never
- **Rewriting code:** this skill reports and routes; it never rewrites code.
- **Approving wall-clock or unseeded randomness in Core:** because "it is only used on the client today" — the server runs the same code later.
- **Accepting "the rule is two lines, leave it in the MonoBehaviour":** size is not the criterion; small rules are the ones quietly restated.
- **Widening the audit:** into design intent, security or performance — note it, name the owner.

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

## Example
- **Crit-hit diff:** `DamageCalculator` rolls `UnityEngine.Random.value` and `PlayerAttack` recomputes `damage * critMultiplier`.
  - **Result:** VIOLATIONS FOUND on both, `path:line` cited, routed to `csharp-engineer`.
