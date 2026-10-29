# Sprite Atlas

Pages: https://docs.unity3d.com/Manual/sprite/atlas/atlas-landing.html, https://docs.unity3d.com/Manual/sprite/atlas/sprite-atlas-reference.html

Sprites from one atlas batch into one draw call, but an atlas is resident as a unit, so mixing unrelated content trades draw calls for unused memory. Once packed, sprites resolve through the atlas automatically; the common case needs no code.

## Creating

- Assets > Create > 2D > Sprite Atlas makes a `.spriteatlasv2` (V2 current, V1 legacy).
- Objects for Packing takes sprites, textures or folders; a folder keeps picking up new art, which can make the atlas unbounded.
- Pack Preview shows the layout and (dropdown) packed secondary textures, catching a count mismatch before it fails.

## Properties

| Property | Decision |
|---|---|
| Type | **Master** owns the packing list; **Variant** derives from a Master at another resolution |
| Master Atlas / Scale | Scale is capped at 1.0; 0.5 packs a half-resolution set without duplicating the list |
| Include in Build | Ships and loads automatically vs must be bound at runtime. On for both Master and Variant makes resolution non-deterministic; disable it on the Master |
| Allow Rotation | Off for sprites re-meshed or laid out by rect downstream (UI `Image`, Sprite Shape) |
| Tight Packing | Packs by mesh outline, saves space, makes `Sprite.textureRect` invalid |
| Padding | Default 4 px; too little bleeds neighbours under filtering |
| Alpha Dilation | Atlas-level equivalent of Alpha Is Transparency |
| Read/Write, Mip Maps, sRGB, Filter Mode | Same meaning as import-settings.md, on the combined texture |
| Max Texture Size, Format, Compression, Crunch | Per-platform override tabs; one big texture, so these decide more memory than any source texture |

## Late binding

With Include in Build off, supply the atlas through `SpriteAtlasManager.atlasRequested`. Subscribe with a named method and unsubscribe in `OnDisable`:

```csharp
private void OnEnable() { SpriteAtlasManager.atlasRequested += this.OnSpriteAtlasRequested; }
private void OnDisable() { SpriteAtlasManager.atlasRequested -= this.OnSpriteAtlasRequested; }

private void OnSpriteAtlasRequested(string atlasTag, Action<SpriteAtlas> callback)
{
    callback(Resources.Load<SpriteAtlas>(atlasTag));
}
```

Resolve by Addressables or AssetBundle the same way, then invoke the callback.

## Scripting

| Member | Note |
|---|---|
| `SpriteAtlas.GetSprite(string)` / `GetSprites(Sprite[])` | Return **clones**: `==` against a scene-authored `Sprite` fails and each call allocates |
| `SpriteAtlas.CanBindTo(Sprite)` | Correct membership test (equality is not) |
| `spriteCount`, `isVariant`, `tag` | Packed count, Variant flag, tag passed to `atlasRequested` |
