# Reflection Probes — Modes, Box Projection, Blending

Sources: [Introduction to Reflection Probes](https://docs.unity3d.com/Manual/ReflectionProbes.html), [Types of Reflection Probe](https://docs.unity3d.com/Manual/RefProbeTypes.html), [Troubleshooting reflections](https://docs.unity3d.com/Manual/AdvancedRefProbe.html), [ReflectionProbe API](https://docs.unity3d.com/ScriptReference/ReflectionProbe.html).
Covers: SKILL.md §4 — **"Choose Reflection Probe mode by whether the reflected content actually changes"**.

A Reflection Probe captures a cubemap from one point and hands it to every
renderer near it. Two consequences follow and cause most of the problems: the
capture is from a **point**, so it is only correct at that point unless box
projection corrects for it, and a realtime capture is six camera renders,
which is a cost the Inspector never displays.

| Mode | What it costs, when it is right | Source |
|---|---|---|
| Baked | Captured at bake time, free at runtime. Correct for anything whose surroundings are static, which is most reflective surfaces in most games | [Types of Reflection Probe](https://docs.unity3d.com/Manual/RefProbeTypes.html) |
| Realtime | Re-renders the scene into six faces. Justified only when the reflected content genuinely changes — moving machinery, a mirror facing the player | [Types of Reflection Probe](https://docs.unity3d.com/Manual/RefProbeTypes.html) |
| Custom | A cubemap supplied by hand, bypassing capture entirely. The cheapest way to art-direct a reflection that need not match the scene | [Types of Reflection Probe](https://docs.unity3d.com/Manual/RefProbeTypes.html) |

## Getting the reflection to sit still

| Setting | What it decides | Source |
|---|---|---|
| `boxProjection` | Reprojects the cubemap onto the probe's box so reflections track the camera correctly inside a bounded space. **Without it, a room's reflection behaves as if infinitely distant** and slides as the camera moves | [Troubleshooting reflections](https://docs.unity3d.com/Manual/AdvancedRefProbe.html) |
| `size` / `center` | The projection box and the probe's zone of influence. A box that does not match the actual room is why box projection sometimes makes things worse rather than better | [Reflection Probe reference](https://docs.unity3d.com/Manual/class-ReflectionProbe.html) |
| `blendDistance` | The fade band where two probes' contributions cross. Zero produces a visible pop as an object crosses the boundary | [Reflection Probe reference](https://docs.unity3d.com/Manual/class-ReflectionProbe.html) |
| `importance` | Which probe wins where zones overlap, before blending applies — the way to nest a small interior probe inside a large exterior one | [ReflectionProbe API](https://docs.unity3d.com/ScriptReference/ReflectionProbe.html) |
| `ReflectionProbeUsage` on the renderer | `Off`, `Simple`, `BlendProbes`, `BlendProbesAndSkybox` — the last is what lets an object fall back to the skybox outside every probe rather than to the nearest one | [ReflectionProbeUsage](https://docs.unity3d.com/ScriptReference/Rendering.ReflectionProbeUsage.html) |

## Realtime cost control

| Setting | What it decides | Source |
|---|---|---|
| `refreshMode` | `OnAwake` captures once — usually what a "realtime" probe actually needed. `EveryFrame` re-renders six faces every frame. `ViaScripting` puts the timing under a `RenderProbe()` call, which is the controlled option | [ReflectionProbeRefreshMode](https://docs.unity3d.com/ScriptReference/Rendering.ReflectionProbeRefreshMode.html) |
| `timeSlicingMode` | Spreads an `EveryFrame` capture across frames — `IndividualFaces` is the gentlest, `NoTimeSlicing` pays the whole cost in one frame and is the usual cause of a periodic hitch | [ReflectionProbeTimeSlicingMode](https://docs.unity3d.com/ScriptReference/Rendering.ReflectionProbeTimeSlicingMode.html) |
| `resolution` / `hdr` | Cubemap face size and format — memory cost is six faces, so a resolution step is a larger jump than it appears | [ReflectionProbe API](https://docs.unity3d.com/ScriptReference/ReflectionProbe.html) |
| `cullingMask` / `shadowDistance` | What the probe's own capture renders. Excluding dynamic objects and shortening its shadow distance cuts capture cost without changing the visible result much | [ReflectionProbe API](https://docs.unity3d.com/ScriptReference/ReflectionProbe.html) |
| `RenderSettings.reflectionBounces` | How many times probes see each other's reflections. Above one requires a re-bake and multiplies bake cost | [RenderSettings](https://docs.unity3d.com/ScriptReference/RenderSettings.html) |
