# Bounds and Obstruction

Base: https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/ — pages `CinemachineConfiner2D.html`, `CinemachineConfiner3D.html`, `CinemachineDeoccluder.html`.

Choose the confiner by the quantity to bound, not project dimensionality: Confiner2D clamps the **visible area**; Confiner3D clamps camera **position** only, so the view may still include geometry outside the volume.

| Item | Rule |
|---|---|
| `CinemachineConfiner2D` | Bakes a reduced shape from the camera's view size; valid only for that size |
| `InvalidateBoundingShapeCache()` | Call when the shape, orthographic size, FOV or aspect changes, else confinement uses a stale view |
| Shape source | `PolygonCollider2D`, `BoxCollider2D` or `CompositeCollider2D`; a composite must generate filled geometry, not outlines (its setting is `unity-2d-physics`'s) |
| Damping / slowing distance | Both zero → abrupt stop at the edge that reads as a bug |

## Deoccluder
| Setting | Rule |
|---|---|
| Collide Against | Occlusion mask. Everything → avoids triggers, props and the player's own collider (unexplained lurches) |
| Strategy | Pull in front of the obstruction, or preserve height/distance while moving around it |
| Camera Radius | Clearance; too small and the near plane clips walls first |
| Minimum Distance From Target | Stops pushing into the character when cornered |
| Damping / Damping When Occluded | Separate in/out rates; react faster than recover |
| Shot quality | Supplies the rating `CinemachineClearShot` selects on ([multi-target-and-multi-shot.md](multi-target-and-multi-shot.md)) |
