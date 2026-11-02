---
name: render-pipeline-urp-hdrp
description: "Active render pipeline (URP, HDRP, Built-in) per quality level. Use first in any rendering, shader or post task."
user-invocable: false
---

# Render Pipeline Targeting

- **Not for:** URP Renderer Features, rendering paths, camera stacking (`unity-urp-rendering`).
- **Not for:** HDRP Frame Settings, Volumes, Custom Passes, Water, ray tracing config (`unity-hdrp-rendering`).
- **Not for:** shader node/HLSL content (`shader-authoring`).
- **Not for:** particle graphs (`vfx-particle-authoring`).
- **Not for:** compute kernels (`compute-shader-vfx`).
- **Not for:** entity rendering (`unity-entities-graphics`), which narrows this answer to URP Forward+ or HDRP.
- **Not for:** post-process authoring (`unity-post-processing`).
- **Not for:** lighting and baking (`unity-lighting`).
- **Companion:** if the Unity plugin is installed, `unity:migrate-birp-to-urp` carries out a Built-in → URP migration once it is approved.
  - **Ownership:** this skill still owns the decision and the HDRP side.

## Steps
1. **Read the pipeline off the project, never the request:** open Graphics Settings, name the assigned Render Pipeline Asset.
   - **Tech Spec naming a pipeline:** a claim to verify.
2. **Check every quality level for an override:** Quality Settings can assign a different Render Pipeline Asset per level, taking precedence over the Graphics default.
   - **Confirming Graphics alone:** validates a whole tier against the wrong pipeline.
3. **An existing project's pipeline is settled unless a migration is explicitly funded:** materials, shaders, lighting and post stacks are authored per pipeline and do not carry across.
   - **Switch:** content re-authoring, not a settings change.
   - **Request that implies a switch:** state that cost and route the decision to `cto`; do not start the switch.
4. **Open choice: decide on platform scope first:** HDRP is PC/console class and does not target mobile; URP covers mobile through console.
   - **Fidelity:** second, and never overrides platform scope; an unsupported platform is an exclusion, not a trade-off.
5. **Name the master stack:** `shader-authoring` needs it.
   - **URP:** Universal Lit, Unlit, Sprite-Lit.
   - **HDRP:** Lit, Unlit, Decal, Fabric, Hair, StackLit.
6. **Confirm each requested high-fidelity feature exists on the target before it enters a Tech Spec:**
   - **HDRP-only (PC/console class):** ray tracing, path tracing, volumetric fog/clouds and the Water System.
   - **URP-only:** Forward+.
7. **Dual-pipeline support = separate per-pipeline assets:** graphs sharing subgraphs.
   - **No pipeline branches:** not `#if UNIVERSAL_PIPELINE`/`#if HDRP` branches in one HLSL file (platform branches rule, `coding-principles.md` → Performance discipline).
   - **Cost:** dual-pipeline support doubles authoring and verification cost; confirm it is required.
8. **Hand off target, platform scope and master stack together:** a partial handoff makes the next skill re-derive the pipeline.
9. **Missing input:** Graphics Settings and Tech Spec disagree → dispatched agent `Blocked` or `Needs-decision`; main session `AskUserQuestion`.
   - **Likelier one:** never pick it (stale spec or misconfigured project); a person decides.

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

## Example
- **"Ray-traced reflections in the boss arena: switch to HDRP, it's just a settings change":** declined the framing.
  - **Why:** every material, shader and post profile is URP-authored, and the project ships mobile, which HDRP does not target.
  - **Did instead:** reported both, routed to `cto`, offered a URP screen-space reflection approximation.
