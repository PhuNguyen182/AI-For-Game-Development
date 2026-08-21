# Placeholder Sprites — Blockout Before Art

Source: [Add placeholder sprites](https://docs.unity3d.com/Manual/sprite/placeholder/placeholder-landing.html).
Covers: SKILL.md §4 — **"Read sprite data through the members that stay valid under packing"**, escalation branch.

Placeholder sprites are procedurally generated white primitives Unity ships so
a feature can be wired, sorted, collided, and playtested before art exists.
They are not backed by a texture asset, which is the one constraint that
shapes how they are used and retired.

| Aspect | What it decides | Source |
|---|---|---|
| Creation | **GameObject > 2D Object > Sprites**, with the 2D Sprite package installed — the shape list is Editor-version dependent, so read the live menu rather than assuming a fixed set | [Add placeholder sprites](https://docs.unity3d.com/Manual/sprite/placeholder/placeholder-landing.html) |
| What you get | A GameObject with a `SpriteRenderer` already assigned — no manual component wiring | [Add placeholder sprites](https://docs.unity3d.com/Manual/sprite/placeholder/placeholder-landing.html) |
| Hard constraint | A placeholder cannot be opened in the Sprite Editor, because there is no importable texture behind it — so no slicing, outline, physics shape, or border can be authored on one | [Add placeholder sprites](https://docs.unity3d.com/Manual/sprite/placeholder/placeholder-landing.html) |
| Swapping to final art | Reassign the `SpriteRenderer`'s Sprite reference; sorting, colliders, and animation bindings on the GameObject survive untouched | [Add placeholder sprites](https://docs.unity3d.com/Manual/sprite/placeholder/placeholder-landing.html) |

**Critical caveat**: the swap carries no import decisions with it. Because the
placeholder never had a PPU, Mesh Type, pivot, or physics shape, the arrival
of real art is exactly when the [import-settings.md](import-settings.md) pass
has to happen — a scene that looked correct in blockout will change size the
moment the real texture lands at a different PPU.
