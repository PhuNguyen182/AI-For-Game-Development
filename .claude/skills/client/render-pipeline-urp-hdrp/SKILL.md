---
name: render-pipeline-urp-hdrp
description: >
  Decision gate for which Scriptable Render Pipeline a project targets and
  which one is actually active: URP versus HDRP versus the legacy Built-in
  pipeline, the Render Pipeline Asset in Graphics Settings and the
  per-quality-level override that can replace it, Shader Graph master-stack
  targets, platform scope, and pipeline migration cost. Use before any
  pipeline-dependent shader, VFX, render pass, or lighting work, and to
  resolve which pipeline is active.
  Not for: URP Renderer Features, rendering paths, camera stacking
  (`unity-urp-rendering`); HDRP Frame Settings, Volumes, Custom Passes
  (`unity-hdrp-rendering`); shader node or HLSL content (`shader-authoring`);
  particle graph structure (`vfx-particle-authoring`); compute kernels
  (`compute-shader-vfx`); entity rendering (`unity-entities-graphics`).
---

# Render Pipeline Targeting — URP, HDRP & the Built-in Pipeline

## 1. Objective
Establish, with evidence, which render pipeline a project runs before anyone writes something that depends on it — and, when the pipeline is genuinely still open, frame the choice as the hard-to-reverse decision it is. It prevents the failures that look like unrelated bugs later: a shader authored against the wrong master stack that renders magenta, an HDRP-only feature specified for a project that also ships mobile, a pipeline confirmed from Graphics Settings while the active quality level silently overrides it, and a pipeline switch proposed as a settings change when it is in fact a re-authoring of every material in the project.

## 2. Role
Act as the render pipeline targeting gate for the client track — the first stop before any shader, VFX, render pass, or lighting task, and the owner of the URP-versus-HDRP choice itself when it has not yet been made. You settle the target and hand off; you do not configure either pipeline's own systems.

## 3. When to invoke this skill
- Before writing or modifying any shader, VFX, render pass, or lighting setup that behaves differently per pipeline.
- Resolving which pipeline a project is actually on when the answer is assumed rather than checked.
- Deciding URP versus HDRP for a new project, or assessing what changing pipeline would cost on an existing one.
- Confirming whether a requested feature exists at all on the target pipeline and platform scope — ray tracing, volumetric fog, the Water System, Forward+.
- A reported symptom that points at a pipeline mismatch: materials rendering magenta, a Shader Graph that will not compile, an effect that works in one quality level and not another.
- Negative trigger: Renderer Features, rendering paths, the URP Asset, 2D Renderer, camera stacking — that is `unity-urp-rendering`, once URP is confirmed.
- Negative trigger: HDRP Asset and Frame Settings, Volume-driven environment, Custom Pass Volumes, Diffusion Profiles, Water System, ray tracing — that is `unity-hdrp-rendering`, once HDRP is confirmed.
- Negative trigger: the shader's own node graph or HLSL, once the target is settled — that is `shader-authoring`.
- Negative trigger: particle graph and emission structure — that is `vfx-particle-authoring`.
- Negative trigger: a compute kernel driving a visual effect — that is `compute-shader-vfx`.
- Negative trigger: how ECS entities reach the pipeline — that is `unity-entities-graphics`, which depends on this skill's answer and narrows it further to URP Forward+ or HDRP only.

## 4. How to use this skill
1. **Read the pipeline off the project, never off the request** — open Graphics Settings for the assigned Render Pipeline Asset, and state which asset it is. A Tech Spec that names a pipeline is a claim to verify, not evidence.
2. **Check the active quality level for an override before declaring the answer** — Quality Settings can assign a different Render Pipeline Asset per level, which takes precedence over the Graphics default. A project can therefore be on URP in one quality tier and something else in another, and confirming only the Graphics setting is how a whole tier gets validated against the wrong pipeline.
3. **Treat an existing project's pipeline as settled unless someone is explicitly funding a migration** — materials, shaders, lighting setups, and post-process stacks are authored per pipeline and do not carry across, so switching is a content re-authoring project, not a settings change. If a request implies a switch, say what it actually costs and route the decision to `technical-architect` rather than starting it.
4. **When the choice is genuinely open, decide it on platform scope first** — HDRP is PC and console class and does not target mobile; URP covers mobile through console. Fidelity ambition is the second criterion and never overrides the first, because a platform HDRP does not support is not a trade-off, it is an exclusion.
5. **Name the master stack the shader work will target** — Universal Lit, Unlit, or Sprite-Lit for URP; Lit, Unlit, Decal, Fabric, Hair, or StackLit for HDRP. This is the single fact `shader-authoring` needs from this skill, and getting it wrong is what produces a graph that cannot compile against the installed pipeline.
6. **Confirm every requested high-fidelity feature exists on the target before it enters a Tech Spec** — ray tracing, path tracing, volumetric fog and clouds, and the Water System are HDRP-only and PC/console-class; Forward+ is URP-specific. A feature named in a spec that the target pipeline lacks is a scope error found cheapest here.
7. **Keep dual-pipeline support as separate per-pipeline assets, not branches inside one file** — a URP-target graph and an HDRP-target graph sharing subgraphs, rather than one HLSL file threaded with `#if UNIVERSAL_PIPELINE`/`#if HDRP`, per `performance-and-algorithms.md`'s platform-abstraction rule applied to pipelines. Dual support doubles the authoring and verification cost, so confirm it is genuinely required.
8. **Hand off with the target, the platform scope, and the master stack stated together** — an incomplete hand-off is what causes the receiving skill to re-derive the pipeline and sometimes get a different answer.
9. **Ask when Graphics Settings and the Tech Spec disagree** — do not reconcile them by picking the more likely one. A mismatch is either a stale spec or a misconfigured project, and both need a person to say which.

## 5. Specific goals / tasks this skill performs
- Determining and evidencing the active render pipeline, including per-quality-level overrides.
- Making the URP-versus-HDRP choice on platform scope for a project where it is still open.
- Costing a proposed pipeline migration honestly, and routing that decision upward.
- Naming the Shader Graph master stack and platform scope that downstream shader and VFX work must target.
- Confirming a requested feature exists on the target pipeline before it is committed to.
- Deciding whether dual-pipeline support is genuinely required, and structuring it as separate assets.
- Out of scope: URP system configuration (`unity-urp-rendering`); HDRP system configuration (`unity-hdrp-rendering`); shader content (`shader-authoring`); particle graphs (`vfx-particle-authoring`); compute kernels (`compute-shader-vfx`); entity rendering (`unity-entities-graphics`); post-process effect authoring (`unity-post-processing`); lighting and probe baking (`unity-lighting`).

## 6. Output format
```
## Pipeline Targeting — <feature/effect name>
- Decision: URP / HDRP / Built-in / migration required
- Evidence: <Render Pipeline Asset in Graphics Settings, and the quality levels checked for an override>
- Platform scope: <targets this pipeline must serve, and any excluded by it>
- Master stack for shader work: <Universal Lit / HDRP StackLit / ...>
- Feature availability: <each requested feature confirmed present or absent on this target>
- Dual-pipeline support: <required and how it is structured — or "not required">
- Migration cost: <stated if a switch was implied — or "not applicable">
- Routed to: <unity-urp-rendering / unity-hdrp-rendering / shader-authoring / vfx-particle-authoring, with what each was handed>
```

**Extended report — emit ONLY when the requester asks for it.** It adds all three fields:
```
- Known limitations: <what this targeting decision does not cover>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Create a Shader Graph screen-distortion effect for the ultimate ability" on a project described as URP mobile plus PC.
- Output: Decision URP, evidenced by the URP Asset in Graphics Settings and confirmed across both quality levels, neither of which overrides it; master stack Universal Unlit for the distortion sample; platform scope includes mobile, so the effect's instruction cost is a real constraint rather than a PC-class free choice; routed the graph itself to `shader-authoring` and the full-screen injection point to `unity-urp-rendering`, which owns the Renderer Feature.

**Example 2**
- Input: "We want ray-traced reflections in the boss arena — switch the project to HDRP, it is just a settings change."
- Output: declined the framing. The switch is not a settings change: every material, shader, lighting setup, and post-process profile in the project is authored against URP and does not carry across, so this is a content re-authoring effort. The project also ships mobile, which HDRP does not target, so the switch would drop a shipping platform rather than upgrade it. Reported both facts and routed the decision to `technical-architect`; offered a URP-appropriate screen-space reflection approximation as the in-scope alternative.

**Example 3**
- Input: an effect renders correctly in the Editor's default quality level and is magenta on the mobile build.
- Output: traced to a Quality Settings override — the mobile quality level assigns a different Render Pipeline Asset than Graphics Settings, so the material was validated against a pipeline that tier never uses. Confirmed the per-level assignment per §4's override step, restated the target for that tier, and routed the material re-authoring to `shader-authoring` rather than treating it as a build-only bug.

## 8. Edge cases & guardrails
- Never take the pipeline from the request — read it from the project, and say which asset you read.
- Never confirm the pipeline from Graphics Settings alone — a quality level can override it, and that is exactly how one tier gets validated against the wrong pipeline.
- Never describe a pipeline switch as configuration — it re-authors every material and shader in the project, and that decision belongs to `technical-architect`.
- Never specify an HDRP-only feature for a project that ships mobile — HDRP does not target it, so there is no fallback to tune, only a platform to drop.
- Never hand off without the master stack and platform scope — an incomplete hand-off makes the next skill guess the pipeline again.
- Never thread pipeline branches through one shared HLSL file — keep per-pipeline assets, and confirm dual support is actually required before paying for it twice.
- If Graphics Settings and the Tech Spec disagree, stop and ask — one of them is wrong, and guessing which propagates the error into everything downstream.
