# Sprite Import Settings

Texture Type **Sprite (2D and UI)** exposes these. Import settings are asset metadata shared by every instance. Page: https://docs.unity3d.com/Manual/texture-type-sprite.html

| Setting | Decision |
|---|---|
| Sprite Mode | **Single** whole texture; **Multiple** sheet cut in the Sprite Editor (only mode with per-sub-sprite rect/pivot/border); **Polygon** clipped to a polygon |
| Pixels Per Unit | Texture pixels per world unit. Sets rendered size and physics-shape scale; changing it after colliders are tuned rescales every derived hitbox |
| Mesh Type | **Full Rect** quad, mandatory for 9-slicing; **Tight** mesh from alpha cuts overdraw but cannot 9-slice. Forced Full Rect under 32×32 |
| Extrude Edges | Padding around the mesh; raise when a filtered/scaled sprite bleeds at the edge |
| Pivot | Preset or Custom X/Y; Single mode only (Multiple sets it per sprite in the Sprite Editor) |
| Generate Physics Shape | Auto-traces a collision outline when no Custom Physics Shape exists; off for decorative sprites |
| sRGB | On for display colour; off for linear data (mask, data) or values gamma-shift |
| Alpha Source / Alpha Is Transparency | Where alpha comes from (None, Input Texture Alpha, From Gray Scale); Alpha Is Transparency dilates edge colour, fixing dark fringing |
| Read/Write | CPU pixel access, doubles texture memory; on only if a script reads pixels |
| Generate Mip Maps | Only for sprites scaled significantly in perspective; on fixed-scale pixel art it blurs and adds a third more memory |
| Filter Mode | **Point** for crisp pixel art (stays sharp at non-integer scales); Bilinear/Trilinear for smooth art |
| Wrap Mode | Repeat/Clamp/Mirror per axis; matters for Tiled Draw Mode |
| Non-Power of 2 | Handling of NPOT sizes; relevant when the target compression needs POT |
| Max Size / Format / Compression / Compressor Quality | Largest lever on sprite memory. Set per platform via override tabs, never one default for PC and mobile |
