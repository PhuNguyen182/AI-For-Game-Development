# Sprite Atlas

Sources: https://docs.unity3d.com/Manual/sprite/atlas/atlas-landing.html, https://docs.unity3d.com/Manual/sprite/atlas/create-sprite-atlas.html, https://docs.unity3d.com/Manual/sprite/atlas/master-variant/master-variant-sprite-atlases.html, https://docs.unity3d.com/Manual/sprite/atlas/distribution/load-sprite-atlas-spriteatlasmanageratlasrequested.html, https://docs.unity3d.com/Manual/sprite/atlas/sprite-atlas-reference.html, `UnityEngine.U2D.SpriteAtlas` / `SpriteAtlasManager` scripting API

## Why

A Sprite Atlas packs multiple source textures into one combined texture, so every sprite drawn from it can batch into a single GPU draw call instead of one draw call per distinct source texture — the direct fix for the "reduce draw calls" rule in `performance-and-algorithms.md`'s Rendering & draw calls section for any scene with many small distinct sprite textures (UI icons, particle sprites, tile sets).

## Creating one

1. **Assets > Create > 2D > Sprite Atlas** — creates a `.spriteatlasv2` asset (Sprite Atlas V2 is the current default format; V1 is legacy).
2. Before packing, prepare source sprites: disable **Read/Write** on each (unless a script genuinely needs CPU pixel access), and enable **Tight Packing** to reduce transparent-pixel waste in the packed layout.
3. Select the atlas asset, drag sprites/textures/folders onto **Objects for Packing** (or use its **+** button).
4. Click **Pack Preview** to visualize the packed result; for sprites with [secondary textures](secondary-textures.md), use the preview's dropdown to inspect the packed normal/mask maps too — verify every sprite going into one atlas has a matching secondary-texture count first, a mismatch is a common packing error.

Once packed, sprites referencing atlas-packed textures automatically resolve through the atlas at both edit-time and runtime — no code change needed for the common case.

## Inspector properties

| Property | Description |
|---|---|
| Type | **Master** (default — owns its own Objects for Packing list) or **Variant** (derives its sprite set from a Master Atlas at a different resolution, no independent packing list). |
| Master Atlas | The parent atlas (Variant only). |
| Scale | Resolution multiplier relative to the Master (Variant only, max 1.0) — e.g. 0.5 packs a half-resolution texture for the same sprite set. |
| Include in Build | Whether the atlas is bundled and loaded automatically at startup, vs. requiring manual runtime loading (see Late binding below). |
| Allow Rotation | Lets the packer rotate sprites for tighter packing efficiency. |
| Tight Packing | Packs by each sprite's actual mesh/outline shape rather than its bounding rectangle. |
| Padding | Pixel spacing between packed sprites (default 4) — too little risks bleeding between adjacent sprites when filtered. |
| Alpha Dilation | Expands edge colors into transparent pixels, matching the "Alpha Is Transparency" import setting's purpose but at the atlas level. |
| Read/Write, Generate Mip Maps, sRGB, Filter Mode, Aniso Level | Same meaning as the equivalent [texture import settings](import-settings.md), applied to the combined atlas texture. |
| Max Texture Size, Format, Compression, Use Crunch Compression, Compressor Quality | Combined-texture compression controls, with per-platform override tabs — same "set deliberately per platform" discipline as any other texture per `performance-and-algorithms.md`. |

## Master/Variant atlases

Use a **Variant** to ship a lower-resolution version of the same sprite set for a constrained platform (typically mobile) while keeping a full-resolution **Master** for desktop/high-end targets — set the Variant's **Scale** below 1.0 rather than maintaining two entirely separate atlases with duplicated Objects for Packing lists.

By default Unity may include both Master and Variant in a build, which can produce unpredictable results if both are loadable simultaneously — control this deliberately: either disable **Include in Build** on the Master so only the Variant resolves at runtime, or resolve the desired atlas explicitly via `SpriteAtlas.GetSprite`/`GetSprites` in code rather than leaving it to chance.

## Runtime / late-bound loading

When **Include in Build** is off, an atlas must be bound manually via `SpriteAtlasManager.atlasRequested`:

```csharp
private void OnEnable()
{
    SpriteAtlasManager.atlasRequested += this.OnSpriteAtlasRequested;
}

private void OnDisable()
{
    SpriteAtlasManager.atlasRequested -= this.OnSpriteAtlasRequested;
}

private void OnSpriteAtlasRequested(string atlasTag, Action<SpriteAtlas> callback)
{
    SpriteAtlas atlas = Resources.Load<SpriteAtlas>(atlasTag);
    callback(atlas);
}
```

The same pattern applies loading from an Addressable/AssetBundle instead of `Resources` — resolve the atlas by whatever asset-loading mechanism the project uses (see `performance-and-algorithms.md`'s Addressables guidance for load/release discipline), then invoke the callback with the result. Per `coding-principles.md`'s Event handlers rule, subscribe/unsubscribe `atlasRequested` with a named method in `OnEnable`/`OnDisable`, not an inline lambda that can't be unsubscribed.

## Scripting API surface

| Member | Description |
|---|---|
| `SpriteAtlas.spriteCount` | Number of sprites packed into the atlas. |
| `SpriteAtlas.isVariant` | Whether this atlas is a Variant. |
| `SpriteAtlas.tag` | The atlas's tag identifier. |
| `SpriteAtlas.GetSprite(string name)` | Returns a clone of the named packed sprite. |
| `SpriteAtlas.GetSprites(Sprite[] buffer)` | Fills a buffer with clones of every packed sprite. |
| `SpriteAtlas.CanBindTo(Sprite sprite)` | Whether a given sprite belongs to this atlas. |
| `SpriteAtlasManager.atlasRequested` | Static event fired when a sprite needs an atlas that isn't currently loaded/bound — the late-binding hook above. |

## Practical guidance

- Group sprites into an atlas by **what's likely to be on screen together** (a UI screen's icon set, one character's part sheet) — an atlas mixing unrelated content wastes GPU memory keeping the whole combined texture resident for a scene that only needs a fraction of it.
- `GetSprite`/`GetSprites` return **clones**, not the original packed `Sprite` reference — don't assume reference equality against a scene-authored `Sprite` field when comparing against an atlas-fetched one.
