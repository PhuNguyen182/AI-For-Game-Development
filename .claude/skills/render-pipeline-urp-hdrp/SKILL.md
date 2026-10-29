---
name: render-pipeline-urp-hdrp
description: "Confirm which render pipeline is active (URP, HDRP, Built-in) per quality level and what it limits, before any rendering, shader or post work. Use first in any rendering task."
user-invocable: false
---

# Render Pipeline Targeting

Not for: URP Renderer Features, rendering paths, camera stacking (`unity-urp-rendering`), HDRP Frame Settings, Volumes, Custom Passes, Water, ray tracing config (`unity-hdrp-rendering`), shader node/HLSL content (`shader-authoring`), particle graphs (`vfx-particle-authoring`), compute kernels (`compute-shader-vfx`), entity rendering (`unity-entities-graphics`, which narrows this answer to URP Forward+ or HDRP), post-process authoring (`unity-post-processing`), lighting and baking (`unity-lighting`).
Companion, if the Unity plugin is installed: once a Built-in → URP migration is approved, `unity:migrate-birp-to-urp` carries it out; this skill still owns the decision and the HDRP side.

## Steps
1. **Read the pipeline off the project, never the request** — open Graphics Settings, name the assigned Render Pipeline Asset. A Tech Spec naming a pipeline is a claim to verify.
2. **Check every quality level for an override** — Quality Settings can assign a different Render Pipeline Asset per level, taking precedence over the Graphics default. Confirming Graphics alone validates a whole tier against the wrong pipeline.
3. **An existing project's pipeline is settled unless a migration is explicitly funded** — materials, shaders, lighting and post stacks are authored per pipeline and do not carry across; a switch is content re-authoring, not a settings change. If a request implies one, state that cost and route the decision to `cto`; do not start it.
4. **Open choice: decide on platform scope first** — HDRP is PC/console class and does not target mobile; URP covers mobile through console. Fidelity is second and never overrides this: an unsupported platform is an exclusion, not a trade-off.
5. **Name the master stack** — URP: Universal Lit, Unlit, Sprite-Lit. HDRP: Lit, Unlit, Decal, Fabric, Hair, StackLit. This is what `shader-authoring` needs.
6. **Confirm each requested high-fidelity feature exists on the target before it enters a Tech Spec** — ray tracing, path tracing, volumetric fog/clouds and the Water System are HDRP-only (PC/console class); Forward+ is URP-only.
7. **Dual-pipeline support = separate per-pipeline assets** (graphs sharing subgraphs), not `#if UNIVERSAL_PIPELINE`/`#if HDRP` branches in one HLSL file (platform branches rule, `coding-principles.md` → Performance discipline). It doubles authoring and verification cost; confirm it is required.
8. **Hand off target, platform scope and master stack together** — a partial handoff makes the next skill re-derive the pipeline.
9. **Graphics Settings and Tech Spec disagree → ask**; don't pick the likelier one (stale spec or misconfigured project; a person decides).

## Output
```
## Pipeline Targeting — <feature/effect name>
- Decision: URP / HDRP / Built-in / migration required
- Evidence: <Render Pipeline Asset in Graphics Settings; quality levels checked for override>
- Platform scope: <targets served, and any excluded>
- Master stack for shader work: <...>
- Feature availability: <each requested feature present or absent>
- Dual-pipeline support: <required and structure / not required>
- Migration cost: <stated if a switch was implied / not applicable>
- Routed to: <skill, with what it was handed>
```
On request only, add `Known limitations`, `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Ray-traced reflections in the boss arena: switch to HDRP, it's just a settings change" → declined the framing: every material, shader and post profile is URP-authored, and the project ships mobile, which HDRP does not target. Reported both, routed to `cto`, offered a URP screen-space reflection approximation.
