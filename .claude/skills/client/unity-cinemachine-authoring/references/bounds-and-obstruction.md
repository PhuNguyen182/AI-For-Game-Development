# Bounds and Obstruction

Sources: [CinemachineConfiner2D](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineConfiner2D.html), [CinemachineConfiner3D](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineConfiner3D.html), [CinemachineDeoccluder](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineDeoccluder.html).
Covers: SKILL.md §4 — **"Use `CinemachineConfiner2D` for what the camera sees and `CinemachineConfiner3D` for where it is"**, **"Give the Deoccluder a collide-against mask instead of leaving it on Everything"**.

The two confiners are not a 2D and 3D pair of the same thing. One clamps the
camera's **visible area** so the view never shows outside a shape; the other
clamps the camera's **position** inside a volume, which says nothing about
what the view includes. Choosing by project dimensionality rather than by
which quantity needs bounding is the usual mistake.

| Extension | What it bounds, and what it costs | Source |
|---|---|---|
| `CinemachineConfiner2D` | The camera's visible rectangle against a 2D bounding shape. It **bakes** a reduced shape derived from the camera's view size, so the bake is only valid for that size | [CinemachineConfiner2D](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineConfiner2D.html) |
| `InvalidateBoundingShapeCache()` | Must be called when the bounding shape changes, or when orthographic size, field of view, or aspect changes — otherwise the camera is confined to a region computed for a view it no longer has | [CinemachineConfiner2D API](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/api/Unity.Cinemachine.CinemachineConfiner2D.html) |
| Bounding shape source | A `PolygonCollider2D`, `BoxCollider2D`, or `CompositeCollider2D`. A composite must produce filled geometry rather than outlines for the confiner to have an interior to work with — the composite's own geometry setting is `unity-2d-physics`'s | [CinemachineConfiner2D](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineConfiner2D.html) |
| Damping and slowing distance | Softens the stop at the boundary. With both at zero the camera hits the edge abruptly, which reads as a bug rather than a limit | [CinemachineConfiner2D](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineConfiner2D.html) |
| `CinemachineConfiner3D` | The camera's **position** inside a bounding volume. Nothing prevents the view from including geometry outside it | [CinemachineConfiner3D](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineConfiner3D.html) |

## Deoccluder

| Setting | What it decides | Source |
|---|---|---|
| Collide Against | The layer mask the occlusion test uses. Left at Everything, the camera avoids trigger volumes, small props, and the player's own collider, producing lurches with no visible cause | [CinemachineDeoccluder](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineDeoccluder.html) |
| Strategy | Pull the camera in front of the obstruction, or preserve its height or distance while moving around it. The choice is about which property of the shot matters more when they conflict | [CinemachineDeoccluder](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineDeoccluder.html) |
| Camera Radius | The clearance kept from geometry. Too small and the near plane clips into walls before the deoccluder reacts | [CinemachineDeoccluder](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineDeoccluder.html) |
| Minimum Distance From Target | Stops the camera pushing into the character when it is cornered | [CinemachineDeoccluder](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineDeoccluder.html) |
| Damping and Damping When Occluded | Separate rates for moving in and moving back out — asymmetric by design, since reacting to an obstruction should be faster than recovering from one | [CinemachineDeoccluder](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineDeoccluder.html) |
| Shot quality signal | The Deoccluder is what supplies a camera's shot quality rating, which `CinemachineClearShot` selects on — see [multi-target-and-multi-shot.md](multi-target-and-multi-shot.md) | [CinemachineDeoccluder](https://docs.unity3d.com/Packages/com.unity.cinemachine@3.1/manual/CinemachineDeoccluder.html) |
