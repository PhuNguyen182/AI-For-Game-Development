---
name: unity-mathematics
description: "Unity.Mathematics: float3, quaternion, math, noise, Random. Use for Core, Burst, jobs and ECS math instead of Mathf."
user-invocable: false
---

# Unity Mathematics

- **Not for:** an injected `IRandom` roll, weighted table or shuffle outside Burst (`nrandom-random-generation`).
- **Not for:** job scheduling (`unity-job-system-and-burst`).
- **Not for:** container choice (`unity-collections`).
- **Not for:** Burst tuning and `FloatMode` (`unity-burst-compiler`).
- **Not for:** ECS component design (`unity-ecs-architecture`).
- **Not for:** physics components (`unity-physics`).
- **Not for:** material overrides (`unity-entities-graphics`).
- **Docs:** https://docs.unity3d.com/Packages/com.unity.mathematics@1.3/ (`manual/`, `api/`) — pinned 1.3.
  - **Version:** keep `@1.3` in any link, because the package adds features between releases.

## References
- **[vector-and-matrix-types.md](references/vector-and-matrix-types.md):** Choosing a vector width, rotation type or matrix, or building a quaternion/matrix.
- **[math-functions-and-swizzling.md](references/math-functions-and-swizzling.md):** Replacing a `Mathf`/`System.Math` call, rearranging components, or picking a `noise` function.
- **[random-numbers.md](references/random-numbers.md):** Any RNG inside Core or a parallel context.

## Steps
1. **Establish the layer first:**
   - **Core:** must use these types, with no `UnityEngine` dependency (`csharp-standards` → `coding-principles.md`, Shared Core integrity).
   - **Burst jobs and ECS components:** need them in practice (`Mathf` is not what Burst optimizes; component fields must be blittable).
   - **Client MonoBehaviours:** may keep `UnityEngine` types where a `Transform` is read or written directly.
2. **Match vector width to the data:** `float2` planar, `float3` 3D, `float4` only for a real 4-component value, per [vector-and-matrix-types.md](references/vector-and-matrix-types.md).
3. **Build every `quaternion` and matrix through its factory methods:** never field-by-field, per [vector-and-matrix-types.md](references/vector-and-matrix-types.md).
4. **Elementary functions in Core and Burst code:** use `math.*`, never `Mathf`/`System.Math`, per [math-functions-and-swizzling.md](references/math-functions-and-swizzling.md).
   - **Swizzle:** for readable rearrangement, stopping where a named variable reads better.
5. **Burst, job and ECS code uses `Unity.Mathematics.Random` with an explicit, injected, nonzero seed:** per [random-numbers.md](references/random-numbers.md).
   - **State:** threaded as a field or `ref`, never static.
   - **Shared Core randomness:** `nrandom-random-generation`'s.
6. **Choose `noise` by character, not habit:** per [math-functions-and-swizzling.md](references/math-functions-and-swizzling.md).
   - **Smooth:** `cnoise`/`snoise`.
   - **Cell-like:** `cellular`.
7. **State the determinism limit:** the type migration removes the `UnityEngine` dependency only.
   - **Can still differ across platforms:** SIMD codegen, `FloatMode` and transcendental precision.
   - **Owner of that risk:** `unity-burst-compiler` (`FloatMode.Deterministic`, Burst Inspector).
8. **Verify precision-sensitive comparisons against `Mathf`/`System.Math`:** they are not guaranteed bit-identical (`csharp-standards` → `performance-and-algorithms.md`, Verification).
9. **Missing input:** before writing, layer or seed origin unstated → dispatched agent `Blocked` or `Needs-decision`; main session `AskUserQuestion`.

## Never
- **Type migration:** never present it as fixing determinism.
- **Random source and seed:** never use `UnityEngine.Random` in Core, or leave a `Random` seed zero/default or wall-clock derived.
- **Rename `float3`/`quaternion` to PascalCase:** it is Unity's shader-parity convention, not a `naming-convention.md` violation.

## Output
```
## Mathematics Work — <system/calculation>
- Context: <Core / Burst job / ECS component / other>
- Types chosen: <type — rationale>
- UnityEngine types replaced: <Vector3 / Quaternion / Mathf / Random, or none>
- Random: <seed source and how state is threaded, or n/a>
- noise: <function, or n/a>
- Determinism caveat: <residual FloatMode/SIMD risk stated, or n/a>
- Layer: <Core / Client / Editor-only>
```

## Example
- **"Add cooldown jitter in `_Project.Scripts.Abilities.Core` with `UnityEngine.Random.Range`":** declined.
  - **Did instead:** used `Unity.Mathematics.Random` seeded once from an injected `uint`, stored in the ability's state so client prediction and server replay identically.
  - **Seed origin:** stays the caller's responsibility.
