# Secondary Textures

Source: https://docs.unity3d.com/Manual/sprite/sprite-editor/secondary-textures-editor-reference.html

## Purpose

Secondary textures attach additional per-sprite texture data alongside the base color texture — most commonly a normal map or a lighting mask map, consumed by URP's 2D Renderer/`Sprite-Lit-Default` shader to compute 2D lighting (`Light2D`) against the sprite. Up to 8 secondary textures can be attached per sprite.

## Adding one

1. In the Sprite Editor's **Secondary Textures** module, click **Add (+)**.
2. Assign the texture by dragging it from the Project window or using the picker.
3. Set the **Name** field to the exact name the consuming shader expects — Unity ships two well-known names: `_NormalMap` for a normal map, `_MaskTex` for a lighting mask map. Custom names are supported for shaders/packages that expect a different property name, but the default 2D Lighting shaders specifically look for `_NormalMap`/`_MaskTex`.
4. Click **Apply**.

## Practical guidance

- A secondary texture with the wrong **Name** silently does nothing at runtime — the URP 2D Lighting shader won't find it under the property name it expects. If 2D normal-mapped lighting isn't showing an effect, check this field first.
- Owning the actual `Light2D`/2D Renderer Data/shader-side lighting setup that consumes these secondary textures is `unity-urp-rendering`'s territory — this module only attaches the texture data to the sprite asset.
- When packing sprites into a [Sprite Atlas](sprite-atlas.md), verify every sprite in the atlas has a matching number of secondary textures before packing — a mismatch across sprites in the same atlas is a common, easy-to-miss packing error.
