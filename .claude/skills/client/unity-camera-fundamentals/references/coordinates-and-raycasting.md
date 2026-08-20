# Coordinate Conversion & Raycasting

Covers SKILL.md step 5 (world/screen/viewport conversions, camera-driven raycasting).

## Scripting API
- [`Camera.WorldToScreenPoint`](https://docs.unity3d.com/ScriptReference/Camera.WorldToScreenPoint.html), [`Camera.ScreenToWorldPoint`](https://docs.unity3d.com/ScriptReference/Camera.ScreenToWorldPoint.html), [`Camera.ScreenToViewportPoint`](https://docs.unity3d.com/ScriptReference/Camera.ScreenToViewportPoint.html)
- [`Camera.ScreenPointToRay`](https://docs.unity3d.com/ScriptReference/Camera.ScreenPointToRay.html) — camera-driven raycasting (click/tap picking).
- [`Physics.RaycastNonAlloc`](https://docs.unity3d.com/ScriptReference/Physics.RaycastNonAlloc.html) / [`Physics2D.Raycast`](https://docs.unity3d.com/ScriptReference/Physics2D.Raycast.html) — non-allocating raycast for hot-path camera picking.
