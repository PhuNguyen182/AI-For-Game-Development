# Shared Core & Burst Compatibility — Layer Rules and the Determinism Boundary

Source: not sourced from a single URL — synthesized from `coding-principles.md`'s Shared Core integrity section, `performance-and-algorithms.md`, and this package's own manual content.
Covers: SKILL.md §4 — **"Identify the context before choosing any type"**, **"Never claim byte-for-byte cross-platform determinism from type choice alone"**.

Settles which layer requires these types and, more importantly, exactly how
far the determinism claim reaches — the boundary most often overstated after a
type migration. Sibling-skill ownership is tabulated at the end.

## Why these types satisfy Shared Core

| Property | What it decides | Source |
|---|---|---|
| Blittable, unmanaged structs | Nothing here allocates or needs marshalling, so the same value crosses into a job or component unchanged | synthesized |
| Zero `UnityEngine` dependency | Exactly what `coding-principles.md`'s Shared Core integrity section requires of `Game.Core.*`, where `Vector3`/`Quaternion`/`Random` are disallowed | synthesized |
| Burst's preferred data model | Burst is built to vectorize these operations, so the Shared Core choice and the performance choice coincide rather than trade off | synthesized |

## Layer-by-layer requirement

| Context | Requirement | Source |
|---|---|---|
| `Game.Core.*` Shared Core | Mandatory — a `UnityEngine` math type here is a rule violation, not a preference | synthesized |
| Burst-compiled job or method | Required in practice: `Mathf` is not the surface Burst optimizes around | synthesized |
| ECS component | Required — component fields must be blittable and unmanaged | synthesized |
| `Game.Client.*` MonoBehaviour | Not required; `UnityEngine` types are correct where a `Transform` is being read or written directly | synthesized |

## The determinism boundary

| Claim | Status | Source |
|---|---|---|
| "No `UnityEngine` dependency in Shared Core" | **Satisfied** by the type migration alone | synthesized |
| "Bit-identical results across platforms and architectures" | **Not satisfied** — SIMD codegen, instruction reordering, `FloatMode`, and transcendental precision all still vary | synthesized |
| Who owns the residual | `unity-burst-compiler`, via `FloatMode.Deterministic` and Burst Inspector verification | synthesized |

**Critical caveat**: presenting a type migration as having "fixed determinism"
is the specific overclaim this file exists to prevent. It fixes the dependency
half and leaves the numeric half untouched.

## Sibling-skill ownership

| Neighbour | This skill owns | The neighbour owns | Source |
|---|---|---|---|
| `unity-burst-compiler` | That these types are what Burst vectorizes best | HPC# subset compliance, `FloatMode`, intrinsics, AOT settings, Burst Inspector verification | synthesized |
| `unity-ecs-architecture` | The `float3`/`quaternion` field types a component uses | Modeling the component, system, and query themselves | synthesized |
| `unity-collections` | The element type, e.g. the `float3` in `NativeArray<float3>` | Which container holds it, and its allocator | synthesized |
| `unity-job-system-and-burst` | The math the job body performs | Scheduling it and chaining `JobHandle` dependencies | synthesized |
