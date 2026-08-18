---
name: compute-shader-vfx
description: >
  Technique for authoring compute shaders whose deliverable is a visual
  effect — GPU particle simulation, procedural mesh deformation, curl-noise
  fields, or any GPU-driven buffer that feeds a shader or VFX Graph. Use this
  whenever a Tech Spec calls for a compute-shader-driven visual behavior. Do
  not use this when the compute shader's primary purpose is raw performance
  optimization of a non-visual system (pathfinding, physics, bulk simulation
  for its own sake) — that ownership belongs to Tech Lead – Performance. When
  a single request serves both a visual outcome and a raw optimization goal,
  split by primary purpose and coordinate rather than owning it solo.
---

# Compute Shader for VFX

## 1. Objective
Produce correct, leak-free, platform-aware compute shaders that drive a visual effect — never a black-box GPU kernel whose buffers outlive their scene, and never a compute-only visual that silently has no fallback on hardware that can't run it.

## 2. Role
Act as a GPU compute specialist operating strictly inside the visual-effects boundary. You own the kernel design and the buffer contract with the C# side that dispatches it; you do not own compute shader work whose goal is raw throughput on a non-visual system.

## 3. When to invoke this skill
- A Tech Spec calls for a compute-shader-driven visual effect: large-scale GPU particle simulation, GPU vertex displacement/deformation, a procedural mesh generated on the GPU for a visual effect, a curl-noise or force field driving particle motion.
- Negative trigger: the task's primary purpose is raw performance optimization of a system that isn't a visual effect (e.g. moving inventory search or pathfinding to a compute shader purely for framerate) — that belongs to Tech Lead – Performance; do not take this on.
- Negative trigger: a request that mixes both goals in one compute shader — stop and split the work by primary purpose with Tech Lead – Performance instead of silently doing both under one hat (this mirrors the agent's own coordination rule).

## 4. How to use this skill
1. **Define the buffer contract first**: the `struct` layout used in the compute shader must match the C#-side struct exactly in field order, size, and alignment (stride) — a mismatch here doesn't throw, it silently corrupts data. Use `RWStructuredBuffer<T>` for read-write particle/vertex state, and `AppendStructuredBuffer<T>` / `ConsumeStructuredBuffer<T>` for spawn/death lists.
2. **Verify platform compute support before committing to the approach.** Not every mobile GPU/API level supports compute shaders at the feature level the effect needs. If the project ships to a platform where support is uncertain, either confirm it explicitly or design a CPU/Shuriken fallback path (see `vfx-particle-authoring`) rather than shipping a compute-only effect that silently doesn't render on some devices.
3. **Design kernels around one job each** (Emit, Simulate, Sort, ...) rather than one monolithic kernel doing everything — same single-responsibility reasoning as the project's SOLID rule, applied to GPU kernels.
4. **Choose thread group size deliberately** (a common starting point is 64, 128, or 256 threads per group) based on the target hardware's warp/wavefront size, and state the choice rather than picking it arbitrarily. Size the dispatch off the actual live element count — `Mathf.CeilToInt(particleCount / (float)groupSize)` — never a hardcoded group count that silently drops or wastes work as the count changes.
5. **Use ping-pong (double) buffering** for any pass that both reads and writes the same data set within a frame — an in-place read-modify-write across parallel threads is a race condition, not a correctness detail to skip.
6. **Wire results into rendering** via `DrawProceduralIndirect`/`DrawMeshInstancedIndirect` with an indirect-args buffer sized from a GPU counter, or by exposing the buffer to a consuming shader/VFX Graph "Custom HLSL" block via `SetBuffer`.
7. **Release every `ComputeBuffer`.** Any buffer created in C# to back the compute shader must be `.Release()`d in `OnDisable`/`OnDestroy` — an unreleased `ComputeBuffer` is native memory the managed GC never reclaims, which is the compute-specific case of the project's Memory discipline rule.
8. **Validate at small scale first.** Confirm correctness on a small element count using the frame debugger/graphics inspector before scaling up to the effect's real particle/vertex count — a bug that's invisible at 100 elements is often obvious at 10,000.
9. **State the per-frame dispatch cost** (element count × kernel complexity) in a comment when it's non-trivial, per the algorithmic-complexity discipline in `performance-and-algorithms.md`.

## 5. Specific goals / tasks this skill performs
- GPU particle simulation buffers feeding a shader or VFX Graph.
- GPU-driven mesh deformation / procedural vertex displacement for a visual effect.
- Compute-based noise/force fields (curl noise, flow fields) driving particle or vertex motion.
- Out of scope: any compute shader whose primary purpose is non-visual throughput (Tech Lead – Performance's territory).

## 6. Output format
```
## Compute Shader VFX — <effect name>
- Purpose: <visual outcome this compute pass produces>
- Buffer contract: <struct layout, stride, C#-side match confirmed: yes/no>
- Kernels: <list, one line each on responsibility>
- Thread group size: <N> — rationale: <...>
- Dispatch sizing: <formula/derivation, not a hardcoded constant>
- Platform compute support verified: <platforms> / fallback plan: <CPU path or "none needed, PC/console only per Tech Spec">
- ComputeBuffer lifecycle: created in <method>, released in <method>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: "Implement a compute-shader-driven particle VFX for the new ability."
- Output: three kernels (Emit/Simulate/Sort), 128-thread groups sized off a live particle counter, ping-pong position buffers, results fed to a `DrawMeshInstancedIndirect` call reading a Shader Graph-authored particle shader; mobile fallback noted as out of scope per Tech Spec (PC-only ability).

**Example 2**
- Input: "GD wants a GPU-driven cloth-like flag ripple for background scenery."
- Output: single Simulate kernel doing spring-mass integration on a vertex buffer, dispatched once per flag instance, buffer released on flag pool return; flagged to Tech Lead – Performance for awareness since flag count could scale — but ownership stays here because the deliverable is visual, not throughput-driven.

## 8. Edge cases & guardrails
- Never leave a `ComputeBuffer` unreleased — check every code path that creates one has a matching release, including early-return/disable paths.
- Never assume compute shader support on a platform without checking — a silent compute failure on unsupported hardware reads to the player as "the effect just doesn't show up," which is worse than a lower-fidelity fallback.
- If a request's primary purpose is ambiguous between visual output and raw computation speed, ask or split with Tech Lead – Performance rather than silently owning both.
- Don't hardcode thread group counts or dispatch dimensions — derive them from the live element count every time.
