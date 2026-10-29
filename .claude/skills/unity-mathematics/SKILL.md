---
name: unity-mathematics
description: "Unity.Mathematics: float3/float4x4, quaternion, swizzles, math functions, noise, struct Random. Use for Game.Core.*, Burst, jobs and ECS math instead of UnityEngine Vector3/Mathf/Random."
user-invocable: false
---

# Unity Mathematics

Not for: an injected `IRandom` roll, weighted table or shuffle outside Burst (`nrandom-random-generation`); job scheduling (`unity-job-system-and-burst`); container choice (`unity-collections`); Burst tuning and `FloatMode` (`unity-burst-compiler`); ECS component design (`unity-ecs-architecture`); physics components (`unity-physics`); material overrides (`unity-entities-graphics`).
Docs: https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/ (`manual/`, `api/`) — pinned 1.3; keep `@1.3` in any link, the package adds features between releases.

| Reference | Read when |
|---|---|
| [vector-and-matrix-types.md](references/vector-and-matrix-types.md) | Choosing a vector width, rotation type or matrix, or building a quaternion/matrix |
| [math-functions-and-swizzling.md](references/math-functions-and-swizzling.md) | Replacing a `Mathf`/`System.Math` call, rearranging components, or picking a `noise` function |
| [random-numbers.md](references/random-numbers.md) | Any RNG inside `Game.Core.*` or a parallel context |

## Steps
1. **Establish the layer first.** `Game.Core.*` must use these types: no `UnityEngine` dependency (`csharp-standards` → `coding-principles.md`, Shared Core integrity). Burst jobs and ECS components need them in practice (`Mathf` is not what Burst optimizes; component fields must be blittable). `Game.Client.*` MonoBehaviours may keep `UnityEngine` types where a `Transform` is read or written directly.
2. **Match vector width to the data** (`float2` planar, `float3` 3D, `float4` only for a real 4-component value). Per [vector-and-matrix-types.md](references/vector-and-matrix-types.md).
3. **Build every `quaternion` and matrix through its factory methods**, never field-by-field. Same file.
4. **Use `math.*`, never `Mathf`/`System.Math`, for elementary functions in Core and Burst code**; swizzle for readable rearrangement, stopping where a named variable reads better. Per [math-functions-and-swizzling.md](references/math-functions-and-swizzling.md).
5. **Burst, job and ECS code uses `Unity.Mathematics.Random` with an explicit, injected, nonzero seed**, state threaded as a field or `ref`, never static; Shared Core randomness is `nrandom-random-generation`'s. Per [random-numbers.md](references/random-numbers.md).
6. **Choose `noise` by character, not habit** — smooth (`cnoise`/`snoise`) vs cell-like (`cellular`). Per [math-functions-and-swizzling.md](references/math-functions-and-swizzling.md).
7. **State the determinism limit.** The type migration removes the `UnityEngine` dependency only; SIMD codegen, `FloatMode` and transcendental precision can still differ across platforms, owned by `unity-burst-compiler` (`FloatMode.Deterministic`, Burst Inspector).
8. **Verify precision-sensitive comparisons** against `Mathf`/`System.Math`; they are not guaranteed bit-identical (`csharp-standards` → `performance-and-algorithms.md`, Verification).
9. **Layer or seed origin unstated → ask before writing.**

## Never
- Present a type migration as fixing determinism.
- Use `UnityEngine.Random` in `Game.Core.*`, or leave a `Random` seed zero/default or wall-clock derived.
- Rename `float3`/`quaternion` to PascalCase: Unity's shader-parity convention, not a `naming-convention.md` violation.

## Output
```
## Mathematics Work — <system/calculation>
- Context: <Game.Core.* / Burst job / ECS component / other>
- Types chosen: <type — rationale>
- UnityEngine types replaced: <Vector3 / Quaternion / Mathf / Random, or none>
- Random: <seed source and how state is threaded, or n/a>
- noise: <function, or n/a>
- Verification: <precision check, or n/a>
- Determinism caveat: <residual FloatMode/SIMD risk stated, or n/a>
- Layer: <Game.Core.* / Game.Client.* / Editor-only>
- Known limitations: <...>
```

## Example
- "Add cooldown jitter in `Game.Core.Abilities` with `UnityEngine.Random.Range`" → declined: used `Unity.Mathematics.Random` seeded once from an injected `uint`, stored in the ability's state so client prediction and server replay identically; where the seed originates stays the caller's responsibility.
