# TextMeshPro — Font Assets, Sprite Assets, Shaders

## Font Asset Creator
Window > TextMesh Pro > Font Asset Creator: pick the `.ttf`, configure, Generate Font Atlas, preview, save into a `Resources` folder (TMP resolves fallback/default assets from there).

| Setting | Effect |
|---|---|
| Sampling Point Size | Auto = largest size fitting every character on the atlas; manual = pixel-accurate bitmap control |
| Padding | Larger = smoother SDF and room for thicker outline/glow, at atlas cost; 5 px is the baseline for 512x512 |
| Packing Method | Optimum (slower, better fit) vs Fast (iteration) |
| Atlas Resolution | 512x512 suits ASCII only; bigger sets or finer SDF need more |
| Render Mode | SMOOTH/RASTER (bitmap, no SDF effects); SDFAA (fast, less precise); SDF8/16/32 (oversampled, for large sizes or heavy effects); HINTED variants snap to pixels for crisp small text |
| Character Set | Predefined, or custom decimal/hex ranges or literal characters |
| Font Style / Get Kerning Pairs | Bold/Italic/Outline for bitmap only; imports kerning if the font has it |

**SDF, never static/bitmap, for text that scales or uses outline/underlay/glow.** Choose Render Mode and Atlas Resolution against the real sizes and effects.

## Sprite Assets (`<sprite>`)
Source atlas: Texture Type Sprite (2D and UI), Sprite Mode Multiple, slice in the Sprite Editor, then `Assets > Create > TextMesh Pro > Sprite Asset` (restore the texture's import settings if used elsewhere). Put under `Resources/Sprites`; set a default in TMP Settings or per text object. Fallback sprite assets are searched in order.

**One atlas per text object**: each extra atlas costs a draw call.

## Shaders
| Family | Behaviour |
|---|---|
| Distance Field | Unlit, full SDF effects (outline, underlay, glow, bevel) |
| Distance Field Overlay | Unlit, for overlay rendering |
| Distance Field (Surface) | Scene-lit, more GPU cost; only for text lit inside a 3D/World Space scene |
| Mobile variants | Lighter, fewer simultaneous effects; default on constrained hardware |
| Bitmap shaders | Pair with non-SDF assets; no distance-field effects |

Use Distance Field, never Surface, for ordinary UI text: Screen Space canvases are unlit.
