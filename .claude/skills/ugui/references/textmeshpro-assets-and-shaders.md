# TextMeshPro — Font Assets, Sprite Assets, Shaders

Source: [Font Asset Creator](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/TextMeshPro/FontAssetsCreator.html), [Sprites](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/TextMeshPro/Sprites.html), [Shaders](https://docs.unity3d.com/Packages/com.unity.ugui@2.6/manual/TextMeshPro/Shaders.html).
Covers: SKILL.md §4 — "Generate font assets with a padding/atlas budget that matches the target effects", "One sprite atlas per text object".

## Font Asset Creator

Converts a source font file into a TMP font asset plus its atlas texture,
via **Window > TextMesh Pro > Font Asset Creator**: import the `.ttf`,
pick it as the source, configure the settings below, **Generate Font
Atlas**, review the preview, then save into a `Resources` folder (TMP
resolves fallback/default assets from `Resources`).

| Setting | Effect |
|---|---|
| Sampling Point Size / Auto Sizing | Auto finds the largest point size that still fits every requested character on the chosen atlas resolution; manual sizing gives pixel-accurate bitmap control instead |
| Padding | Larger padding = smoother SDF gradient and room for thicker outline/glow effects later, at the cost of atlas space — 5px is the documented baseline for a 512×512 atlas |
| Packing Method | **Optimum** (searches for the largest fitting size — slower, better use of atlas space) vs **Fast** (quicker, coarser — fine for iteration) |
| Atlas Resolution | 512×512 is adequate for an ASCII-only font; a larger character set or finer SDF gradient quality needs more |
| Render Mode | **SMOOTH/RASTER** (antialiased/non-antialiased bitmap, no SDF effects available), **SDFAA** (fast, less precise SDF), **SDF8/16/32** (slower, higher-precision SDF via oversampling — needed for large on-screen sizes or heavy outline/glow effects), plus HINTED variants that align to pixel boundaries for crisper small text |
| Character Set | Predefined sets (ASCII, Extended ASCII, Numbers + Symbols, …) or a custom set via decimal ranges, hex Unicode ranges, or literal characters |
| Font Style / Get Kerning Pairs | Bold/Italic/Outline styling (bitmap fonts only); imports kerning pairs from the source font file if it supplies them |

**SDF, never a static/bitmap font asset, for anything that will be scaled,
outlined, or have a glow/underlay effect** — bitmap-rendered text does not
support those shader effects at all, and does not scale cleanly. Pick
Render Mode and Atlas Resolution together against the actual on-screen
sizes and effects the design calls for, rather than leaving the Font Asset
Creator's defaults unexamined.

## Sprite Assets

Inline sprites in text via the `<sprite>` tag. Workflow: set the source
atlas texture's Texture Type to "Sprite (2D and UI)" and Sprite Mode to
"Multiple," slice it in the Sprite Editor, then run `Assets > Create >
TextMesh Pro > Sprite Asset` on that texture (reverting the source
texture's import settings afterward if it's also used elsewhere). Place
sprite assets under a `Resources/Sprites` folder for discovery, and set a
default sprite asset in TMP Settings, or assign one per text object.

**Use one atlas per text object where possible** — the Manual is explicit
that multiple sprite atlases referenced by the same text object cost one
draw call *per atlas*, which defeats the point of batching that object's
own text. A sprite asset also supports fallback sprite assets, searched in
order when a requested sprite isn't found in the primary one.

## Shaders and materials

Each TMP text object's Material determines which shader renders it:

| Shader family | Behavior |
|---|---|
| **Distance Field** | Unlit; supports the full SDF effect set (outline, underlay, glow, bevel) without reacting to scene lighting |
| **Distance Field Overlay** | Same unlit SDF rendering, intended for overlay-style rendering |
| **Distance Field (Surface)** | Reacts to scene lighting via Unity's surface shader framework — more GPU-expensive, use only when text genuinely needs to sit lit within a 3D/World Space scene |
| **Mobile variants** | Lighter-weight versions of the above, at the cost of supporting fewer simultaneous effects — the default choice on constrained hardware |
| **Bitmap-only shaders** | Paired with a non-SDF (SMOOTH/RASTER) font asset — no distance-field effects available at all |

Pick Distance Field (never Surface) for ordinary UI text — Screen Space
canvases aren't lit anyway (per
[canvas-and-scaling.md](canvas-and-scaling.md)), so Surface's lighting
cost buys nothing there. Reserve the Surface variant, and the extra GPU
cost that comes with it, for text genuinely embedded in a lit 3D/World
Space scene.
