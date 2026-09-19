# Path Tweens

Source: [DOTween Documentation](https://dotween.demigiant.com/documentation.php).
Covers: SKILL.md §4 — "Pick PathType/PathMode deliberately for a path tween, and budget resolution against curve smoothness".

## `DOPath` / `DOLocalPath`

```csharp
transform.DOPath(waypoints, duration, pathType, pathMode, resolution, gizmoColor);
```

| Parameter | Meaning |
|---|---|
| `waypoints` (`Vector3[]`) | Positions the object travels through, in order |
| `duration` | Total time to traverse the whole path |
| `pathType` | `Linear` (straight segments between waypoints), `CatmullRom` (smooth curve through every waypoint), `CubicBezier` (smooth curve using explicit control points) |
| `pathMode` | `Ignore` (no automatic orientation), `3D` (orient toward path direction in 3D), `Sidescroller2D`, `TopDown2D` — controls how/whether the object rotates to face its direction of travel along the path |
| `resolution` | Path detail/smoothness for curved types — default `10`; higher gives a smoother curve at a higher computation cost, lower is cheaper but coarser |
| `gizmoColor` | Editor-only Scene view visualization color for the path |

`CubicBezier` paths need waypoints in groups of three (waypoint, in-control
point, out-control point) — the very first waypoint is derived
automatically from the object's current position, so the array doesn't
need to restate it.

`SetOptions(...)` on a path tween configures closed-loop behavior (the
path wraps back to its start) and related path-specific flags.
`SetLookAt(...)` controls what direction the object faces while
travelling the path, independent of `pathMode`'s automatic orientation.

`Rigidbody2D` has its own `DOPath`/`DOLocalPath` using `Vector2[]`
waypoints, for physics-driven 2D path movement (requires
`DOTweenModulePhysics2D`, per [getting-started.md](getting-started.md)).

## Practical guidance

- Use `Linear` for a patrol route or a deliberately mechanical movement;
  `CatmullRom` for organic/curved motion through a set of waypoints
  without needing explicit control points; `CubicBezier` only when the
  curve shape itself needs hand-authored control points.
- Increase `resolution` only when a visible faceting artifact actually
  shows on a `CatmullRom`/`CubicBezier` curve — the default of 10 is
  adequate for most cases, and resolution cost scales with path length and
  waypoint count.
- `OnWaypointChange` (per [settings-and-callbacks.md](settings-and-callbacks.md))
  is the hook for logic that must fire exactly when the object reaches
  each waypoint, rather than polling position against waypoint coordinates
  by hand.
