# Coordinate Spaces, Conversions, and Picking

Sources: [Camera API](https://docs.unity3d.com/ScriptReference/Camera.html), [Camera.ScreenToWorldPoint](https://docs.unity3d.com/ScriptReference/Camera.ScreenToWorldPoint.html), [Camera.WorldToScreenPoint](https://docs.unity3d.com/ScriptReference/Camera.WorldToScreenPoint.html), [Camera.ScreenPointToRay](https://docs.unity3d.com/ScriptReference/Camera.ScreenPointToRay.html).
Covers: SKILL.md §4 — **"Pass a real distance as the z component of `ScreenToWorldPoint`"**, **"Check the returned z before trusting `WorldToScreenPoint`"**, **"Bound and mask every camera-driven raycast, and use the non-allocating overload in a per-frame path"**.

These conversions do not fail. They return a `Vector3` for every input,
including inputs that make no geometric sense, which is why their two common
misuses produce confident wrong answers rather than errors: a missing depth
argument, and a point that is behind the camera.

## The three spaces

| Space | Units and origin | Source |
|---|---|---|
| World | Scene units, arbitrary origin | [Camera API](https://docs.unity3d.com/ScriptReference/Camera.html) |
| Screen | Pixels, origin **bottom-left**, extending to `Screen.width`/`Screen.height`. Note UI systems and some input paths use a top-left origin, so a value crossing that boundary needs flipping | [Camera.ScreenToWorldPoint](https://docs.unity3d.com/ScriptReference/Camera.ScreenToWorldPoint.html) |
| Viewport | Normalised 0–1 across the camera's own rect, not the screen — which makes it the right space for split-screen maths and the wrong one for absolute pixel work | [Camera.ScreenToViewportPoint](https://docs.unity3d.com/ScriptReference/Camera.ScreenToViewportPoint.html) |

## The depth argument

| Call | What z means | Source |
|---|---|---|
| `ScreenToWorldPoint(v)` | `v.z` is **distance from the camera in world units**, not a screen coordinate. With `v.z` left at zero the result is the camera's own position, for every input — the single most common misuse of this API | [Camera.ScreenToWorldPoint](https://docs.unity3d.com/ScriptReference/Camera.ScreenToWorldPoint.html) |
| Orthographic case | Still requires a sensible z to place the point along the view direction, even though size does not change with distance | [Camera.ScreenToWorldPoint](https://docs.unity3d.com/ScriptReference/Camera.ScreenToWorldPoint.html) |
| `WorldToScreenPoint(p)` | Returns z as the point's distance from the camera. **Negative z means the point is behind the camera**, and the returned x and y are mirrored but perfectly plausible — an off-screen indicator without this check points the wrong way for exactly the targets it exists to show | [Camera.WorldToScreenPoint](https://docs.unity3d.com/ScriptReference/Camera.WorldToScreenPoint.html) |

## Picking

| Call | What it decides | Source |
|---|---|---|
| `ScreenPointToRay(pos)` | Builds the ray from a screen position — the correct entry point for click and tap picking. The screen position itself comes from the input layer, not from a legacy `Input` read here | [Camera.ScreenPointToRay](https://docs.unity3d.com/ScriptReference/Camera.ScreenPointToRay.html) |
| `Physics.Raycast` layer mask and max distance | Both default to everything and infinity. An unbounded ray against every layer tests colliders nobody intended and is the default nobody chose | [Physics.Raycast](https://docs.unity3d.com/ScriptReference/Physics.Raycast.html) |
| `Physics.RaycastNonAlloc` with a reused buffer | The per-frame form — the allocating overload returns a fresh array each call, which the no-per-frame-allocation rule in `coding-principles.md` forbids in a hot path | [Physics.RaycastNonAlloc](https://docs.unity3d.com/ScriptReference/Physics.RaycastNonAlloc.html) |
| `Physics2D.Raycast` | The 2D counterpart. A 2D scene needs the 2D call — 3D and 2D colliders do not see each other, per `unity-2d-physics` | [Physics2D.Raycast](https://docs.unity3d.com/ScriptReference/Physics2D.Raycast.html) |
| Plane intersection instead of a raycast | For a click on a known ground plane, intersecting the ray with a `Plane` needs no collider at all and cannot miss | [Camera.ScreenPointToRay](https://docs.unity3d.com/ScriptReference/Camera.ScreenPointToRay.html) |

Collider setup, layer matrix configuration, and query behaviour belong to
`unity-3d-physics` and `unity-2d-physics`; this file covers only the camera
side of building the ray.
