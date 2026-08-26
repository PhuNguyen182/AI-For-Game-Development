---
name: compute-shader-vfx
description: >
  Technique for compute shaders whose deliverable is a visual effect — GPU
  particle simulation, procedural mesh and vertex deformation, curl-noise and
  flow fields, and any GPU buffer feeding a shader or VFX Graph. Covers the
  C#-to-HLSL struct stride contract, `RWStructuredBuffer`,
  `AppendStructuredBuffer`, `[numthreads]` and dispatch sizing, ping-pong
  buffering, `DrawProceduralIndirect` with indirect args,
  `AsyncGPUReadback` versus a blocking `GetData`, `ComputeBuffer.Release`, and
  platform compute support. Use when a visual effect is GPU-driven.
  Not for: non-visual compute throughput (`tech-lead-performance`); CPU
  parallel work (`unity-job-system-and-burst`); the shader consuming the
  buffer (`shader-authoring`); particle graph structure
  (`vfx-particle-authoring`); ECS mesh deformation
  (`unity-entities-graphics`).
---

# Compute Shaders for Visual Effects

## 1. Objective
Produce compute passes that drive a visual effect correctly, release what they allocate, and degrade honestly on hardware that cannot run them. It prevents the failure modes compute code has that ordinary C# does not: a C# struct whose stride disagrees with the HLSL one, which corrupts data rather than throwing; a kernel with no bounds check writing past the element count because dispatch rounds up to whole thread groups; an in-place read-modify-write across parallel threads that is a race rather than a sequence; a `ComputeBuffer` the GC can never reclaim; a blocking `GetData` that stalls the frame on GPU completion; and a compute-only effect that renders nothing at all on a device that does not support it.

## 2. Role
Act as the GPU compute specialist for visual effects on the client track — the tool reached for when a Tech Spec asks for a GPU-driven visual behaviour. You own the kernels and the buffer contract with the C# side that dispatches them; you do not own compute work whose purpose is throughput on a non-visual system.

## 3. When to invoke this skill
- A Tech Spec calls for a GPU-driven visual effect: large-scale particle simulation, vertex displacement or deformation, GPU-generated procedural geometry, a curl-noise or flow field driving motion.
- Defining or fixing the struct contract between a C# buffer and its HLSL counterpart.
- Sizing `[numthreads]` and the dispatch, or fixing a kernel that processes the wrong element count.
- Wiring compute output into rendering through `DrawProceduralIndirect`, `DrawMeshInstancedIndirect`, or a VFX Graph custom block.
- A reported symptom: the effect renders garbage, renders nothing on one device class, drops frames at a specific point in the frame, or leaks memory across scene loads.
- Negative trigger: the primary purpose is throughput on a non-visual system — pathfinding, inventory search, bulk simulation for its own sake — that is `tech-lead-performance`.
- Negative trigger: the work is CPU-side parallelism over native containers — that is `unity-job-system-and-burst`; both are "many elements at once", but the deciding question is whether the result must reach the GPU as a buffer or the CPU as data.
- Negative trigger: the shader that reads the buffer and shades the result — that is `shader-authoring`.
- Negative trigger: the particle graph's emission and simulation structure — that is `vfx-particle-authoring`; this skill writes a custom kernel it consumes.
- Negative trigger: compute skinning and blend shapes for ECS entities — that is `unity-entities-graphics`, which has its own deformation system with its own limits.

## 4. How to use this skill
1. **Define the buffer contract before writing a kernel** — the HLSL `struct` must match the C# one in field order, type sizes, and resulting stride, because a mismatch does not throw; it reinterprets memory and produces plausible-looking garbage. State the stride explicitly on both sides.
2. **Confirm compute support on every shipping platform before committing to the approach** — check `SystemInfo.supportsComputeShaders` and the project's actual device floor. If support is uncertain, design the fallback now, since a compute-only effect on unsupported hardware shows the player nothing at all, which is worse than a simpler effect that renders.
3. **Give each kernel one job** — Emit, Simulate, Sort, Compact — rather than one kernel doing everything, per the Single Responsibility rule in `coding-principles.md`. Separate kernels are also independently profilable, which a monolithic one is not.
4. **Derive the dispatch from the live element count and bounds-check inside the kernel** — `Mathf.CeilToInt(count / (float)groupSize)` rounds up, so the final thread group runs threads with no element behind them; without an early `if (id.x >= count) return;` those threads write past the end. Never hardcode a group count.
5. **Choose `[numthreads]` deliberately against the target hardware** — 64 suits AMD wavefronts, 32 suits NVIDIA warps, and 64 to 256 is the usual range on mobile; state which target drove the number rather than inheriting a template's default.
6. **Ping-pong any buffer a pass both reads and writes in the same dispatch** — parallel threads have no ordering between them, so an in-place read-modify-write is a race, not a shortcut. Read from one buffer, write to the other, swap after the dispatch.
7. **Keep the GPU result out of every gameplay decision** — per `coding-principles.md`'s Shared Core integrity section, the rule lives in `Game.Core.*` and the server evaluates it independently, so a value that exists only in GPU memory can never be the source of truth. Compute output drives visuals; if a rule needs the same data, compute it on the CPU as well and treat the GPU copy as presentation.
8. **Read back with `AsyncGPUReadback`, never a blocking `GetData` in a frame path** — `GetData` stalls the CPU until the GPU has finished, which is the whole pipeline's worth of latency; the async request delivers a frame or more later, so any consumer must tolerate that delay by design.
9. **Feed rendering through an indirect draw** — `DrawProceduralIndirect` or `DrawMeshInstancedIndirect` with an args buffer filled from a GPU counter keeps the instance count on the GPU, so the CPU never has to read back just to know how many to draw.
10. **Release every `ComputeBuffer` on every path**, in `OnDisable` or `OnDestroy` and on early returns, per `performance-and-algorithms.md`'s Memory discipline section — an unreleased buffer is native memory the managed GC never reclaims and never reports.
11. **Validate at small scale before scaling up** — confirm correctness at a hundred elements with the Frame Debugger or a graphics inspector; a stride or bounds bug that is invisible at that size is obvious at ten thousand, and far cheaper to find first.
12. **State the per-frame dispatch cost when it is non-trivial** — element count times kernel complexity, per `performance-and-algorithms.md`'s Algorithmic complexity discipline section, and back any performance claim with a capture rather than the expectation that the GPU is free.
13. **Split the work when a request serves both a visual outcome and raw throughput** — say which half is which and coordinate with `tech-lead-performance` rather than silently owning both under one deliverable.

## 5. Specific goals / tasks this skill performs
- GPU particle simulation buffers feeding a shader or VFX Graph.
- GPU-driven vertex displacement, deformation, and procedural geometry for visual effects.
- Compute-based noise and force fields driving particle or vertex motion.
- The C#-to-HLSL struct and stride contract, and diagnosis of corruption caused by it.
- Dispatch sizing, `[numthreads]` selection, and kernel bounds correctness.
- Indirect draw wiring and buffer lifecycle management.
- Platform compute-support checks and fallback design.
- Out of scope: non-visual compute throughput (`tech-lead-performance`); CPU-side parallel work (`unity-job-system-and-burst`); the consuming shader (`shader-authoring`); particle graph structure (`vfx-particle-authoring`); ECS mesh deformation (`unity-entities-graphics`).

## 6. Output format
```
## Compute VFX — <effect name>
- Visual outcome: <what this pass produces on screen>
- Buffer contract: <struct fields, stride, and how the C#/HLSL match was confirmed>
- Kernels: <one line each — name and single responsibility>
- Thread group size: <N> — the target hardware that decided it
- Dispatch sizing: <formula> — bounds check present in kernel: <yes>
- Ping-pong: <which buffers, or "not needed — no in-place read-write">
- Render wiring: <DrawProceduralIndirect / DrawMeshInstancedIndirect / VFX Graph block>
- Readback: <AsyncGPUReadback and the latency the consumer tolerates — or "none">
- Buffer lifecycle: <created in, released in — including early-return paths>
- Platform support: <verified targets, and the fallback where compute is unavailable>
- Cost: <elements × kernel complexity per frame, with any measurement taken>
- Layer: <Game.Client.* presentation only — no gameplay rule reads this buffer>
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered effect does not cover>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Implement a compute-driven particle effect for the new ultimate ability" on a PC-only ability in a project that also ships mobile.
- Output: three kernels — Emit consuming a spawn list, Simulate integrating motion against a curl-noise field, Compact removing dead particles; 128-thread groups chosen against the PC GPU floor and stated; dispatch derived from a live counter with an `id.x >= count` guard; ping-pong position and velocity buffers since Simulate reads and writes both; drawn through `DrawMeshInstancedIndirect` with the args buffer filled from the GPU counter so no readback is needed; buffers released in `OnDisable` including the early-return path; the ability is PC-only per the Tech Spec, and mobile falls back to the existing Shuriken effect rather than rendering nothing.

**Example 2**
- Input: "Read the particle positions back each frame so the gameplay code can tell when a projectile particle hits an enemy."
- Output: declined as specified, on two grounds. A blocking `GetData` every frame stalls the CPU on GPU completion, and `AsyncGPUReadback` returns at least a frame late, so neither gives a hit test usable this frame. More fundamentally, a hit is a game rule: it lives in `Game.Core.*` where the server evaluates it too, so it cannot depend on a value that exists only in GPU memory. Kept the collision test on the CPU against the authoritative projectile state and left the compute pass driving the visual trail alone.

**Example 3**
- Input: a GPU deformation effect renders correct geometry for most vertices and garbage in a thin band at the end of the mesh.
- Output: two independent causes found together. The kernel had no bounds check, so the final thread group wrote past the vertex count — dispatch rounds up to whole groups, and those extra threads are real. The C# struct also carried a trailing `float` the HLSL struct did not, so the strides disagreed and every element after the first read shifted. Fixed both per §4's contract and dispatch steps, and re-validated at a hundred vertices before scaling back up.

## 8. Edge cases & guardrails
- Never assume the C# and HLSL structs match — confirm the stride on both sides; a mismatch corrupts silently rather than throwing.
- Never dispatch without a bounds check in the kernel — the last thread group always runs threads with no element behind them.
- Never read and write the same buffer in one dispatch — parallel threads have no ordering, so it is a race regardless of how the code reads.
- Never let a gameplay rule depend on GPU-only data — it cannot be reproduced by the server, and reading it back is either a stall or a frame late.
- Never call a blocking `GetData` in a per-frame path — it stalls the CPU on the GPU's whole queue.
- Never leave a `ComputeBuffer` unreleased on any path — it is native memory the GC cannot see, and it survives the scene that created it.
- Never ship a compute-only effect without checking platform support — an unsupported device shows nothing, which reads as a missing feature rather than a lower-fidelity one.
- Never hardcode a dispatch group count — derive it from the live element count every frame.
- If a request mixes a visual outcome with a raw throughput goal, split it with `tech-lead-performance` rather than owning both.
