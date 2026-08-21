---
name: unity-mathematics
description: >
  `Unity.Mathematics` — the shader-like, SIMD-friendly C# math library:
  `float2`/`float3`/`float4` and their `int`/`bool`/`double` variants,
  `float3x3`/`float4x4`, `quaternion`, swizzling (`v.xz`, `v.rgb`), the static
  `math` class (`math.normalize`, `math.saturate`, `math.distancesq`), `noise`
  (`cnoise`/`snoise`/`cellular`), and the explicit-state `Random` struct. Every
  type is a blittable unmanaged struct with no `UnityEngine` dependency, so it
  is the math library for `Game.Core.*`, Burst jobs, and ECS components alike,
  and `Unity.Mathematics.Random` is the seeded, injectable RNG Shared Core
  requires instead of `UnityEngine.Random`. Not for: job scheduling
  (`unity-job-system-and-burst`), container choice (`unity-collections`), Burst
  tuning and `FloatMode` (`unity-burst-compiler`), ECS component design
  (`unity-ecs-architecture`), physics components (`unity-physics`), material
  overrides (`unity-entities-graphics`).
---

# Unity Mathematics — Vector/Matrix Types, math, Random & noise

## Bundled resources

### References
Read-only context, loaded on demand so this file stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Mathematics 1.3 Manual/API index roots and the version-pin rule | Starting any task here, or before adding a new upstream link |
| [shared-core-and-burst-compatibility.md](references/shared-core-and-burst-compatibility.md) | Why these types satisfy Shared Core, and exactly how far that determinism claim reaches | The code's layer is being established, or someone claims determinism is now solved |
| [vector-and-matrix-types.md](references/vector-and-matrix-types.md) | `floatN`/`quaternion`/`float3x3`/`float4x4` surface and factory methods | Choosing a vector width, a rotation representation, or a matrix type |
| [math-functions-and-swizzling.md](references/math-functions-and-swizzling.md) | The static `math` class and how swizzle properties are generated/documented | Replacing a `Mathf`/`System.Math` call, or rearranging vector components |
| [random-numbers.md](references/random-numbers.md) | `Random` state model, seeding constraints, `NextFloat` ranges | Any RNG is needed inside `Game.Core.*` or a parallel context |
| [noise-functions.md](references/noise-functions.md) | `cnoise`/`snoise`/`cellular` character and dimensionality | Picking a noise function for procedural generation |

## 1. Objective
Use the right `Unity.Mathematics` type and function surface for the data at hand — correct vector/matrix width, correct rotation representation, a properly seeded and injected `Random` for deterministic Shared Core logic, the right `noise` function for procedural generation — without drifting into job scheduling, collection choice, Burst tuning, or ECS component design.

## 2. Role
Act as the math-library specialist for the client track — the tool reached for whenever code needs vector/matrix/rotation math, a deterministic RNG, or procedural noise in `Game.Core.*`, a Burst-compiled job, or an ECS component. You pick the type and API, and you keep `Game.Core.*` from leaking a `UnityEngine.Vector3`/`Quaternion`/`Random` dependency where a `Unity.Mathematics` equivalent belongs.

## 3. When to invoke this skill
- Choosing `float2`/`float3`/`float4` (or an `int`/`bool`/`double` variant) over `UnityEngine.Vector2`/`Vector3`/`Vector4` for `Game.Core.*`, Burst-compiled, or ECS component data.
- Using `quaternion` instead of `UnityEngine.Quaternion` for rotation math outside a MonoBehaviour's own `Transform` access, or `float3x3`/`float4x4` (`float4x4.TRS`, `float4x4.LookAt`) instead of hand-rolled matrix arithmetic.
- Using swizzling (`v.xyz`, `v.xy`, `v.zyx`) to rearrange vector components instead of constructing a new vector field-by-field.
- Using the static `math` class (`math.sin`, `math.sqrt`, `math.normalize`, `math.dot`, `math.cross`, `math.lerp`, `math.clamp`, `math.saturate`) instead of `Mathf`/`System.Math` inside `Game.Core.*` or a Burst-compiled job.
- A Shared Core system needs a seeded, deterministic RNG — `Unity.Mathematics.Random` with an explicitly managed, injected seed instead of `UnityEngine.Random`.
- Choosing and applying a `noise` function (`noise.cnoise`, `noise.snoise`, `noise.cellular`) for procedural generation.
- Negative trigger: scheduling jobs, `JobHandle` dependency chains, or `NativeContainer`/collection type choice — that's `unity-job-system-and-burst`/`unity-collections`.
- Negative trigger: Burst compilation tuning (HPC# subset, `FloatMode`, intrinsics, AOT settings) — that's `unity-burst-compiler`, even when the code being tuned is full of these types.
- Negative trigger: modeling ECS entities/components/systems/queries — that's `unity-ecs-architecture`, even when a component's fields are typed with `float3`/`quaternion`.
- Negative trigger: choosing physics components, collider shapes, joints/motors, or spatial queries — that's `unity-physics`, even though every physics parameter here is `float3`/`quaternion`-typed.
- Negative trigger: choosing rendering/material-override components — that's `unity-entities-graphics`, even though override components are commonly `float4`-typed.

## 4. How to use this skill
1. **Identify the context before choosing any type**, per [shared-core-and-burst-compatibility.md](references/shared-core-and-burst-compatibility.md) (against the version pinned in [root-links.md](references/root-links.md)) — `Game.Core.*`, a Burst-compiled job, and an ECS component each require these types over their `UnityEngine` equivalents. For Shared Core this is not preference: `coding-principles.md`'s Shared Core integrity section forbids the `UnityEngine` dependency outright.
2. **Pick the vector width that matches the actual dimensionality**, per [vector-and-matrix-types.md](references/vector-and-matrix-types.md) — `float2` for 2D, `float3` for 3D, `float4` only for a genuine 4-component value (homogeneous coordinate, RGBA colour). Defaulting to `float4` "to be safe" wastes SIMD lanes and copy width on every pass.
3. **Use swizzling for readable component rearrangement**, per [math-functions-and-swizzling.md](references/math-functions-and-swizzling.md) — `position.xz` for a ground-plane projection, `colour.rgb` for dropping alpha. Stop at the point a named intermediate variable would read better than another chained swizzle.
4. **Use the static `math` class for every elementary function** in `Game.Core.*` or a Burst-compiled job, per [math-functions-and-swizzling.md](references/math-functions-and-swizzling.md) — never `Mathf`, which both pulls a `UnityEngine` dependency into Shared Core and is not the surface Burst is optimized around.
5. **Use `quaternion` for all Shared Core/Burst/ECS rotation data**, built through its factory methods (`quaternion.identity`, `quaternion.AxisAngle`, `quaternion.Euler`, `quaternion.LookRotation`) per [vector-and-matrix-types.md](references/vector-and-matrix-types.md) — never mix `UnityEngine.Quaternion` in on that side of the boundary.
6. **Use `float3x3`/`float4x4` with the library's own factory methods** for transform composition (`float4x4.TRS`, `float4x4.LookAt`) rather than assembling matrix math by hand, per [vector-and-matrix-types.md](references/vector-and-matrix-types.md).
7. **For any Shared Core RNG need, use `Unity.Mathematics.Random` with an explicit, injected, nonzero seed**, per [random-numbers.md](references/random-numbers.md) and `coding-principles.md`'s Shared Core integrity section. Thread the value through as an explicit field or `ref` parameter — never a static instance — so results stay reproducible and independent across parallel uses.
8. **Choose the `noise` function by dimensionality and statistical character**, per [noise-functions.md](references/noise-functions.md) — `cnoise` and `snoise` give smooth continuous variation, `cellular` gives cell-like organic structure. They are not interchangeable, so pick for the effect rather than by habit.
9. **Never claim byte-for-byte cross-platform determinism from type choice alone** — these types satisfy the "no `UnityEngine` dependency" half of the Shared Core rule; SIMD codegen, `FloatMode`, and transcendental precision can still diverge, and that residual belongs to `unity-burst-compiler`. State the caveat rather than overclaiming, per [shared-core-and-burst-compatibility.md](references/shared-core-and-burst-compatibility.md).
10. **Verify precision-sensitive comparisons instead of assuming bit-identical behaviour** against `Mathf`/`System.Math`, per `performance-and-algorithms.md`'s Verification section — the two libraries are not guaranteed to agree bit-for-bit even on the same named function.
11. **If the calling context or the RNG seed's origin is unstated, ask before writing** — step 1 needs the layer and step 7 needs the seed source; either guessed produces code that compiles, runs, and is wrong in a way no compiler reports.

## 5. Specific goals / tasks this skill performs
- Choosing the right vector/matrix/quaternion type and width for a given piece of data.
- Migrating `Game.Core.*` code off `UnityEngine.Vector3`/`Quaternion`/`Mathf`/`Random` onto their `Unity.Mathematics` equivalents.
- Applying swizzling for readable, allocation-free component rearrangement.
- Setting up `Unity.Mathematics.Random` with a properly managed, injected seed for deterministic RNG needs.
- Selecting and applying `noise` functions for procedural generation.
- Out of scope: job scheduling and `NativeContainer` lifetime (`unity-job-system-and-burst`); collection type choice (`unity-collections`); Burst compilation tuning, including the deeper determinism guarantees `FloatMode` controls (`unity-burst-compiler`); ECS component/system/query design (`unity-ecs-architecture`).

## 6. Output format
```
## Mathematics Work — <system/calculation name>
- Context: <Game.Core.* Shared Core / Burst job / ECS component / other>
- Type(s) chosen: <float2 / float3 / float4 / float3x3 / float4x4 / quaternion> — rationale
- UnityEngine types replaced: <Vector3 / Quaternion / Mathf / Random — or "none, new code">
- Swizzling used: <which, or "none">
- Random usage: <seed source and how state is threaded/injected — or "not applicable">
- noise function(s) used: <cnoise / snoise / cellular — or "not applicable">
- Rule compliance: <Shared Core has no UnityEngine dependency, per Shared Core integrity>
- Verification: <how precision-sensitive behaviour was confirmed, or "not applicable">
- Determinism caveat disclosed: <yes — residual FloatMode/SIMD risk stated / not applicable>
- Layer: <Game.Core.* / Game.Client.* / Editor-only>
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered solution does not cover>
- Latent concerns: <failure modes not yet triggered: assumptions holding only under current conditions, thresholds not yet reached>
- Future remediation: <the concrete fix for each concern, each with its trigger condition>
```

## 7. Examples
**Example 1**
- Input: a Shared Core damage-falloff calculation in `Game.Core.Combat` uses `UnityEngine.Vector3.Distance` and `Mathf.Clamp01`, violating the Shared Core "no `UnityEngine` dependency" rule.
- Output: parameters and return retyped to `float3`; distance replaced with `math.distance`, and `math.distancesq` recommended where only a threshold comparison happens, per `performance-and-algorithms.md`'s squared-distance guidance; `Mathf.Clamp01` replaced with `math.saturate`; confirmed by reference search that the file no longer names `UnityEngine`.

**Example 2**
- Input: "Add cooldown jitter to the ability system using `UnityEngine.Random.Range` so cooldowns don't all line up." — the cooldown logic lives in `Game.Core.Abilities`.
- Output: declined for Shared Core code. Used `Unity.Mathematics.Random`, seeded once from an explicit injected `uint` (never wall-clock derived) and stored in the ability's own state so the sequence reproduces identically for client prediction and server authority. Disclosed that where the injected seed itself originates remains the caller's responsibility.

**Example 3**
- Input: a terrain generator needs organic-looking biome cell boundaries and currently calls `noise.snoise` because that was what the last feature used.
- Output: switched to `noise.cellular` — simplex gives smooth continuous variation, which cannot produce cell boundaries no matter how it is thresholded, per [noise-functions.md](references/noise-functions.md). Sample coordinates kept in `float2`, since the generator is planar and `float3` would waste a lane per sample.

## 8. Edge cases & guardrails
- Never present a type migration as having fixed determinism — these types resolve only the `UnityEngine`-dependency half; SIMD codegen, `FloatMode`, and transcendental precision remain `unity-burst-compiler`'s territory.
- Never use `UnityEngine.Random` in `Game.Core.*` — always `Unity.Mathematics.Random` with an explicit, injected, nonzero seed.
- Never leave a `Random` seed at zero/default or derive it from wall-clock time in Shared Core — both break the determinism `coding-principles.md` requires, and neither fails loudly.
- Never reach for `float4` when `float2`/`float3` fits — the unused lanes cost copy width on every pass for nothing.
- Never "fix" the library's lowercase type names (`float3`, `quaternion`) to PascalCase — they are Unity's deliberate shader-parity convention, explicitly not a `naming-convention.md` violation.
- Never assume `math` functions are bit-identical to `Mathf`/`System.Math` where a precision-sensitive comparison depends on it — verify per step 10 instead.
- If the layer or the seed's origin is unstated, ask — both silently determine correctness, and neither is recoverable from the code alone.
