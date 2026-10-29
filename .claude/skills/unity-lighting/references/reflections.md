# Reflection Probes

Docs: Manual Reflection Probe pages (introduction, types, troubleshooting); API `ReflectionProbe`, `ReflectionProbeRefreshMode`, `ReflectionProbeTimeSlicingMode`, `ReflectionProbeUsage`.

A probe captures a cubemap from one point, so it is correct only there unless box projection corrects it; a realtime capture is six camera renders the Inspector never shows as cost.

| Mode | Use |
|---|---|
| Baked | Free at runtime; right for static surroundings (most surfaces) |
| Realtime | Only when reflected content changes (moving machinery, a mirror facing the player) |
| Custom | Hand-supplied cubemap; cheapest way to art-direct a reflection |

## Stability
- `boxProjection`: without it a room's reflection acts infinitely distant and slides with the camera.
- `size`/`center`: the box and zone of influence; a box not matching the room makes box projection worse.
- `blendDistance`: zero pops at the boundary.
- `importance`: wins in overlaps before blending; nests a small interior probe in a large exterior one.
- `ReflectionProbeUsage` on the renderer: `Off`, `Simple`, `BlendProbes`, `BlendProbesAndSkybox` (the last falls back to skybox outside every probe, not to the nearest).

## Realtime cost
- `refreshMode`: `OnAwake` captures once (often all a "realtime" probe needed); `EveryFrame` re-renders six faces each frame; `ViaScripting` with `RenderProbe()` is the controlled option.
- `timeSlicingMode`: `IndividualFaces` gentlest; `NoTimeSlicing` pays everything in one frame (usual periodic hitch).
- `resolution`/`hdr`: six faces, so a resolution step is a larger jump than it looks.
- `cullingMask`/`shadowDistance` of the capture: drop dynamic objects and shorten shadows to cut cost.
- `RenderSettings.reflectionBounces` above one needs a re-bake and multiplies bake cost.
