# Reflections

Covers reflection techniques in Unity — Reflection Probes (baked, realtime, custom), placement and blending, box projection, and performance — plus how URP resolves and blends probe contributions per GameObject.

## Manual — General
- [Reflections](https://docs.unity3d.com/6000.5/Documentation/Manual/reflections-landing.html)
- [Introduction to Reflection Probes](https://docs.unity3d.com/6000.5/Documentation/Manual/ReflectionProbes.html)
- [Types of Reflection Probe](https://docs.unity3d.com/6000.5/Documentation/Manual/RefProbeTypes.html)
- [Place a Reflection Probe](https://docs.unity3d.com/6000.5/Documentation/Manual/UsingReflectionProbes.html)
- [Add GameObjects to reflections](https://docs.unity3d.com/6000.5/Documentation/Manual/ReflectionProbes-set-gameobjects.html)
- [Set GameObjects to use Reflection Probes](https://docs.unity3d.com/6000.5/Documentation/Manual/ReflectionProbes-set-gameobjects-use.html)
- [Enable reflections of reflections](https://docs.unity3d.com/6000.5/Documentation/Manual/ReflectionProbes-EnableReflectionsOfReflections.html)
- [Optimize reflections](https://docs.unity3d.com/6000.5/Documentation/Manual/RefProbePerformance.html)
- [Troubleshooting reflections (Box Projection)](https://docs.unity3d.com/6000.5/Documentation/Manual/AdvancedRefProbe.html)
- [Reflection Probe Inspector window reference](https://docs.unity3d.com/6000.5/Documentation/Manual/class-ReflectionProbe.html)

## Manual — URP
- [Reflections in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/lighting/reflection-probes.html)
- [Reflection Probes in URP](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/lighting/reflection-probes-introduction.html)
- [Troubleshooting reflections (URP)](https://docs.unity3d.com/6000.5/Documentation/Manual/urp/lighting/reflection-probes-troubleshooting.html)

## Scripting API
- [ReflectionProbe](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/ReflectionProbe.html) — key members: `mode`, `refreshMode`, `timeSlicingMode`, `resolution`, `intensity`, `blendDistance`, `boxProjection`, `size`, `center`, `cullingMask`, `hdr`, `importance`, `clearFlags`, `backgroundColor`, `nearClipPlane`, `farClipPlane`, `shadowDistance`, `texture` (read-only); methods `RenderProbe()`, `IsFinishedRendering()`, `Reset()`, `BlendCubemap()`.
- [Rendering.ReflectionProbeMode](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/Rendering.ReflectionProbeMode.html) — enum: `Baked`, `Realtime`, `Custom`.
- [Rendering.ReflectionProbeUsage](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/Rendering.ReflectionProbeUsage.html) — enum: `Off`, `BlendProbes`, `BlendProbesAndSkybox`, `Simple`.
- [Rendering.ReflectionProbeRefreshMode](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/Rendering.ReflectionProbeRefreshMode.html) — enum: `OnAwake`, `EveryFrame`, `ViaScripting`.
- [Rendering.ReflectionProbeTimeSlicingMode](https://docs.unity3d.com/6000.5/Documentation/ScriptReference/Rendering.ReflectionProbeTimeSlicingMode.html) — enum: `NoTimeSlicing`, `AllFacesAtOnce`, `IndividualFaces`.
