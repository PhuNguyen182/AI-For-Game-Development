# Radial, Curve, Shape, Align and Random Layouts

Pages: `/docs/circleLayout`, `curveLayout`, `shapeLayout`, `alignLayout`, `randomLayout`, `randomModifier`; API `Flexalon<Name>Layout`. Shared enums: `Align`, `Plane` (`XY`/`XZ`/`ZY`).

| Arrangement | Layout |
|---|---|
| Ring, carousel, radial menu, spiral | `FlexalonCircleLayout` |
| Authored path, possibly extended past its ends | `FlexalonCurveLayout` |
| Concentric n-sided formation | `FlexalonShapeLayout` |
| Children keep own positions, pinned to floor/wall/edge | `FlexalonAlignLayout` |
| Deliberately messy | `FlexalonRandomLayout` (replaces the arrangement) |
| Regular plus a little disorder | Any layout + `FlexalonRandomModifier` ([constraints-and-modifiers.md](constraints-and-modifiers.md)) |

## Circle / spiral
| Property | Decides |
|---|---|
| `Plane` (v4.0) | Plane of the circle; its two axes are "axis 1/2" for radius options |
| `InitialRadius` (v4.0) | `Fixed = 0` uses `Radius`; `HalfAxis1 = 1`, `HalfAxis2 = 2`, `HalfMinAxis = 3`, `HalfMaxAxis = 4` derive from half the layout's own size |
| `SpacingType` | `Fixed = 0` uses `SpacingDegrees` (can overflow 360); `Evenly = 1` spreads the full circle |
| `RadiusType` / `RadiusStep` | `Constant = 0`; `Step = 1` per child (spiral, negative = inward); `Wrap = 2` per full turn (concentric rings) |
| `Spiral` / `SpiralSpacing` | Offsets along the plane normal to build a helix |
| `StartAtDegrees` | Rotates all children; first child otherwise at `(radius, 0, 0)` |
| `Rotate` | `None = 0`, `Out = 1`, `In = 2`, `Forward = 3`, `Backward = 4` |
| `PlaneAlign` (v4.0) | Alignment on the plane normal: per object for a circle, whole spiral for a spiral |

`Half*` options size the circle from a parent: with `Plane.XZ`, `InitialRadius = HalfAxis1` and width `Fill`, diameter matches layout width. The Constraints page still says "Use Width"; since v4.0 it is `InitialRadius`.

## Curve
| Property | Decides |
|---|---|
| `Points` | `CurvePoint` = `Position`, `Tangent` (an offset), `TangentMode`; three points along X by default |
| `TangentMode` | `Manual = 0`, `MatchPrevious = 1`, `Corner = 2`, `Smooth = 3` |
| `SpacingType` / `Spacing` | `Fixed = 0` absolute; `Evenly = 1` pins first/last to the ends; `EvenlyConnected = 2` loops a closed curve |
| `StartAt` | Offsets all objects along the curve; the property to drive from a Unity `Animator` |
| `BeforeStart`, `AfterEnd` (v3.0) | `Stop = 0`, `PingPong = 1`, `ExtendLine = 2`, `Repeat = 3`, `RepeatMirror = 4` |
| `Rotation` | `None = 0`, `In = 1`, `Out = 2`, `InWithRoll = 3`, `OutWithRoll = 4`, `Forward = 5`, `Backward = 6` |
| `CurveLength`, `CurvePositions` | Read-only sampling; do not re-derive the bezier |
| `AddPoint`, `InsertPoint`, `RemovePoint` | Runtime editing |
| `LockPositions`, `LockTangents` | Editor handles only |

Writing `StartAt` every frame dirties the whole subtree every frame (legitimate, but profile before shipping on mobile).

## Shape
`Sides`, `Spacing` (between layers), `ShapeRotationDegrees` (rotates the formation, not the children), `Plane`, `PlaneAlign`. First child at the centre, later children in outward layers, so child order is distance from the centre (leader plus ranks).

## Align
`HorizontalAlign`/`VerticalAlign`/`DepthAlign` place each child within the layout's size; `*Pivot` picks which part of the child's own box lands there. Same align/pivot pair as `FlexalonConstraint`.

## Random layout
- `RandomSeed` keeps results stable across the constant recomputes.
- Per-axis opt-in. Position: `RandomizePositionX/Y/Z`, `PositionMin`/`PositionMax` (+ per-axis `PositionMinX`..`PositionMaxZ`). Rotation: `RandomizeRotationX/Y/Z`, `RotationMin`/`RotationMax` (Quaternion, + per-axis floats). Size: `RandomizeSizeX/Y/Z`, `SizeMin`/`SizeMax`.
- Size randomizes the available size: children must be `Fill` for it to matter. Align then seats randomly sized props on a surface.
