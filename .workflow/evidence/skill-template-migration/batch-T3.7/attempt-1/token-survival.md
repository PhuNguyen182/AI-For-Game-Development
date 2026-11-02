# Token survival explanations (T3.7 attempt 1)

Run: `token-survival.ps1 -Base bdf5c9ec70bf217ee9ed2763abd75fa4280b717c` with the 15 T3.7 skills. Final output: "TOTAL 15 skill(s), 1383 tokens, 49 missing". The tool printed "0 found only in scripts/" for every skill (no moved code in T3.7). Per-skill misses: render-pipeline-urp-hdrp 4, unity-urp-rendering 4, unity-hdrp-rendering 4, shader-authoring 3, vfx-particle-authoring 5, compute-shader-vfx 3, unity-lighting 2, unity-post-processing 3, unity-burst-compiler 2, unity-job-system-and-burst 3, unity-collections 4, unity-ecs-architecture 4, unity-entities-graphics 2, unity-mathematics 3, unity-physics 3. The 49 split into 25 deleted by rule, 14 description symbols, 10 bold titles.

## Deleted by rule (batch brief "Remove or move"): 25 misses
- `Latent concerns`, `Future remediation` (2 tokens each, 24 in all) in 12 skills: render-pipeline-urp-hdrp, unity-urp-rendering, unity-hdrp-rendering, shader-authoring, vfx-particle-authoring, compute-shader-vfx, unity-lighting, unity-post-processing, unity-job-system-and-burst, unity-ecs-architecture, unity-entities-graphics, unity-physics. The "On request only, add ..." line after `## Output` was deleted in each. unity-burst-compiler, unity-collections and unity-mathematics had no such line.
- `Known limitations` (1 token) in render-pipeline-urp-hdrp: the same deleted line named it. In the other skills the tool did not flag it, but the `Known limitations: <...>` line inside `## Output` was deleted in all 15 (the envelope owns it).
- Also deleted, not flagged by the tool: `Verified` style lines in `## Output`. The domain content each carried:
  - unity-urp-rendering `Verified on: <quality tier and device class captured>`: step 10 still says capture on the quality level and device class that uses the asset.
  - unity-hdrp-rendering `Verified on`: step 9 keeps "verify on the Asset and hardware tier that ships".
  - shader-authoring `Platforms verified`: step 9 keeps "verify on every platform the Tech Spec targets".
  - vfx-particle-authoring `Verified`: step 10 keeps "watch it play in-engine on the target tier against the real background".
  - unity-lighting `Verified on`: step 12 keeps the measurement (bake time, frame time or memory on the claimed tier).
  - unity-post-processing `Verified`: no step carried the tier and device capture, so a new last step 10 "Verify on the tier and device captured" holds it (brief rule "Verified lines with domain content").
  - unity-ecs-architecture `Verified via` (Hierarchy / Systems window): step 12 keeps both windows.
  - unity-mathematics `Verification: <precision check>`: step 8 keeps the precision check.
- Kept in `## Output` as domain fields, not Verified lines: unity-burst-compiler `Compilation verified` and `Measurement`; unity-job-system-and-burst `Measurement`; unity-entities-graphics `Batching measured`; unity-ecs-architecture `Measurement`; compute-shader-vfx `Platform support` and `Cost`.

## Description symbols (frontmatter finished in T2; lost there): 14 misses
The tool printed `symbol [SKILL.md:3]` for slash compounds in the Base description. Each part still appears in the body or references of the same skill (checked with grep):
- unity-urp-rendering `ScriptableRendererFeature/RenderPass`: `ScriptableRendererFeature` is in the body; `ScriptableRenderPass` is in `references/renderer-features-and-passes.md`. `Forward/Forward` (two tokens printed): `Forward` appears 6 times in the body.
- unity-hdrp-rendering `ray/path`: "ray tracing" and "path tracing" appear in the body.
- vfx-particle-authoring `blend/sorting`: "blend" and "sorting" appear in the body.
- compute-shader-vfx `mesh/vertex`: "mesh deformation" and "Mesh" appear in the body; "Vertex" appears in `maxComputeBufferInputsVertex`.
- unity-post-processing `Volume/VolumeProfile/VolumeComponent`: `Volume` is in the body; `VolumeProfile` and `VolumeComponent` are in the references.
- unity-burst-compiler `FloatMode/CompileSynchronously`: both are in the body.
- unity-job-system-and-burst `IJob/IJobFor/ScheduleParallel`: all three are in the body.
- unity-collections `NativeArray/List/HashMap/Queue/Stream`: `NativeArray`, `NativeList`, `NativeHashMap`, `NativeStream` are in the body; `NativeQueue` is in `references/collection-types.md`. `Temp/TempJob/Persistent/rewindable` and `FixedString/FixedList`: all in the body.
- unity-mathematics `float3/float4x4`: `float3` is in the body; `float4x4` is in `references/vector-and-matrix-types.md`. `Vector3/Mathf/Random`: all three are in the body.
- unity-physics `PhysicsCollider/Velocity/Mass`: `PhysicsCollider` is in the references; `PhysicsVelocity` and `PhysicsMass` are in the body.

## Bold title changes: 10 misses
The template needs `**Title:**` with the colon inside the bold and no `*` inside, so a title with an arrow, a comma tail or a long clause changed form. The wording is kept.
- render-pipeline-urp-hdrp step 9 (`bold [SKILL.md:21]` "Graphics Settings and Tech Spec disagree → ask"): now `Missing input` with the same condition and `Blocked` / `Needs-decision` / `AskUserQuestion` (ask-inventory class Strict, no assumption branch). "Never pick the likelier one (stale spec or misconfigured project); a person decides" is a nested bullet.
- unity-hdrp-rendering step 6 (`bold` "Enable Adaptive Probe Volumes in the Asset, then hand off placement and baking to `unity-lighting`"): title is now "Enable Adaptive Probe Volumes in the Asset:" with "then hand off placement and baking to `unity-lighting`." after the colon. Step 7 "scope unstated → ask" moved to a new last step 10 `Missing input` (ask-inventory class Missing input).
- shader-authoring step 7 (`bold` "Transform to world space only where the effect needs it"): now "World space: transform only where the effect needs it." The title text changed; the sentence is otherwise the same. Step 10 "ask for a reference image..." became `Missing input` (class Strict), naming the reference image, comparable or parameter.
- vfx-particle-authoring step 6 (two `bold` misses "VFX Graph: size Capacity to the real peak", "set bounds to cover where particles travel"): now "VFX Graph Capacity and bounds:" with nested `Capacity:` "size it to the real peak, because it pre-allocates GPU memory" and `Bounds:` "set them to cover where particles travel, because default bounds cull the effect when its origin leaves the frustum".
- unity-burst-compiler step 8 (`bold` "Use `FunctionPointer<T>` / `SharedStatic<T>` only where required"): now "`FunctionPointer<T>` / `SharedStatic<T>`: use only where required."
- unity-collections step 1 (`bold` "Confirm access pattern, boundary and data lifetime; if any is unstated, ask"): the "ask" half moved to a new last step 10 `Missing input` (class Strict, "guessing picks the wrong container" kept); step 1 now reads "Confirm access pattern, boundary and data lifetime:".
- unity-ecs-architecture step 12 (two `bold` misses "Confirm the built layout in `Window > Entities > Hierarchy`", "and `Window > Entities > Systems`"): now "Confirm the built layout before claiming it:" with the two windows as nested titled bullets; both window paths are in the body.
- unity-mathematics step 9 (`bold` "Layer or seed origin unstated → ask before writing"): now `Missing input` with the same condition and `Blocked` / `Needs-decision` / `AskUserQuestion`, "before writing" kept (class Strict).

Count: 1 + 1 + 1 + 2 + 1 + 1 + 2 + 1 = 10. Total 25 + 14 + 10 = 49.

## Other notes
- unity-urp-rendering: the `Ask which tier a change is for when unstated` sentence in step 1 moved to a new last step 11 `Missing input` (class Missing input). Its text has no separate token miss.
- Step numbers: shader-authoring 3, 4, 9 and compute-shader-vfx 10 (the anchored steps) keep their numbers and subjects.
