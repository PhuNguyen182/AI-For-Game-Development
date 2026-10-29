# Coordinate spaces, conversions and picking

Source: [Camera API](https://docs.unity3d.com/ScriptReference/Camera.html), [ScreenToWorldPoint](https://docs.unity3d.com/ScriptReference/Camera.ScreenToWorldPoint.html), [WorldToScreenPoint](https://docs.unity3d.com/ScriptReference/Camera.WorldToScreenPoint.html), [ScreenPointToRay](https://docs.unity3d.com/ScriptReference/Camera.ScreenPointToRay.html), [Physics.Raycast](https://docs.unity3d.com/ScriptReference/Physics.Raycast.html).

These conversions never fail: they return a `Vector3` even for geometrically meaningless input, so misuse gives confident wrong answers.

## Spaces
- World: scene units.
- Screen: pixels, origin bottom-left, up to `Screen.width`/`Screen.height`. UI and some input paths use top-left; flip when crossing.
- Viewport: normalised 0-1 across the camera's own rect, not the screen; right for split-screen maths, wrong for absolute pixels.

## Depth argument
- `ScreenToWorldPoint(v)`: `v.z` is distance from the camera in world units. At zero the result is the camera's own position for every input, the commonest misuse. Orthographic still needs a sensible z.
- `WorldToScreenPoint(p)`: z is distance from the camera. Negative z means behind the camera, with plausible mirrored x/y; an off-screen indicator without this check points the wrong way for exactly the targets it exists to show.

## Picking
- `ScreenPointToRay(pos)`: entry point for click/tap picking; position comes from the input layer.
- `Physics.Raycast` mask and max distance default to everything and infinity; always set both.
- `Physics.RaycastNonAlloc` with a reused buffer for per-frame use; the allocating overload returns a new array each call.
- `Physics2D.Raycast` for 2D scenes; 3D and 2D colliders do not see each other.
- For a click on a known ground plane, intersect the ray with a `Plane`: no collider, cannot miss.

## Example
Tap-to-move: screen position from the input layer, `ScreenPointToRay`, non-allocating raycast on a Ground mask with explicit max distance, camera cached in `Awake`; the world point goes to the Client movement system, which calls Shared Core. The camera script only answers where the tap landed.
