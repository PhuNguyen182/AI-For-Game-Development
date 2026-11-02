---
name: compute-shader-vfx
description: "Compute shaders for visuals: GPU particles, mesh deformation, flow fields, Shader/VFX Graph buffers. Use for GPU sim."
user-invocable: false
---

# Compute Shaders for Visual Effects

- **Not for:** non-visual compute throughput (`gameplay-engineer`).
- **Not for:** CPU parallel work (`unity-job-system-and-burst`).
  - **Deciding question:** must the result reach the GPU as a buffer or the CPU as data.
- **Not for:** the shader consuming the buffer (`shader-authoring`).
- **Not for:** particle graph structure (`vfx-particle-authoring`).
- **Not for:** ECS skinning and deformation (`unity-entities-graphics`).
- **Not for:** geometry the CPU must read, such as a collider-cooked or saved `Mesh` (`unity-3d-mesh`).
  - **Readback added to recover that data:** means the work belonged there.

## Steps
1. **Define the buffer contract before the kernel:** the HLSL `struct` matches the C# one in field order, type sizes and stride.
   - **Mismatch:** does not throw, it reinterprets memory into plausible garbage.
   - **Stride:** state it on both sides.
2. **Confirm compute support on every shipping platform:** `SystemInfo.supportsComputeShaders` against the project's device floor.
   - **Buffer feeding a vertex shader:** also check `SystemInfo.maxComputeBufferInputsVertex > 0` (many GLES devices report 0).
   - **Uncertain:** design the fallback now, because a compute-only effect on unsupported hardware renders nothing.
3. **One job per kernel:** Emit, Simulate, Sort, Compact (`csharp-standards` → `coding-principles.md` "SOLID"); separate kernels profile independently.
4. **Derive the dispatch from the live element count and bounds-check in the kernel:** `Mathf.CeilToInt(count / (float)groupSize)` rounds up, so the last group runs threads with no element.
   - **Kernel guard:** add `if (id.x >= count) return;`.
   - **Group count:** never hardcode it.
5. **Choose `[numthreads]` against the target and state it:** 64 suits AMD wavefronts, 32 NVIDIA warps, 64-256 is usual on mobile.
6. **Ping-pong any buffer a pass both reads and writes in one dispatch:** parallel threads are unordered, so in-place read-modify-write is a race.
   - **Order:** read one buffer, write the other, swap after.
7. **Keep GPU results out of gameplay decisions:** rules live in a Core assembly and the server evaluates them independently (`csharp-standards` → `coding-principles.md` "Shared Core integrity").
   - **Rule needing the same data:** compute it on the CPU too and treat the GPU copy as presentation.
8. **Read back with `AsyncGPUReadback`, never a blocking `GetData` in a frame path:** `GetData` stalls the CPU on the GPU queue.
   - **Async result:** arrives a frame or more late, so the consumer must tolerate delay by design.
9. **Feed rendering through an indirect draw:** `Graphics.RenderPrimitivesIndirect` or `Graphics.RenderMeshIndirect` with a `GraphicsBuffer` (`DrawMeshInstancedIndirect` is obsolete).
   - **Args buffer:** filled from a GPU counter, so the CPU never reads back just to count.
10. **Release every `ComputeBuffer` on every path:** `OnDisable`/`OnDestroy`, early returns.
    - **Why:** it is native memory the GC never reclaims and it outlives the scene (`csharp-standards` → `performance-and-algorithms.md` "Memory discipline").
11. **Validate at about a hundred elements:** use the Frame Debugger or a graphics inspector before scaling.
    - **Why:** stride and bounds bugs invisible there are obvious at ten thousand.
12. **State the per-frame dispatch cost when non-trivial:** elements × kernel complexity.
    - **Performance claim:** back it with a capture (`csharp-standards` → `performance-and-algorithms.md` "Verification").
13. **Split a request that mixes a visual outcome with raw throughput:** say which half is which and coordinate with `gameplay-engineer` rather than owning both.

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
```

## Example
- **"Read particle positions back each frame so gameplay can detect projectile hits":** declined.
  - **Why:** blocking `GetData` stalls the CPU, `AsyncGPUReadback` is at least a frame late, and a hit is a game rule that lives in a Core assembly where the server evaluates it.
  - **Did instead:** kept the hit test on the CPU against authoritative projectile state; the compute pass drives only the visual trail.
