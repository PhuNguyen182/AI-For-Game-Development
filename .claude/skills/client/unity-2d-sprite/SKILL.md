---
name: unity-2d-sprite
description: >
  Technique for Unity's built-in 2D Sprite authoring pipeline
  (`UnityEngine.Sprite`, `UnityEngine.SpriteRenderer`, `UnityEngine.U2D.*`) —
  Sprite texture import settings (Texture Type, Sprite Mode, Pixels Per
  Unit, Mesh Type, Pivot, Generate Physics Shape), the Sprite Editor's
  modules (slicing/Automatic-Grid-Isometric, Custom Outline render-mesh
  authoring, Custom Physics Shape collision-outline authoring, Secondary
  Textures for normal/mask maps), placeholder sprites, sprite sorting
  (Sorting Layer, Order in Layer, Transparency Sort Mode/Axis, Sorting
  Group), 9-slicing (Border, Sprite Renderer Draw Mode Simple/Sliced/Tiled),
  Sprite Mask, and Sprite Atlas packing (Master/Variant, late binding via
  `SpriteAtlasManager`). Use this for any task touching `Sprite`,
  `SpriteRenderer`, `SpriteMask`, `SortingGroup`, `SpriteAtlas`, the Sprite
  Editor window, or a texture's Sprite import settings. Do not use this for
  2D physics simulation on top of a sprite's physics shape (`Rigidbody2D`,
  `Collider2D` dynamics, joints, effectors) — that's `unity-2d-physics`, a
  separate skill; this skill stops at authoring the physics-shape geometry
  the collider consumes. Do not use this for URP 2D Lighting setup
  (`Light2D`, 2D Renderer Data) that consumes a sprite's secondary
  textures — that's `unity-urp-rendering`. Do not use this for Tilemap or
  Sprite Shape (separate authoring systems built on top of sprites, no
  dedicated skill exists yet in this project — flag as out of scope). Do
  not use this for shader/VFX authoring on sprite materials — that's
  `technical-artist`/`shader-authoring`. Do not use this for gameplay rule
  logic that happens to consume sprite/rendering state (which sprite a
  state machine should show, a hit-flash color decision) — that belongs in
  Shared Core per `coding-principles.md`'s Shared Core integrity rule; this
  skill only covers wiring the Unity-side sprite components themselves.
---

# Unity 2D Sprite — Built-in Sprite Import, Sprite Editor, Rendering & Atlas Pipeline

Sources: see [references/](references/) for the Unity Manual root links, split by topic — [root-links.md](references/root-links.md), [placeholder-sprites.md](references/placeholder-sprites.md), [import-settings.md](references/import-settings.md), [sprite-editor.md](references/sprite-editor.md), [custom-outline.md](references/custom-outline.md), [custom-physics-shape.md](references/custom-physics-shape.md), [secondary-textures.md](references/secondary-textures.md), [sorting-sprites.md](references/sorting-sprites.md), [nine-slicing.md](references/nine-slicing.md), [sprite-mask.md](references/sprite-mask.md), [sprite-atlas.md](references/sprite-atlas.md), [sprite-renderer.md](references/sprite-renderer.md), [sprite-asset-reference.md](references/sprite-asset-reference.md).

## 1. Objective
Configure Unity's built-in 2D Sprite pipeline correctly — right import settings for a texture's role, right Sprite Editor module output (slice/outline/physics-shape/secondary-texture), right sorting/masking/9-slicing setup for the visual requirement, right Sprite Atlas packing for draw-call efficiency — without drifting into 2D physics simulation, URP lighting, Tilemap/Sprite Shape, shader authoring, or gameplay rule logic that belong to sibling skills or roles.

## 2. Role
Act as the built-in 2D Sprite authoring specialist: given a need for sprite import configuration, mesh/collision-outline authoring, sorting/masking/9-slicing, or atlas packing, you choose and configure the right `UnityEngine`/`UnityEngine.U2D`-namespace settings and components — you don't decide gameplay outcomes from sprite/rendering state (that's Shared Core's job), you don't configure `Rigidbody2D`/`Collider2D`/joints/effectors (that's `unity-2d-physics`), and you don't reach into 2D lighting, Tilemap/Sprite Shape, or shader/VFX authoring, which are sibling skills'/roles' territory.

## 3. When to invoke this skill
- Setting a texture's **Sprite import settings** — Texture Type, Sprite Mode (Single/Multiple/Polygon), Pixels Per Unit, Mesh Type (Full Rect/Tight), Pivot, Extrude Edges, Generate Physics Shape, or platform-specific compression overrides.
- Using the **Sprite Editor** to slice a spritesheet (Automatic/Grid By Cell Size/Grid By Cell Count/Isometric Grid), author a render-mesh **Custom Outline**, author a **Custom Physics Shape** outline, or attach **Secondary Textures** (normal/mask maps).
- Adding **placeholder sprites** to block out a scene before final art exists.
- Configuring **sprite sorting** — Sorting Layers, Order in Layer, Transparency Sort Mode/Axis, or a `SortingGroup` to keep a multi-part object's renderers from being interleaved.
- Setting up **9-slicing** — a sprite's Border and a `SpriteRenderer`'s Draw Mode (Sliced/Tiled) and Tile fill mode.
- Adding a **`SpriteMask`** to hide/reveal parts of other sprites, and setting a `SpriteRenderer`'s Mask Interaction.
- Packing sprites into a **Sprite Atlas** (Master/Variant, Include in Build, late-binding via `SpriteAtlasManager.atlasRequested`).
- Configuring a **`SpriteRenderer`**'s Color/Flip/Draw Mode/Material/sorting fields, or reading `Sprite` scripting API data (`rect`, `pivot`, `bounds`, `border`, `GetPhysicsShape`).
- Negative trigger: configuring `Rigidbody2D`, `Collider2D` (beyond authoring the sprite-side physics-shape outline it can consume), 2D joints, or 2D effectors — that's `unity-2d-physics`, a separate skill despite consuming this skill's output.
- Negative trigger: setting up `Light2D`, 2D Renderer Data, or any lighting-side consumption of a sprite's secondary textures — that's `unity-urp-rendering`.
- Negative trigger: Tilemap or Sprite Shape authoring — separate systems built on top of sprites; no dedicated skill exists yet in this project, flag explicitly as out of scope rather than guessing at a workflow.
- Negative trigger: shader/VFX work on sprite materials — that's `technical-artist`/`shader-authoring`.
- Negative trigger: the actual gameplay decision that happens to be expressed through a sprite change (a state machine picking which frame/sprite to show, a damage-flash trigger condition) — that's `csharp-engineer`'s Shared Core, per `coding-principles.md`'s Shared Core integrity rule; this skill stops at wiring the already-decided sprite/color/visibility onto the Unity-side renderer.

## 4. How to use this skill
1. **Confirm scope first.** This skill is the built-in Sprite authoring pipeline (import settings, Sprite Editor modules, `SpriteRenderer`, `SpriteMask`, `SortingGroup`, `SpriteAtlas`). If the task is 2D physics simulation, hand off to `unity-2d-physics`. If it's 2D lighting, hand off to `unity-urp-rendering`. If it's Tilemap/Sprite Shape, state explicitly that no dedicated skill covers it yet rather than improvising a workflow from this skill's scope.
2. **Set import settings deliberately**, per [import-settings.md](references/import-settings.md): Sprite Mode by whether the texture is a single sprite or a spritesheet, Pixels Per Unit consistently within a visual set, Mesh Type by whether 9-slicing is needed (Full Rect required) or overdraw reduction matters more (Tight), and per-platform compression/Max Size overrides per `performance-and-algorithms.md`'s texture-memory-footprint rule — never leave compression at an unexamined default for a shipping platform.
3. **Use the right Sprite Editor module for the job**, per [sprite-editor.md](references/sprite-editor.md): slicing for cutting a spritesheet into sub-sprites, [Custom Outline](references/custom-outline.md) only when a Tight-mesh sprite's transparent padding is significant enough to matter, [Custom Physics Shape](references/custom-physics-shape.md) only when the sprite actually needs `Collider2D` collision derived from its silhouette, [Secondary Textures](references/secondary-textures.md) only when 2D Lighting normal/mask data is actually required — don't author geometry/textures nothing downstream consumes (YAGNI in `coding-principles.md`).
4. **Respect the Shared Core boundary.** Any gameplay decision that happens to manifest as a sprite/color/visibility change (which animation state to show, whether a hit-flash should trigger, a UI state's icon) is decided in `Game.Core.*`; this skill's components only render whatever state Core already resolved — they never decide it themselves, per `coding-principles.md`'s Shared Core integrity rule.
5. **Set sorting deliberately**, per [sorting-sprites.md](references/sorting-sprites.md): explicit Sorting Layer/Order in Layer for anything with a real depth requirement, a `SortingGroup` the moment a multi-part object's renderers must stay visually coherent, `Transparency Sort Mode = Custom Axis` for isometric/top-down cameras — don't rely on default distance-from-camera sorting as a design tool.
6. **Reach for 9-slicing only when a sprite is genuinely resized at runtime or across contexts** ([nine-slicing.md](references/nine-slicing.md)) — a fixed-size sprite doesn't need Sliced/Tiled Draw Mode (KISS in `coding-principles.md`). Choose Sliced for smooth-scaled UI/frames, Tiled for repeating-pattern surfaces.
7. **Use `SpriteMask` only when the design calls for a masked reveal/hide effect** ([sprite-mask.md](references/sprite-mask.md)); verify the active 2D Renderer's Depth/Stencil Buffer is enabled first — the most common reason masking silently does nothing.
8. **Pack a Sprite Atlas** whenever a scene has many small distinct sprite textures likely to be on screen together ([sprite-atlas.md](references/sprite-atlas.md)) — group by co-visibility, use a Variant for a lower-resolution mobile target instead of a duplicated Master, and register `SpriteAtlasManager.atlasRequested` via a named method (unsubscribed in `OnDisable`) rather than a lambda if late-binding an atlas excluded from the build, per `coding-principles.md`'s Event handlers rule.
9. **Configure `SpriteRenderer` deliberately** ([sprite-renderer.md](references/sprite-renderer.md)): cache the component reference outside hot paths, only reassign `sprite`/`color`/sorting fields when the value actually changed (per `performance-and-algorithms.md`'s only-update-on-change rule), and use Flip X/Y instead of a negative Transform scale.
10. **State the hand-off explicitly.** 2D physics simulation on top of authored physics-shape geometry → `unity-2d-physics`. 2D Lighting consuming secondary textures → `unity-urp-rendering`. Tilemap/Sprite Shape → flagged as uncovered, not improvised. Shader/VFX on sprite materials → `technical-artist`/`shader-authoring`. Gameplay decisions behind a sprite/visual change → `csharp-engineer`'s Shared Core.

## 5. Specific goals / tasks this skill performs
- Setting Sprite texture import settings (Sprite Mode, Pixels Per Unit, Mesh Type, Pivot, Generate Physics Shape, platform compression overrides).
- Slicing spritesheets and authoring per-sprite rect/border/pivot data in the Sprite Editor.
- Authoring Custom Outline (render mesh) and Custom Physics Shape (collision outline) geometry.
- Attaching Secondary Textures (normal/mask maps) for downstream 2D Lighting consumption.
- Adding placeholder sprites for pre-art blockout.
- Configuring Sorting Layers, Order in Layer, Transparency Sort Mode/Axis, and Sorting Groups.
- Setting up 9-slicing (Border authoring + Sprite Renderer Draw Mode).
- Adding and configuring Sprite Mask + Mask Interaction.
- Packing, configuring, and runtime-loading Sprite Atlases (including Master/Variant and late binding).
- Configuring Sprite Renderer properties and reading Sprite scripting API data.
- Out of scope: `Rigidbody2D`/`Collider2D`/joint/effector configuration (`unity-2d-physics`); `Light2D`/2D Renderer Data lighting setup (`unity-urp-rendering`); Tilemap/Sprite Shape (uncovered — flag explicitly); shader/VFX authoring (`technical-artist`/`shader-authoring`); gameplay rule logic driving sprite/visual state (`csharp-engineer`'s Shared Core).

## 6. Output format
```
## 2D Sprite Work — <asset/feature name>
- Scope confirmed: built-in Sprite pipeline (not 2D physics simulation, not 2D Lighting, not Tilemap/Sprite Shape)
- Import settings (if applicable): Sprite Mode <Single/Multiple/Polygon>, Pixels Per Unit <n>, Mesh Type <Full Rect/Tight>, Generate Physics Shape <yes/no>, platform overrides <summary>
- Sprite Editor work (if applicable): module(s) used <Slicing/Custom Outline/Custom Physics Shape/Secondary Textures>, key settings, rationale
- Sorting (if applicable): Sorting Layer/Order in Layer, Transparency Sort Mode/Axis, Sorting Group used <yes/no + why>
- 9-slicing (if applicable): Border values, Draw Mode <Sliced/Tiled>, fill mode <Continuous/Adaptive>
- Sprite Mask (if applicable): Mask Source, range scoping <Custom Range summary>
- Sprite Atlas (if applicable): Master/Variant, packing group rationale, Include in Build, late-binding setup <yes/no>
- Sprite Renderer settings: Color/Flip/Draw Mode/Material/Mask Interaction as applicable
- Shared Core boundary: confirmed no gameplay decision made in sprite-layer code
- Hand-off: <physics → unity-2d-physics / lighting → unity-urp-rendering / Tilemap-SpriteShape → flagged uncovered / shader-VFX → technical-artist / gameplay logic → csharp-engineer, as applicable>
- Known limitations: <...>
```

## 7. Examples
**Example 1**
- Input: "Import this 8-frame walk-cycle spritesheet and get it ready for animation, with collision matching each frame's silhouette."
- Output: set Texture Type = Sprite (2D and UI), Sprite Mode = Multiple, Mesh Type = Tight (frames have significant transparent padding), Pixels Per Unit matched to the project's existing character set; sliced the sheet with Grid By Cell Size (uniform frame size) in the Sprite Editor; authored a Custom Physics Shape per frame at moderate Outline Detail (simple silhouette, no need for high fidelity) rather than leaving Generate Physics Shape's auto-outline, since the design wanted a tighter-than-auto-generated hitbox on the character's weapon frames specifically.
- Hand-off: attaching the sliced sprites to an Animator/animation clip and choosing which frame plays when → `csharp-engineer`'s Shared Core (animation-state decision) + `unity-engineer` (Animator wiring); adding the actual `Collider2D`/`Rigidbody2D` that consumes the authored physics shape → `unity-2d-physics`.

**Example 2**
- Input: "A scalable dialogue box UI panel that needs to resize to fit variable-length text, plus batch all the HUD icons into one draw call."
- Output: set the panel sprite's Mesh Type to Full Rect and authored a Border in the Sprite Editor around its frame art; set the panel's Sprite Renderer Draw Mode to Sliced (corners must stay crisp, no repeating pattern needed); created a Sprite Atlas for the HUD icon set, grouped together because they're always on screen simultaneously, with Tight Packing enabled and per-platform Max Size overrides set for the project's PC/mobile targets.
- Hand-off: none for the sprite-layer work itself; the dialogue box's actual resize-to-fit-text logic (computing the target size from text content) → `ui-ux-programmer`, since it's UI layout logic, not sprite authoring.

## 8. Edge cases & guardrails
- Never assume `Rigidbody2D`/`Collider2D`/joint/effector behavior is this skill's territory — this skill only authors the physics-shape *geometry* those components consume; route the component configuration itself to `unity-2d-physics`.
- Never assume `Light2D`/2D Renderer Data lighting setup is this skill's territory, even though it consumes this skill's Secondary Textures output — route that to `unity-urp-rendering`.
- Tilemap and Sprite Shape are separate Unity authoring systems built on top of sprites; this project has no dedicated skill for either yet — state that explicitly rather than trying to stretch this skill's guidance to cover them.
- Never make a gameplay decision (which sprite/frame to show, whether a visual state should trigger) inside sprite-layer code — resolve the decision in Shared Core and let `SpriteRenderer`/`Sprite` code only render whatever state Core already resolved.
- 9-slicing requires **Mesh Type = Full Rect** — Tight mesh type silently breaks it; verify this explicitly rather than assuming any sprite can be 9-sliced.
- A `SpriteMask` that appears to do nothing is very often a Depth/Stencil Buffer disabled on the active 2D Renderer Data asset — check that before assuming the mask setup itself is wrong.
- Don't crank Custom Outline / Custom Physics Shape **Outline Detail** to maximum by default — per `performance-and-algorithms.md`'s hardware-friendly-execution principle, tune it to the lowest detail that still reads correctly; a needlessly detailed physics shape costs more per collision check, and a needlessly detailed render mesh costs more vertices for an imperceptible visual difference.
- **Force Generate All** in either Custom Outline or Custom Physics Shape is destructive to hand-edited geometry across the whole sheet — confirm it's genuinely wanted before using it, don't reach for it as a routine re-sync action.
- Never claim a sprite-related performance improvement (fewer draw calls from atlas packing, reduced overdraw from Tight mesh) without a Profiler measurement (the 2D Profiler module, or the general Unity Profiler) backing it, per `performance-and-algorithms.md`'s Verification section.
- `SpriteAtlas.GetSprite`/`GetSprites` return clones, not the original packed `Sprite` reference — don't assume reference equality when comparing an atlas-fetched sprite against a scene-authored one.
