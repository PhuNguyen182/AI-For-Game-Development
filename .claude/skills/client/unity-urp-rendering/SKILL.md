---
name: unity-urp-rendering
description: >
  Technique for configuring URP's own systems once URP is the confirmed
  pipeline: `ScriptableRendererFeature` and `ScriptableRenderPass` including
  the Render Graph `RecordRenderGraph` path, the Forward, Forward+, Deferred
  and Deferred+ rendering paths, the URP Asset's render scale, shadow distance
  and cascade settings, SRP Batcher compatibility, Rendering Layers, the 2D
  Renderer and `Light2D`, and camera stacking through
  `UniversalAdditionalCameraData`. Use when URP itself must be configured or
  a pass does not run.
  Not for: which pipeline the project is on (`render-pipeline-urp-hdrp`); HDRP
  (`unity-hdrp-rendering`); shader content (`shader-authoring`); post-process
  effect authoring (`unity-post-processing`); lights, probes and baking
  (`unity-lighting`); plain `Camera` scripting (`unity-camera-fundamentals`);
  entity rendering (`unity-entities-graphics`).
---

# Unity URP Rendering — Universal Render Pipeline Configuration

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | URP manual and API roots plus the version pin | Starting any task here, or confirming which URP version the project installs |
| [renderer-features-and-passes.md](references/renderer-features-and-passes.md) | `ScriptableRendererFeature`, `ScriptableRenderPass`, Render Graph, injection points | Building a custom pass, or an existing one stopped running after an upgrade |
| [rendering-paths.md](references/rendering-paths.md) | Forward, Forward+, Deferred, Deferred+ and what each costs | Choosing a path, or diagnosing a per-object light limit |
| [volumes-and-post-processing.md](references/volumes-and-post-processing.md) | Volume components, profiles, priority and blending | Placing or scoping a Volume — the effect catalog itself is another skill's |
| [2d-renderer.md](references/2d-renderer.md) | `Renderer2DData`, `Light2D`, 2D shadows, Tilemap integration | 2D lighting is expected and may or may not be available |
| [camera-stacking-and-asset-settings.md](references/camera-stacking-and-asset-settings.md) | Camera stacks, `UniversalAdditionalCameraData`, URP Asset settings, Rendering Layers, SRP Batcher | Compositing cameras, or mapping quality settings to device tiers |

## 1. Objective
Configure URP so that what was authored actually runs on the tier it was meant for — the pass registered on the Renderer that tier uses, a rendering path chosen against measured light counts, quality settings mapped to real devices rather than left at template defaults. It prevents the failures URP reports as nothing at all: a Renderer Feature added to the wrong Renderer asset and therefore silently absent, a pass still written against the pre-Render-Graph API that stops executing after an upgrade, 2D lighting expected from a Renderer that is not the 2D Renderer, and a shader assumed SRP Batcher compatible that quietly is not.

## 2. Role
Act as the URP configuration specialist for the client track — the tool reached for once `render-pipeline-urp-hdrp` has confirmed URP and the work is configuring URP's own systems. You own the Renderer, the passes, the paths, and the asset settings; you do not own shader content, post-process effect authoring, or lighting.

## 3. When to invoke this skill
- Building a custom render pass — outline, distortion, custom compositing — as a `ScriptableRendererFeature` enqueuing one or more `ScriptableRenderPass` instances.
- A pass that used to work stops running, or fails after a URP upgrade, because it still uses the pre-Render-Graph execution path.
- Choosing or changing the rendering path for a quality tier, or diagnosing lights that stop affecting an object past a certain count.
- Configuring the 2D Renderer: `Renderer2DData`, `Light2D`, 2D shadows, Tilemap and Sprite lighting integration.
- Setting up camera stacking through `UniversalAdditionalCameraData`, or compositing separately rendered layers.
- Mapping URP Asset settings — render scale, shadow distance, cascade count, per-tier feature toggles — to the project's actual device tiers.
- Confirming SRP Batcher is enabled and that shaders genuinely qualify for it.
- Negative trigger: which pipeline the project runs, or whether it should be URP at all — that is `render-pipeline-urp-hdrp`, whose answer this skill requires as input.
- Negative trigger: any HDRP system — Frame Settings, Custom Pass Volumes, Diffusion Profiles — that is `unity-hdrp-rendering`.
- Negative trigger: the shader's node graph or HLSL — that is `shader-authoring`; this skill decides where its output is injected, not what it computes.
- Negative trigger: authoring a post-process effect, its `VolumeComponent`, or picking from the Bloom-to-Vignette override catalog — that is `unity-post-processing`; this skill owns Volume placement and priority only as pipeline configuration.
- Negative trigger: light setup, probes, lightmapping, or shadow authoring as a lighting problem — that is `unity-lighting`; this skill owns the URP Asset's shadow *settings*, not the lighting design.
- Negative trigger: plain `Camera` or `Transform` scripting with no URP system involved — that is `unity-camera-fundamentals`.
- Negative trigger: how ECS entities reach the renderer — that is `unity-entities-graphics`, which requires the Forward+ path this skill configures.

## 4. How to use this skill
1. **Confirm the URP Asset that the target quality tier actually uses, not just the one in Graphics Settings** — Quality Settings can assign a different asset per level, and every later step in this skill applies to one specific asset. [root-links.md](references/root-links.md) pins the URP version these APIs belong to.
2. **Write custom passes against the Render Graph API**, per [renderer-features-and-passes.md](references/renderer-features-and-passes.md) — in current URP a pass records into the graph via `RecordRenderGraph`, and the older `Execute`-based path survives only behind Compatibility Mode. Per `coding-principles.md`'s Obsolete APIs section, new work targets the current API rather than the compatibility path being kept alive for migration.
3. **Register the feature on the Renderer the target tier actually uses** — a `ScriptableRendererFeature` lives on a specific Renderer asset, so adding it to the default Renderer while a tier references another means it silently never runs for that tier, with nothing logged.
4. **Choose the injection point from what the pass must read** — a pass sampling colour has to run after the content it samples, and one sampling depth after depth is written; picking the event by what the effect should look like rather than by its data dependency is the usual reason a pass renders a frame-old or empty texture.
5. **Choose the rendering path against measured light counts per tier**, per [rendering-paths.md](references/rendering-paths.md) — Forward has a per-object light limit, so extra lights stop affecting an object rather than the scene; Forward+ removes that limit with a screen-space light structure; Deferred trades bandwidth for light-count scalability and gives up MSAA. Back the choice with a Profiler capture per `performance-and-algorithms.md`'s Verification section, never with folklore.
6. **Place Volumes as pipeline configuration and hand the effects to their owner**, per [volumes-and-post-processing.md](references/volumes-and-post-processing.md) — this skill decides Global versus local, priority, and blend distance; which overrides go in the profile and how a custom effect is authored is `unity-post-processing`'s.
7. **Confirm the active Renderer is the 2D Renderer before relying on `Light2D`**, per [2d-renderer.md](references/2d-renderer.md) — 2D lighting exists only under `Renderer2DData`, so a project on the Universal Renderer has none of it, and the components simply do nothing rather than warning.
8. **Composite with a Base plus Overlay camera stack**, per [camera-stacking-and-asset-settings.md](references/camera-stacking-and-asset-settings.md) — `UniversalAdditionalCameraData.cameraStack` is URP's mechanism for layering, and independent full-screen cameras cost a full render each while bypassing it.
9. **Scope light and decal influence with Rendering Layers rather than filtering in a shader** — Rendering Layers are distinct from physics and culling Layers, and they express the intent in the pipeline where it can be seen, rather than hiding it in shader logic.
10. **Verify SRP Batcher compatibility rather than assuming the toggle is enough** — the batcher is enabled on the URP Asset, but a shader only qualifies if its per-material properties sit in the expected constant-buffer layout; confirm the shader side with `shader-authoring` instead of inferring from the setting.
11. **Map every tier-sensitive setting deliberately** — render scale, shadow distance, cascade count, and per-tier feature toggles belong in URP Asset variants per device tier, per `performance-and-algorithms.md`'s platform-abstraction rule; template defaults are a decision nobody made.
12. **Verify on the real tier before claiming completion** — capture the effect on the quality level and device class that actually uses the configured asset, because a pass on the wrong Renderer and a correct one look identical in code.
13. **Ask which tier a change is for when it is unstated** — URP configuration is per-asset, so a change applied to the wrong tier is both invisible where it was wanted and unexplained where it landed.

## 5. Specific goals / tasks this skill performs
- Custom render passes as `ScriptableRendererFeature` plus `ScriptableRenderPass` on the Render Graph API, registered on the correct Renderer.
- Rendering path selection per tier, justified by a Profiler capture.
- 2D Renderer configuration: `Renderer2DData`, `Light2D`, 2D shadows.
- Camera stacking through `UniversalAdditionalCameraData`.
- Rendering Layers for light and decal scoping.
- URP Asset quality-tier mapping and SRP Batcher verification.
- Volume placement, priority, and blend scoping as pipeline configuration.
- Out of scope: pipeline targeting (`render-pipeline-urp-hdrp`); HDRP (`unity-hdrp-rendering`); shader content (`shader-authoring`); post-process effect authoring (`unity-post-processing`); lighting design and baking (`unity-lighting`); plain camera scripting (`unity-camera-fundamentals`); entity rendering (`unity-entities-graphics`).

## 6. Output format
```
## URP Configuration — <feature name>
- URP Asset: <name> — and the quality tiers that reference it
- Renderer asset targeted: <name> — confirmed used by <tiers>
- Pass: <feature and pass names, Render Graph or Compatibility Mode, injection point and the data dependency behind it>
- Rendering path: <Forward / Forward+ / Deferred / Deferred+> — measurement that decided it
- Volumes: <placement, priority, blend distance — effects handed to unity-post-processing>
- 2D Renderer: <Renderer2DData confirmed and Light2D setup — or "not a 2D project">
- Camera stack: <base and overlays — or "single camera">
- Rendering Layers: <what they scope — or "unused">
- SRP Batcher: <enabled, and how shader compatibility was confirmed>
- Tier mapping: <render scale, shadow distance, cascades per tier — or "unchanged, and why">
- Verified on: <quality tier and device class actually captured>
- Layer: <Game.Client.* renderer assets and pass code>
- Known limitations: <...>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what the delivered configuration does not cover>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Add a full-screen outline pass for selected units."
- Output: confirmed both quality tiers reference the same Universal Renderer asset before touching anything; built a `ScriptableRendererFeature` recording through `RecordRenderGraph` rather than the Compatibility Mode `Execute` path, injected after transparents because the pass samples the colour target; registered on that Renderer asset specifically; the outline shader itself handed to `shader-authoring`; captured on both the PC and mobile quality levels rather than only the Editor default.

**Example 2**
- Input: "Lights stop affecting the crowd in the arena — switch the project to Deferred, it handles more lights."
- Output: declined as an unmeasured change. The symptom matches Forward's per-object light limit, which is why individual objects lose lights while the scene looks lit, and Forward+ removes exactly that limit without giving up MSAA, which this project's mobile tier uses. Profiled both paths on a mid-tier Android device under a worst-case light count per `performance-and-algorithms.md`, recommended Forward+ for the mobile tier with the frame-time delta attached, and left the PC tier unchanged since it was never light-bound.

**Example 3**
- Input: after a URP upgrade, a previously working custom blur pass renders nothing, with no errors in the console.
- Output: the feature was still using the pre-Render-Graph `Execute` path, which stops being invoked once Compatibility Mode is off. Ported the pass to `RecordRenderGraph` with its inputs declared to the graph, per §4's Render Graph step and the Obsolete APIs rule, rather than re-enabling Compatibility Mode to defer the work.

## 8. Edge cases & guardrails
- Never register a Renderer Feature without confirming which Renderer asset the target tier uses — the wrong one fails silently and looks correct in code.
- Never keep new passes on the pre-Render-Graph `Execute` path — Compatibility Mode is a migration aid, and per the Obsolete APIs rule new work targets the current API.
- Never pick an injection point by how the effect should look — pick it from what the pass reads, or it samples an empty or stale target.
- Never change the rendering path without a Profiler capture — and never reach for Deferred where the symptom is Forward's per-object limit, which Forward+ solves without losing MSAA.
- Never assume `Light2D` works — it requires `Renderer2DData`, and under the Universal Renderer it does nothing at all.
- Never composite with independent full-screen cameras when a camera stack exists — each extra camera is a full render.
- Never infer SRP Batcher compatibility from the toggle — confirm the shader's constant-buffer layout with `shader-authoring`.
- Never leave tier-sensitive settings at template defaults — they are a decision, and defaults mean nobody made it.
- If the target tier is unstated, ask — a URP change lands on one asset, and the wrong one is invisible where it was wanted.
