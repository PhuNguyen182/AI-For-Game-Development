# Tilemap Collider 2D — Generation & Composite Pairing

Sources: [Tilemap Collider 2D](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-collider-2d.html), [Tilemap Collider 2D reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-collider-2d-reference.html), [Composite Collider 2D reference](https://docs.unity3d.com/Manual/2d-physics/collider/composite-collider/composite-collider-2d-reference.html).
Covers: SKILL.md §4 — **"Pair `TilemapCollider2D` with a `CompositeCollider2D` for level terrain"**.

`TilemapCollider2D` turns tile data into collision shapes — one per tile whose
Collider Type is Grid or Sprite. On its own that means hundreds of small
colliders for a level; paired with a `CompositeCollider2D` those merge into
one shape. Everything attached to the resulting body — `Rigidbody2D`,
materials, effectors, joints — is `unity-2d-physics`'s work.

## Setup

| Step | What it decides | Source |
|---|---|---|
| Add Tilemap Collider 2D to the `Tilemap` | Generates a shape per tile with Collider Type Grid or Sprite; tiles set to None contribute nothing — see [tile-palette-and-tiles.md](tile-palette-and-tiles.md) | [Tilemap Collider 2D](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-collider-2d.html) |
| Add Composite Collider 2D on the same object | Merges those shapes into one, which is the difference between a level's collision costing per tile and costing per surface | [Composite Collider 2D reference](https://docs.unity3d.com/Manual/2d-physics/collider/composite-collider/composite-collider-2d-reference.html) |
| Add a Static `Rigidbody2D` | Required by the composite; Static is correct for terrain that never moves | [Composite Collider 2D reference](https://docs.unity3d.com/Manual/2d-physics/collider/composite-collider/composite-collider-2d-reference.html) |

## Properties

| Property | What it decides | Source |
|---|---|---|
| Maximum Tile Change Count | How many tile edits are absorbed incrementally before Unity rebuilds the whole collider instead; default 1000, and a runtime system crossing it pays a full rebuild rather than an incremental update | [Tilemap Collider 2D reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-collider-2d-reference.html) |
| Extrusion Factor | How far each tile's shape extends, in world units, to close hairline seams between merged tiles — the fix for a character catching on invisible joins | [Tilemap Collider 2D reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-collider-2d-reference.html) |
| Use Delaunay Mesh | Adds a triangulation pass for accuracy on irregular Sprite-type shapes, at generation cost — on only when a specific inaccuracy is observed | [Tilemap Collider 2D reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-collider-2d-reference.html) |
| Material | The `PhysicsMaterial2D` for the generated collision, whose combine semantics `unity-2d-physics` owns | [Tilemap Collider 2D reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-collider-2d-reference.html) |
| Is Trigger | Overlap-only rather than solid — a whole tilemap layer as a detection volume | [Tilemap Collider 2D reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-collider-2d-reference.html) |
| Used by Effector | Opts the generated collider into an `Effector2D` on the same object; off by default and silently required | [Tilemap Collider 2D reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-collider-2d-reference.html) |
| Composite Operation | Merge, Intersect, Difference, Flip, or None when combined — **and it does nothing at all without an actual `CompositeCollider2D` present** | [Tilemap Collider 2D reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-collider-2d-reference.html) |
| Composite Order | Evaluation order against other sources feeding the same composite | [Tilemap Collider 2D reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-collider-2d-reference.html) |
| Offset | Shifts generated shapes from the tile positions, in units | [Tilemap Collider 2D reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-collider-2d-reference.html) |
| Layer Overrides | Priority, include and exclude layers, force send and receive, contact capture and callback layers — identical semantics to any `Collider2D`, owned by `unity-2d-physics` | [Tilemap Collider 2D reference](https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-collider-2d-reference.html) |

## Scripting

| Member | What it decides | Source |
|---|---|---|
| `maximumTileChangeCount`, `extrusionFactor`, `useDelaunayMesh` | Runtime equivalents of the fields above | [TilemapCollider2D API](https://docs.unity3d.com/ScriptReference/Tilemaps.TilemapCollider2D.html) |
| `hasTilemapChanges` | Whether tile edits are still pending a collider rebuild — the guard before assuming a runtime tile change is already collidable | [TilemapCollider2D API](https://docs.unity3d.com/ScriptReference/Tilemaps.TilemapCollider2D.html) |
