# Tilemap Collider 2D

Sources: https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-collider-2d-landing.html, https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-collider-2d.html, https://docs.unity3d.com/Manual/tilemaps/work-with-tilemaps/tilemap-collider-2d-reference.html, https://docs.unity3d.com/Manual/2d-physics/collider/composite-collider/composite-collider-2d-reference.html, `UnityEngine.Tilemaps.TilemapCollider2D` scripting API

## Scope boundary

This component's job is generating `Collider2D` shapes from a `Tilemap`'s tile data. Configuring the resulting body's `Rigidbody2D` dynamics, additional standalone `Collider2D`s, effectors, or joints is `unity-2d-physics`'s territory — this file stops at wiring `TilemapCollider2D` itself and its `CompositeCollider2D` pairing.

## Setup

1. Select the `Tilemap` GameObject, **Add Component > Tilemap Collider 2D**. Unity generates a collider shape per tile that has `Collider Type = Sprite` or `Grid` (see [tile-palette-and-tiles.md](tile-palette-and-tiles.md)).
2. For better performance, also **Add Component > Composite Collider 2D** on the same GameObject (requires a `Rigidbody2D`, typically `Static` for a level's terrain) — `TilemapCollider2D` then merges each tile's individual shape into the composite instead of leaving hundreds of separate per-tile colliders, matching `performance-and-algorithms.md`'s guidance to prune/merge collision work rather than pay per-tile physics cost.

## Inspector properties

| Property | Description |
|---|---|
| Maximum Tile Change Count | Number of tile edits allowed before Unity does a full collider rebuild instead of an incremental one. Default 1000. |
| Extrusion Factor | How far each tile's collision shape extends, in world units, to close seams when compositing with `Composite Collider 2D`. |
| Use Delaunay Mesh | Adds a Delaunay triangulation pass for more accurate collision on complex tile shapes, at extra generation cost. |
| Material | The `PhysicsMaterial2D` applied to the generated collider(s). |
| Is Trigger | Whether the generated shape(s) are trigger (overlap-only) or solid. |
| Used by Effector | Enables `Effector2D` components on the same GameObject to act on this collider — see `unity-2d-physics`'s effectors coverage. |
| Composite Operation | How shapes combine when paired with `Composite Collider 2D`: **Merge**, **Intersect**, **Difference**, **Flip**, **None**. |
| Composite Order | Evaluation order relative to other `Composite Collider 2D` sources. |
| Offset | Offsets generated shapes from tile positions, in units. |
| Layer Overrides | Priority, include/exclude layers, force send/receive layers, contact-capture layers, callback layers — same 2D physics layer-override semantics as any other `Collider2D`. |

## Scripting API surface

| Member | Description |
|---|---|
| `maximumTileChangeCount` | Script-side equivalent of Maximum Tile Change Count. |
| `extrusionFactor` | Script-side equivalent of Extrusion Factor. |
| `useDelaunayMesh` | Script-side equivalent of Use Delaunay Mesh. |
| `hasTilemapChanges` | Read-only — whether pending tile changes still need a collider rebuild. |

## Practical guidance

- Default to `Collider Type = Grid` on tiles plus `TilemapCollider2D` + `Composite Collider 2D` for ordinary level terrain — it's the cheapest, most common setup, and matches `performance-and-algorithms.md`'s simplest-shape and merge-shapes guidance.
- Only enable `Use Delaunay Mesh` when the tileset's actual silhouettes need it (irregular Sprite-type colliders) — it's an added generation cost, not a default-on setting.
- Never make a gameplay decision (damage, trap trigger outcome) inside a `TilemapCollider2D`-driven collision callback — resolve the outcome in Shared Core and let this component only detect the physical event, per `coding-principles.md`'s Shared Core integrity rule.
