# Sprite Atlas — Packing, Master/Variant & Late Binding

Sources: [Create a sprite atlas](https://docs.unity3d.com/Manual/sprite/atlas/create-sprite-atlas.html), [Master/variant sprite atlases](https://docs.unity3d.com/Manual/sprite/atlas/master-variant/master-variant-sprite-atlases.html), [Load a sprite atlas at runtime](https://docs.unity3d.com/Manual/sprite/atlas/distribution/load-sprite-atlas-spriteatlasmanageratlasrequested.html), [Sprite Atlas reference](https://docs.unity3d.com/Manual/sprite/atlas/sprite-atlas-reference.html).
Covers: SKILL.md §4 — **"Group an atlas by what appears on screen together"**.

An atlas combines source textures so sprites drawn from it batch into one draw
call, which is the direct application of `performance-and-algorithms.md`'s
Rendering & draw calls section to 2D content. The grouping decision is the
whole skill: an atlas is resident as a unit, so mixing unrelated content trades
draw calls for memory that the scene never uses.

## Creating and packing

| Step | What it decides | Source |
|---|---|---|
| Assets > Create > 2D > Sprite Atlas | Creates a `.spriteatlasv2` asset; V2 is the current format and V1 is legacy | [Create a sprite atlas](https://docs.unity3d.com/Manual/sprite/atlas/create-sprite-atlas.html) |
| Objects for Packing | Sprites, textures, or whole folders — a folder entry keeps picking up new art, which is either convenient or an unbounded atlas depending on the folder | [Create a sprite atlas](https://docs.unity3d.com/Manual/sprite/atlas/create-sprite-atlas.html) |
| Pack Preview | Shows the packed layout, and via its dropdown the packed secondary textures — the check that catches a secondary-texture count mismatch before it fails | [Create a sprite atlas](https://docs.unity3d.com/Manual/sprite/atlas/create-sprite-atlas.html) |

Once packed, sprites resolve through the atlas automatically at edit time and
runtime; the common case needs no code.

## Inspector properties

| Property | What it decides | Source |
|---|---|---|
| Type | **Master** owns a packing list; **Variant** derives its set from a Master at a different resolution and has no list of its own | [Master/variant sprite atlases](https://docs.unity3d.com/Manual/sprite/atlas/master-variant/master-variant-sprite-atlases.html) |
| Master Atlas / Scale | The parent, and a multiplier capped at 1.0 — 0.5 packs a half-resolution set for a constrained target without duplicating the list | [Master/variant sprite atlases](https://docs.unity3d.com/Manual/sprite/atlas/master-variant/master-variant-sprite-atlases.html) |
| Include in Build | Whether the atlas ships and loads automatically, or must be bound at runtime. Leaving it on for both a Master and its Variant makes which one resolves non-deterministic | [Master/variant sprite atlases](https://docs.unity3d.com/Manual/sprite/atlas/master-variant/master-variant-sprite-atlases.html) |
| Allow Rotation | Rotates sprites for tighter packing — must be off for sprites a downstream system re-meshes or lays out by rect, such as UI `Image` or Sprite Shape | [Sprite Atlas reference](https://docs.unity3d.com/Manual/sprite/atlas/sprite-atlas-reference.html) |
| Tight Packing | Packs by mesh outline rather than bounding rect, saving space but making `Sprite.textureRect` invalid — see [sprite-asset-reference.md](sprite-asset-reference.md) | [Sprite Atlas reference](https://docs.unity3d.com/Manual/sprite/atlas/sprite-atlas-reference.html) |
| Padding | Pixels between packed sprites, default 4 — too little bleeds neighbouring sprites into each other under filtering | [Sprite Atlas reference](https://docs.unity3d.com/Manual/sprite/atlas/sprite-atlas-reference.html) |
| Alpha Dilation | Expands edge colour into transparent pixels at atlas level, the same purpose as Alpha Is Transparency on import | [Sprite Atlas reference](https://docs.unity3d.com/Manual/sprite/atlas/sprite-atlas-reference.html) |
| Read/Write, Mip Maps, sRGB, Filter Mode | Same meaning as the per-texture settings in [import-settings.md](import-settings.md), applied to the combined texture | [Sprite Atlas reference](https://docs.unity3d.com/Manual/sprite/atlas/sprite-atlas-reference.html) |
| Max Texture Size, Format, Compression, Crunch | Compression controls with per-platform override tabs — the atlas is one large texture, so these decide more memory than any single source texture did | [Sprite Atlas reference](https://docs.unity3d.com/Manual/sprite/atlas/sprite-atlas-reference.html) |

## Late binding

With Include in Build off, the atlas must be supplied on demand through
`SpriteAtlasManager.atlasRequested`. Subscribe with a named method and
unsubscribe it, per `coding-principles.md`'s Event handlers section.

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

The same shape applies when loading from Addressables or an AssetBundle —
resolve by whichever mechanism the project uses, then invoke the callback.

## Scripting surface

| Member | What it decides | Source |
|---|---|---|
| `SpriteAtlas.GetSprite(string)` | Returns a **clone**, not the packed original — reference comparison against a scene-authored `Sprite` fails, and each call allocates | [Sprite Atlas reference](https://docs.unity3d.com/Manual/sprite/atlas/sprite-atlas-reference.html) |
| `SpriteAtlas.GetSprites(Sprite[])` | Fills a buffer with clones, same caveat at bulk scale | [Sprite Atlas reference](https://docs.unity3d.com/Manual/sprite/atlas/sprite-atlas-reference.html) |
| `SpriteAtlas.CanBindTo(Sprite)` | Whether a sprite belongs to this atlas — the correct membership test, since equality is not | [Sprite Atlas reference](https://docs.unity3d.com/Manual/sprite/atlas/sprite-atlas-reference.html) |
| `SpriteAtlas.spriteCount` / `isVariant` / `tag` | Packed count, Variant flag, and the tag `atlasRequested` passes back | [Sprite Atlas reference](https://docs.unity3d.com/Manual/sprite/atlas/sprite-atlas-reference.html) |
| `SpriteAtlasManager.atlasRequested` | Fires when a sprite needs an atlas that is not bound — the late-binding hook above | [Load a sprite atlas at runtime](https://docs.unity3d.com/Manual/sprite/atlas/distribution/load-sprite-atlas-spriteatlasmanageratlasrequested.html) |
