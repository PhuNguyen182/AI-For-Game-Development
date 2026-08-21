# Secondary Textures — `_NormalMap` and `_MaskTex` Binding

Source: [Secondary Textures tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/secondary-textures-editor-reference.html).
Covers: SKILL.md §4 — **"Name a secondary texture exactly `_NormalMap` or `_MaskTex`"**.

Secondary textures attach up to eight extra textures to a sprite alongside its
colour texture, and are looked up **by property name** from the shader. That
name is the whole contract: it is the difference between working 2D
normal-mapped lighting and a completely silent no-op. Setting up the `Light2D`
rig that consumes them belongs to `unity-urp-rendering`.

## Attaching one

| Step | What it decides | Source |
|---|---|---|
| Add (+) in the Secondary Textures module | Creates an entry; up to 8 per sprite | [Secondary Textures tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/secondary-textures-editor-reference.html) |
| Texture slot | The map itself, assigned by drag or picker | [Secondary Textures tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/secondary-textures-editor-reference.html) |
| Name | Must be `_NormalMap` for a normal map or `_MaskTex` for a lighting mask — the URP 2D lit shaders look up exactly these names. Any other name binds nothing, errors nothing, and lights nothing; custom names work only for a shader that declares that property | [Secondary Textures tab reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/secondary-textures-editor-reference.html) |
| Apply | Commits the entry to the texture's import settings | [Sprite Editor window reference](https://docs.unity3d.com/Manual/sprite/sprite-editor/sprite-editor-window-reference.html) |

**Critical caveat**: every sprite packed into one atlas must carry the *same
number* of secondary textures. A mismatch inside a single atlas is a pack-time
failure, so verify counts across the set before packing per
[sprite-atlas.md](sprite-atlas.md).
