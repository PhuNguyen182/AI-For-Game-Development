# Tilemap Collider 2D

Pages: https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-collider-2d.html, https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-collider-2d-reference.html

`TilemapCollider2D` makes one shape per tile whose Collider Type is Grid or Sprite (None contributes nothing). Alone that is hundreds of colliders; with a `CompositeCollider2D` they merge into one. Body, materials, effectors and joints are `unity-2d-physics`'s.

## Setup

1. Add Tilemap Collider 2D to the Tilemap.
2. Add Composite Collider 2D on the same object (collision cost per surface, not per tile).
3. Add a Static `Rigidbody2D` (required by the composite; Static for terrain that never moves).

## Properties

| Property | Decision |
|---|---|
| Maximum Tile Change Count | Edits absorbed incrementally before a full rebuild; default 1000. Crossing it in one batch pays a full rebuild |
| Extrusion Factor | Extends each shape (world units) to close hairline seams; fixes a character catching on invisible joins |
| Use Delaunay Mesh | Triangulation for irregular Sprite-type shapes, at generation cost; on only for an observed inaccuracy |
| Material | `PhysicsMaterial2D` (combine semantics: `unity-2d-physics`) |
| Is Trigger | Overlap-only; a layer as detection volume |
| Used by Effector | Opts into an `Effector2D` on the same object; off by default and silently required |
| Composite Operation | Merge, Intersect, Difference, Flip, None; **does nothing without a `CompositeCollider2D`** |
| Composite Order | Evaluation order against other composite sources |
| Offset | Shifts shapes from tile positions |
| Layer Overrides | Same as any `Collider2D` (`unity-2d-physics`) |

Script: `maximumTileChangeCount`, `extrusionFactor`, `useDelaunayMesh`; `hasTilemapChanges` says whether edits still await a collider rebuild, so check it before assuming a runtime tile change is collidable.
