# Token survival explanations (T3.6 attempt 1)

Run: `token-survival.ps1 -Base bdf5c9ec70bf217ee9ed2763abd75fa4280b717c` with the 14 T3.6 skills. Final output: "TOTAL 14 skill(s), 2196 tokens, 46 missing". The tool printed "0 found only in scripts/" for every skill (no moved code in T3.6). Every miss is explained below.

## Deleted by rule (batch brief "Remove or move"): 22 misses
- `Latent concerns` and `Future remediation` (2 tokens each) in 11 skills: unity-input-system, unity-3d-physics, unity-2d-physics, unity-animation, unity-audio-mixer, unity-cinemachine-authoring, unity-navmesh-navigation, unity-2d-spriteshape, unity-3d-mesh, spine-animation, unity-addressables. The "On request only, add ..." line after `## Output` was deleted in each. (unity-camera-fundamentals, unity-2d-sprite, unity-tilemap had no such line.)
- Also deleted, not flagged by the tool: `Known limitations:` lines inside `## Output` fences (envelope owns them) in all 14 skills, and the `Verified` / `Verification` / `Verified on` / `Verified in Play Mode` / `Verified against` lines in unity-3d-physics, unity-2d-physics, unity-animation, unity-camera-fundamentals, unity-cinemachine-authoring, unity-navmesh-navigation, unity-2d-sprite, unity-3d-mesh, spine-animation, unity-addressables. Domain content in them:
  - unity-3d-physics, unity-2d-physics, unity-animation, unity-navmesh-navigation, unity-2d-sprite, unity-3d-mesh, spine-animation: the measurement is still required by steps 11, 11, 13, 11, 11, 10, 13 (Profiler / Physics Debug / Mesh Preview, "not measured" kept in unity-2d-physics step 11).
  - unity-cinemachine-authoring `Verified in Play Mode`: step 12 keeps the Play Mode check.
  - unity-addressables `Verified against: full content build / Play Mode Scripts only`: step 12 keeps both facts.
  - unity-camera-fundamentals `Verified on: <aspect ratios and device classes actually run>`: no step carried it, so a last step 16 `**Verify on:** the aspect ratios and device classes actually run.` now holds it (brief rule "Verified lines with domain content").
- unity-audio-mixer `Diagnosis: <Audio Profiler evidence ...>` stays in `## Output` (a domain field, not a Verified line).

## Description symbols (frontmatter finished in T2; lost there): 19 misses
The tool printed `symbol [SKILL.md:3]` for slash compounds in the Base description. Each part still appears in the body or references of the same skill:
- unity-input-system `PlayerInput/PlayerInputManager`: `PlayerInput` is in the body (steps 7, 8); `PlayerInputManager` is in `references/player-input-and-multiplayer.md`.
- unity-3d-physics `fixedDeltaTime`, `GameObjects`; unity-2d-physics `GameObjects`: `Time.fixedDeltaTime` is in `references/physics-optimization.md`; the singular `GameObject` is in the references of both skills; the plural token itself no longer appears.
- unity-camera-fundamentals `FOV/orthographicSize`, `follow/shake`: all four words appear in the body (steps 2, 10, 12).
- unity-cinemachine-authoring `Follow/OrbitalFollow/PositionComposer`, `Confiner2D/3D`, `TargetGroup`, `StateDriven/ClearShot`: `CinemachineFollow`, `CinemachineOrbitalFollow`, `CinemachinePositionComposer`, `Confiner2D`, `Confiner3D`, `CinemachineTargetGroup`, `ClearShot` in the body (rename list, steps 7 and 9); `StateDriven` in the references.
- unity-navmesh-navigation `NavMeshSurface/Modifier`: `NavMeshSurface` and `NavMeshModifier` in the body (Docs slugs, step 2).
- unity-tilemap `Rule/Auto/Animated`: `Rule Tile`, `Auto Tile`, `Animated Tile` in step 8 and the Docs line.
- unity-3d-mesh `SetVertices/SetIndices`, `MeshFilter/MeshRenderer`: `SetVertices` in the Example, `SetIndices` in `references/mesh-anatomy.md`, `MeshFilter` in `references/mesh-components.md`, `MeshRenderer` in step 6.
- spine-animation `SkeletonAnimation/SkeletonGraphic/SkeletonMecanim`, `SetSkin/SetupPoseSlots`: all in steps 2 and 4.
- unity-addressables `LoadAssetAsync/InstantiateAsync/LoadSceneAsync`, `Release/ReleaseInstance`, `groups/labels`: `LoadAssetAsync`, `InstantiateAsync`, `LoadSceneAsync` in `references/load-and-release.md`; `ReleaseInstance` in step 5; groups and labels in `references/architecture-and-concepts.md`.

## Bold title changes: 5 misses
The template needs `**Title:**` with the colon inside the bold, so a title with an arrow, a semicolon tail or a long clause changed form. The wording is kept.
- unity-2d-physics step 2 (`bold [SKILL.md:22]`: "Symptom does not name its layer → state the assumption first"): now "Symptom does not name its layer:" with "state the assumption first." after it.
- spine-animation step 1 (`bold [SKILL.md:24]`: "Rendering surface, pipeline or alpha workflow unstated → `Blocked` naming it"): now "Rendering surface, pipeline or alpha workflow unstated:" with "`Blocked` naming it." after it. Step numbers 2 and 7 are unchanged.
- unity-3d-mesh step 5 (`bold [SKILL.md:25]`): title is now "`MarkDynamic` before the first write on a mesh rewritten every frame:" with "never on one that is not" after the colon.
- unity-3d-mesh step 7 (`bold [SKILL.md:27]`) and step 8 (`bold [SKILL.md:28]`): the condition moved after the colon ("by whether runtime code reads or measures the data back", "only when per-object culling can be lost"). No wording lost.
