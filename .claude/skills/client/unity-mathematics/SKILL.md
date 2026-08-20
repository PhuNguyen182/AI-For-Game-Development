---
name: unity-mathematics
description: >
  Technique for `Unity.Mathematics` — the shader-like, SIMD-friendly C# math
  library (`float2`/`float3`/`float4` and their `int`/`bool`/`double`
  variants, `float3x3`/`float4x4` matrices, `quaternion`, swizzling, the
  static `math` class, `noise` functions, and the explicit-state `Random`
  struct). Because every type has zero `UnityEngine` dependency and is a
  blittable, unmanaged struct, this is the correct math library for
  `Game.Core.*` Shared Core code (per `coding-principles.md`'s Shared Core
  integrity rule) as well as for Burst-compiled jobs and ECS components — the
  same types work identically in all three contexts.
  `Unity.Mathematics.Random` is specifically the seeded, injectable,
  explicit-state RNG that `coding-principles.md` requires in place of
  `UnityEngine.Random` for deterministic Shared Core logic. Do not use this
  for scheduling jobs or choosing `NativeContainer`/collection types — that's
  `unity-job-system-and-burst`/`unity-collections`. Do not use this for
  Burst compilation tuning itself (HPC# subset, `FloatMode`, AOT, intrinsics)
  — that's `unity-burst-compiler`, even though `Unity.Mathematics` types are
  what Burst vectorizes most efficiently. Do not use this to model ECS
  components/systems — that's `unity-ecs-architecture`, even though a
  component's fields are commonly typed with `float3`/`quaternion` from this
  library. Do not use this to choose physics components, collider shapes,
  joints/motors, or spatial queries — that's `unity-physics`, even though
  every physics parameter is `float3`/`quaternion`-typed. Do not use this to
  choose rendering/material-override components — that's
  `unity-entities-graphics`, even though override components are commonly
  `float4`-typed.
---

# Unity Mathematics — Vector/Matrix Types, math, Random & noise

Sources: see [references/](references/) for the Unity Manual/Scripting API root links, split by topic — [root-links.md](references/root-links.md), [vector-and-matrix-types.md](references/vector-and-matrix-types.md), [math-functions-and-swizzling.md](references/math-functions-and-swizzling.md), [random-numbers.md](references/random-numbers.md), [noise-functions.md](references/noise-functions.md), [shared-core-and-burst-compatibility.md](references/shared-core-and-burst-compatibility.md).

## 1. Objective
Use the right `Unity.Mathematics` type and function surface for the data at hand — correct vector/matrix width, correct rotation representation, a properly seeded and injected `Random` for deterministic Shared Core logic, the right `noise` function for procedural generation — without drifting into job scheduling, collection choice, Burst tuning, or ECS component design.

## 2. Role
Act as the math-library specialist: given code that needs vector/matrix/rotation math, a deterministic RNG, or procedural noise — in `Game.Core.*`, a Burst-compiled job, or an ECS component — you pick the right `Unity.Mathematics` type and API, and you make sure `Game.Core.*` never leaks a `UnityEngine.Vector3`/`Quaternion`/`Random` dependency where a `Unity.Mathematics` equivalent belongs instead.

## 3. When to invoke this skill
- Choosing `float2`/`float3`/`float4` (or an `int`/`bool`/`double` variant) over `UnityEngine.Vector2`/`Vector3`/`Vector4` for `Game.Core.*`, Burst-compiled, or ECS component data.
- Using `quaternion` instead of `UnityEngine.Quaternion` for rotation math outside a MonoBehaviour's own `Transform` access.
- Using `float3x3`/`float4x4` for transform/matrix math (`float4x4.TRS`, `float4x4.LookAt`, etc.) instead of hand-rolled matrix arithmetic.
- Using swizzling (`v.xyz`, `v.xy`, `v.zyx`, etc.) to rearrange vector components instead of constructing a new vector field-by-field.
- Using the static `math` class (`math.sin`, `math.sqrt`, `math.normalize`, `math.dot`, `math.cross`, `math.lerp`, `math.clamp`, etc.) instead of `Mathf`/`System.Math` inside `Game.Core.*` or a Burst-compiled job.
- A Shared Core system needs a seeded, deterministic RNG — using `Unity.Mathematics.Random` with an explicitly managed/injected seed instead of `UnityEngine.Random`.
- Choosing and applying a `noise` function (`noise.cnoise`, `noise.snoise`, `noise.cellular`) for procedural generation.
- Negative trigger: scheduling jobs, `JobHandle` dependency chains, or `NativeContainer`/collection type choice — that's `unity-job-system-and-burst`/`unity-collections`.
- Negative trigger: Burst-specific compilation tuning (HPC# subset, `FloatMode`, intrinsics, AOT settings) — that's `unity-burst-compiler`, even when the code being tuned is full of `Unity.Mathematics` types.
- Negative trigger: modeling ECS entities/components/systems/queries — that's `unity-ecs-architecture`, even when a component's fields are typed with `float3`/`quaternion`.
- Negative trigger: choosing physics components, collider shapes, joints/motors, or spatial queries — that's `unity-physics`, even though every physics parameter here is `float3`/`quaternion`-typed.
- Negative trigger: choosing rendering/material-override components — that's `unity-entities-graphics`, even though override components are commonly `float4`-typed.

## 4. How to use this skill
1. **Identify the context first.** `Game.Core.*` Shared Core code, a Burst-compiled job/method, and an ECS component all require `Unity.Mathematics` types over their `UnityEngine` equivalents — for Shared Core specifically, this isn't a style preference, it's what `coding-principles.md`'s "no `UnityEngine` dependency in Shared Core" rule requires.
2. **Pick the vector width that matches the actual dimensionality** — `float2` for 2D data, `float3` for 3D, `float4` only when a real 4-component value (e.g. a homogeneous coordinate, an RGBA color) is involved. Don't default to `float4` "to be safe."
3. **Use swizzling for readable component rearrangement** (`position.xz` for a ground-plane projection, `color.rgb` for dropping alpha) instead of manually constructing a new vector field-by-field — but keep complex expressions readable with a named intermediate variable rather than chaining swizzles until the intent is unclear.
4. **Use the static `math` class for every elementary function** in `Game.Core.*` or a Burst-compiled job — `math.sin`/`math.sqrt`/`math.normalize`/`math.dot`/`math.cross`/`math.lerp`/`math.clamp`, etc. — never `Mathf`, which both pulls a `UnityEngine` dependency into Shared Core and isn't the type Burst is optimized around.
5. **Use `quaternion` for all Shared Core/Burst/ECS rotation data**, built via its factory methods (`quaternion.identity`, `quaternion.AxisAngle`, `quaternion.Euler`, `quaternion.LookRotation`) — never mix in `UnityEngine.Quaternion` on that side of the boundary.
6. **Use `float3x3`/`float4x4` with the library's own factory methods** for transform composition (`float4x4.TRS`, `float4x4.LookAt`) rather than assembling matrix math by hand.
7. **For any Shared Core RNG need, use `Unity.Mathematics.Random` with an explicit, injected, nonzero seed** — never `UnityEngine.Random`, per `coding-principles.md`'s determinism requirement. Thread the `Random` value through as an explicit field/parameter (it's a mutable struct — pass by `ref` when a method needs to advance its state), not a static/global instance, so results stay reproducible and independent across parallel uses.
8. **Choose the `noise` function by dimensionality and desired statistical properties**, not by habit — `noise.cnoise` (classic Perlin) vs. `noise.snoise` (simplex) vs. `noise.cellular` (Worley/cellular) produce visually and statistically different results; pick deliberately for what the effect actually needs.
9. **Don't claim byte-for-byte cross-platform determinism from type choice alone.** Using `Unity.Mathematics` types satisfies the "no `UnityEngine` dependency" half of `coding-principles.md`'s Shared Core determinism rule, but SIMD codegen, `FloatMode`, and transcendental-function precision can still diverge across platforms/architectures — that residual risk is `unity-burst-compiler`'s `FloatMode.Deterministic` concern, not something this skill can guarantee by itself. State this explicitly rather than overclaiming determinism.
10. **Verify precision-sensitive comparisons rather than assuming bit-identical behavior** against `Mathf`/`System.Math` equivalents — the libraries aren't guaranteed to agree bit-for-bit even on the "same" function.

## 5. Specific goals / tasks this skill performs
- Choosing the right vector/matrix/quaternion type and width for a given piece of data.
- Migrating `Game.Core.*` code off `UnityEngine.Vector3`/`Quaternion`/`Mathf`/`Random` onto their `Unity.Mathematics` equivalents to satisfy the Shared Core "no `UnityEngine` dependency" rule.
- Applying swizzling for readable, allocation-free component rearrangement.
- Setting up `Unity.Mathematics.Random` with a properly managed, injected seed for deterministic RNG needs.
- Selecting and applying `noise` functions for procedural generation.
- Out of scope: job scheduling/`NativeContainer` lifetime (`unity-job-system-and-burst`); collection type choice (`unity-collections`); Burst compilation tuning, including the deeper determinism guarantees `FloatMode` controls (`unity-burst-compiler`); ECS component/system/query design (`unity-ecs-architecture`).

## 6. Output format
```
## Mathematics Work — <system/calculation name>
- Context: Game.Core.* Shared Core / Burst job / ECS component / other
- Type(s) chosen: <float2/float3/float4, float3x3/float4x4, quaternion, etc.> — rationale
- UnityEngine types replaced: <Vector3/Quaternion/Mathf/Random — or "none, new code">
- Swizzling used: <yes/no — which>
- Random usage: <seed source, how the state is threaded/injected — or "not applicable">
- noise function(s) used: <cnoise/snoise/cellular — or "not applicable">
- Determinism caveat disclosed: <yes — see guardrail 9, or "not applicable, non-Core code">
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: a Shared Core damage-falloff calculation (`Game.Core.Combat`) was using `UnityEngine.Vector3.Distance` and `Mathf.Clamp01`, which violates the Shared Core "no `UnityEngine` dependency" rule in `coding-principles.md`.
- Output: replaced the parameters/return with `float3`, distance math with `math.distance` (and noted `math.distancesq` as the cheaper alternative per `performance-and-algorithms.md`'s squared-distance guidance when only a threshold comparison is needed), and `Mathf.Clamp01` with `math.saturate`; confirmed via a project-wide reference search that `Game.Core.Combat` no longer references `UnityEngine` anywhere in this file.

**Example 2**
- Input: "Add a cooldown-jitter to the ability system using `UnityEngine.Random.Range` so cooldowns don't all line up." — the ability system's cooldown logic lives in `Game.Core.Abilities`.
- Output: declined `UnityEngine.Random` for Shared Core code — used `Unity.Mathematics.Random` instead, seeded once from an explicit, injected `uint` (not derived from wall-clock time) and stored as part of the ability's own state so the jitter sequence is reproducible for both client prediction and server authority; disclosed that the seed source itself (where the injected value ultimately comes from) is the caller's responsibility, not this change's.

## 8. Edge cases & guardrails
- `Unity.Mathematics` types resolve the "no `UnityEngine` dependency" half of Shared Core determinism, but do **not** by themselves guarantee identical results across platforms/architectures — SIMD codegen, `FloatMode`, and transcendental-function precision can still diverge; that residual is `unity-burst-compiler`'s concern, not a guarantee this skill can make alone.
- Never use `UnityEngine.Random` in `Game.Core.*` — always `Unity.Mathematics.Random` with an explicit, injected, nonzero seed.
- Never leave a `Random`'s seed at a zero/default value or derive it from wall-clock time in Shared Core — both break the determinism `coding-principles.md` requires.
- Don't reach for `float4` when `float2`/`float3` fits the actual data — wasted struct width costs SIMD lanes and copy overhead for no benefit.
- Swizzle for readability, not as a substitute for a meaningful intermediate variable name in a genuinely complex expression.
- The library's lowercase type names (`float3`, `quaternion`) are Unity's own deliberate shader-parity convention, not a violation of this project's PascalCase-for-types rule in `naming-convention.md` — don't "fix" them.
- Keep any noise/random usage inside `Game.Core.*` driven by an explicit, injected seed — never derived from wall-clock time or any other non-deterministic source.
- Don't assume `math` class functions are bit-identical to `Mathf`/`System.Math` equivalents on values where precision-sensitive comparisons matter — verify rather than assume.
