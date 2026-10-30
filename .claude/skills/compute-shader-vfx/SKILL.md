---
name: compute-shader-vfx
description: "Compute shaders whose output is a visual: GPU particles, procedural mesh/vertex deformation, flow fields, buffers feeding Shader/VFX Graph — dispatch sizing, buffer lifetime, mobile limits. Use when a visual effect needs GPU simulation."
user-invocable: false
---

# Compute Shaders for Visual Effects

Not for: non-visual compute throughput (`gameplay-engineer`), CPU parallel work (`unity-job-system-and-burst`; deciding question: must the result reach the GPU as a buffer or the CPU as data), the shader consuming the buffer (`shader-authoring`), particle graph structure (`vfx-particle-authoring`), ECS skinning and deformation (`unity-entities-graphics`), geometry the CPU must read such as a collider-cooked or saved `Mesh` (`unity-3d-mesh`; a readback added to recover that data means the work belonged there).

## Steps
1. **Define the buffer contract before the kernel** — the HLSL `struct` matches the C# one in field order, type sizes and stride; a mismatch does not throw, it reinterprets memory into plausible garbage. State the stride on both sides.
2. **Confirm compute support on every shipping platform** — `SystemInfo.supportsComputeShaders` against the project's device floor, plus `SystemInfo.maxComputeBufferInputsVertex > 0` when a buffer feeds a vertex shader (many GLES devices report 0). If uncertain, design the fallback now: a compute-only effect on unsupported hardware renders nothing.
3. **One job per kernel** (Emit, Simulate, Sort, Compact; `csharp-standards` → `coding-principles.md` "SOLID"); separate kernels profile independently.
4. **Derive the dispatch from the live element count and bounds-check in the kernel** — `Mathf.CeilToInt(count / (float)groupSize)` rounds up, so the last group runs threads with no element; add `if (id.x >= count) return;`. Never hardcode a group count.
5. **Choose `[numthreads]` against the target** and state it: 64 suits AMD wavefronts, 32 NVIDIA warps, 64-256 is usual on mobile.
6. **Ping-pong any buffer a pass both reads and writes in one dispatch** — parallel threads are unordered, so in-place read-modify-write is a race. Read one, write the other, swap after.
7. **Keep GPU results out of gameplay decisions** — rules live in a Core assembly and the server evaluates them independently (`csharp-standards` → `coding-principles.md` "Shared Core integrity"). If a rule needs the same data, compute it on the CPU too and treat the GPU copy as presentation.
8. **Read back with `AsyncGPUReadback`, never a blocking `GetData` in a frame path** — `GetData` stalls the CPU on the GPU queue; the async result arrives a frame or more late, so the consumer must tolerate delay by design.
9. **Feed rendering through an indirect draw** (`Graphics.RenderPrimitivesIndirect` or `Graphics.RenderMeshIndirect` with a `GraphicsBuffer`; `DrawMeshInstancedIndirect` is obsolete) with an args buffer filled from a GPU counter, so the CPU never reads back just to count.
10. **Release every `ComputeBuffer` on every path** (`OnDisable`/`OnDestroy`, early returns) — it is native memory the GC never reclaims and it outlives the scene (`csharp-standards` → `performance-and-algorithms.md` "Memory discipline").
11. **Validate at about a hundred elements** with the Frame Debugger or a graphics inspector before scaling; stride and bounds bugs invisible there are obvious at ten thousand.
12. **State the per-frame dispatch cost when non-trivial** (elements x kernel complexity) and back any performance claim with a capture (`csharp-standards` → `performance-and-algorithms.md` "Verification").
13. **Split a request that mixes a visual outcome with raw throughput** — say which half is which and coordinate with `gameplay-engineer` rather than owning both.

## Output
```
## Compute VFX — <effect>
- Visual outcome: <what the pass produces on screen>
- Buffer contract: <struct fields, stride, how the C#/HLSL match was confirmed>
- Kernels: <name and single responsibility each>
- Thread group size: <N> — target hardware that decided it
- Dispatch sizing: <formula> — bounds check in kernel: <yes>
- Ping-pong: <buffers, or "not needed">
- Render wiring: <RenderPrimitivesIndirect / RenderMeshIndirect / VFX Graph block>
- Readback: <AsyncGPUReadback and tolerated latency, or "none">
- Buffer lifecycle: <created in, released in, including early returns>
- Platform support: <verified targets and the fallback>
- Cost: <elements x complexity per frame, with any measurement>
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Read particle positions back each frame so gameplay can detect projectile hits" → declined: blocking `GetData` stalls the CPU and `AsyncGPUReadback` is at least a frame late, and a hit is a game rule that lives in a Core assembly where the server evaluates it. Kept the hit test on the CPU against authoritative projectile state; the compute pass drives only the visual trail.
