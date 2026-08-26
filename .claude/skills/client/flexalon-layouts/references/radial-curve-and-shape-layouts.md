# Radial, Curve, Shape, Align, and Random Layouts — the non-linear arrangements

Sources: [Circle Layout](https://www.flexalon.com/docs/circleLayout), [Curve Layout](https://www.flexalon.com/docs/curveLayout), [Shape Layout](https://www.flexalon.com/docs/shapeLayout), [Align Layout](https://www.flexalon.com/docs/alignLayout), [Random Layout](https://www.flexalon.com/docs/randomLayout), and the corresponding [Scripting API](https://www.flexalon.com/docs/api/Flexalon.html) pages.
Covers: SKILL.md §4 — **"Pick the layout component from the arrangement's actual shape"**.

The five layouts that are not packing or gridding: a circle/spiral, a bézier
curve, an n-sided formation, an align-only pass, and a randomizer. Flexible
and Grid live in [flexible-and-grid-layouts.md](flexible-and-grid-layouts.md); all five below share the
`Align` (`Start`/`Center`/`End`) and `Plane` (`XY`/`XZ`/`ZY`) enums.

- [Picking one](#picking-one)
- [`FlexalonCircleLayout` — circle and spiral](#flexaloncirclelayout--circle-and-spiral)
- [`FlexalonCurveLayout` — bézier path](#flexaloncurvelayout--bézier-path)
- [`FlexalonShapeLayout` — n-sided formation](#flexalonshapelayout--n-sided-formation)
- [`FlexalonAlignLayout` — alignment without arrangement](#flexalonalignlayout--alignment-without-arrangement)
- [`FlexalonRandomLayout` — randomized within bounds](#flexalonrandomlayout--randomized-within-bounds)

## Picking one

| The arrangement is | Layout | Source |
|---|---|---|
| A ring, carousel, radial menu, or spiral | `FlexalonCircleLayout` | [Circle Layout](https://www.flexalon.com/docs/circleLayout) |
| Following an authored path, straight or curved, possibly extending past its ends | `FlexalonCurveLayout` | [Curve Layout](https://www.flexalon.com/docs/curveLayout) |
| A crowd/unit formation in concentric n-sided rings | `FlexalonShapeLayout` | [Shape Layout](https://www.flexalon.com/docs/shapeLayout) |
| Children keeping their own positions but pinned to a floor, wall, or edge | `FlexalonAlignLayout` | [Align Layout](https://www.flexalon.com/docs/alignLayout) |
| Deliberately messy — scattered props, jittered debris | `FlexalonRandomLayout` | [Random Layout](https://www.flexalon.com/docs/randomLayout) |
| Regular, but needing a *little* disorder on top | Any layout + `FlexalonRandomModifier` — see [constraints-and-modifiers.md](constraints-and-modifiers.md) | [Random Modifier](https://www.flexalon.com/docs/randomModifier) |

## `FlexalonCircleLayout` — circle and spiral

| Property | What it decides | Source |
|---|---|---|
| `Plane` (v4.0) | Which plane the circle is drawn on; the two plane axes become "axis 1" and "axis 2" for the radius options | [Circle Layout](https://www.flexalon.com/docs/circleLayout) |
| `InitialRadius` (`InitialRadiusOptions`, v4.0) | `Fixed = 0` uses `Radius`; `HalfAxis1 = 1`, `HalfAxis2 = 2`, `HalfMinAxis = 3`, `HalfMaxAxis = 4` derive it from half the layout's own size on that plane axis | [Enum InitialRadiusOptions](https://www.flexalon.com/docs/api/Flexalon.FlexalonCircleLayout.InitialRadiusOptions.html) |
| `Radius` (`float`) | The radius when `InitialRadius` is `Fixed` — ignored otherwise | [Class FlexalonCircleLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonCircleLayout.html) |
| `SpacingType` (`SpacingOptions`) | `Evenly = 1` distributes the full circle between children (count-dependent); `Fixed = 0` uses `SpacingDegrees` (count-independent, so it can overflow past 360°) | [Enum SpacingOptions](https://www.flexalon.com/docs/api/Flexalon.FlexalonCircleLayout.SpacingOptions.html) |
| `SpacingDegrees` (`float`) | Degrees between children when `SpacingType` is `Fixed` | [Class FlexalonCircleLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonCircleLayout.html) |
| `RadiusType` (`RadiusOptions`) | `Constant = 0`; `Step = 1` increments the radius per child (inward/outward spiral); `Wrap = 2` increments once per full turn (concentric rings) | [Enum RadiusOptions](https://www.flexalon.com/docs/api/Flexalon.FlexalonCircleLayout.RadiusOptions.html) |
| `RadiusStep` (`float`) | How much the radius changes per interval — negative spirals inward | [Class FlexalonCircleLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonCircleLayout.html) |
| `Spiral` (`bool`) / `SpiralSpacing` (`float`) | Offsets each object along the plane normal to build a helix, and by how much | [Circle Layout](https://www.flexalon.com/docs/circleLayout) |
| `StartAtDegrees` (`float`) | Rotates all children around the circle; the first child otherwise sits at `(radius, 0, 0)` | [Class FlexalonCircleLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonCircleLayout.html) |
| `Rotate` (`RotateOptions`) | `None = 0`, `Out = 1`, `In = 2`, `Forward = 3`, `Backward = 4` — whether children face the centre, away, or along the ring | [Enum RotateOptions](https://www.flexalon.com/docs/api/Flexalon.FlexalonCircleLayout.RotateOptions.html) |
| `PlaneAlign` (`Align`, v4.0) | Alignment on the plane's normal axis: per-object for a circle, whole-spiral for a spiral | [Circle Layout](https://www.flexalon.com/docs/circleLayout) |

The `Half*` radius options exist to make a circle fit a parent that sized it:
with `Plane.XZ`, `InitialRadius = HalfAxis1`, and width set to `SizeType.Fill`,
the circle's diameter matches the layout width. That is the mechanism the
docs' constraint example uses to grow a ring to 120% of a clicked target —
see [constraints-and-modifiers.md](constraints-and-modifiers.md). Note that the Constraints page still calls
this a "Use Width" property; since v4.0 the property is `InitialRadius`.

## `FlexalonCurveLayout` — bézier path

| Property | What it decides | Source |
|---|---|---|
| `Points` (`IReadOnlyList<CurvePoint>`) | The curve itself — three points along X by default. `CurvePoint` carries `Position`, `Tangent` (an **offset** from the point), and `TangentMode` | [Struct CurvePoint](https://www.flexalon.com/docs/api/Flexalon.FlexalonCurveLayout.CurvePoint.html) |
| `TangentMode` per point | `Manual = 0`, `MatchPrevious = 1`, `Corner = 2` (zero tangent, sharp corner), `Smooth = 3` (computed from neighbours) | [Enum TangentMode](https://www.flexalon.com/docs/api/Flexalon.FlexalonCurveLayout.TangentMode.html) |
| `SpacingType` (`SpacingOptions`) | `Fixed = 0` uses `Spacing` as absolute distance; `Evenly = 1` pins first/last to the ends; `EvenlyConnected = 2` treats a closed curve as a loop so first and last do not collide | [Enum SpacingOptions](https://www.flexalon.com/docs/api/Flexalon.FlexalonCurveLayout.SpacingOptions.html) |
| `Spacing` (`float`) | Distance between children when `SpacingType` is `Fixed` | [Class FlexalonCurveLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonCurveLayout.html) |
| `StartAt` (`float`) | Offsets all objects along the curve — **the property to drive from a Unity `Animator`** to move objects along the path, per [animators.md](animators.md) | [Curve Layout](https://www.flexalon.com/docs/curveLayout) |
| `BeforeStart`, `AfterEnd` (`ExtendBehavior`, v3.0) | What happens past each end: `Stop = 0` (clamp), `PingPong = 1`, `ExtendLine = 2` (straight, along the end tangent), `Repeat = 3`, `RepeatMirror = 4` | [Enum ExtendBehavior](https://www.flexalon.com/docs/api/Flexalon.FlexalonCurveLayout.ExtendBehavior.html) |
| `Rotation` (`RotationOptions`) | `None = 0`, `In = 1`, `Out = 2`, `InWithRoll = 3`, `OutWithRoll = 4`, `Forward = 5`, `Backward = 6` — the `*WithRoll` variants additionally roll the X axis along the curve | [Enum RotationOptions](https://www.flexalon.com/docs/api/Flexalon.FlexalonCurveLayout.RotationOptions.html) |
| `LockPositions`, `LockTangents` (`bool`) | Hide the corresponding scene handles — editor clutter control only, no runtime effect | [Curve Layout](https://www.flexalon.com/docs/curveLayout) |
| `CurveLength` (`float`, get) / `CurvePositions` (`IReadOnlyList<Vector3>`, get) | Read-only sampling of the evaluated curve — the supported way to draw or follow it without re-deriving the bézier | [Class FlexalonCurveLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonCurveLayout.html) |
| `AddPoint`, `InsertPoint`, `RemovePoint` | Runtime curve editing, by `CurvePoint` or by `(position, tangent)` | [Class FlexalonCurveLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonCurveLayout.html) |

```csharp
using UnityEngine;
using Flexalon;

namespace Game.Client.Layout
{
    // Sweeps items along a curve; drive Offset instead if the layout must not re-run.
    public class CurveScroller : MonoBehaviour
    {
        [SerializeField] private FlexalonCurveLayout path;
        [SerializeField] private float unitsPerSecond = 1f;

        private void Awake()
        {
            this.path.SpacingType = FlexalonCurveLayout.SpacingOptions.Fixed;
            this.path.Spacing = 1.5f;
            this.path.Rotation = FlexalonCurveLayout.RotationOptions.Forward;
            this.path.BeforeStart = FlexalonCurveLayout.ExtendBehavior.Repeat;
            this.path.AfterEnd = FlexalonCurveLayout.ExtendBehavior.Repeat;
        }

        private void Update()
        {
            this.path.StartAt += this.unitsPerSecond * Time.deltaTime;
        }
    }
}
```

**Critical caveat**: writing `StartAt` every frame keeps the whole subtree
dirty every frame, so `Measure`/`Arrange` re-run continuously. That is a
legitimate design (the docs animate exactly this property with a Unity
`Animator`) but it is not free — profile it against the frame budget per
`performance-and-algorithms.md`'s Verification section before shipping it on
mobile.

## `FlexalonShapeLayout` — n-sided formation

| Property | What it decides | Source |
|---|---|---|
| `Sides` (`int`) | How many sides each concentric layer has | [Shape Layout](https://www.flexalon.com/docs/shapeLayout) |
| `Spacing` (`float`) | Distance between layers | [Shape Layout](https://www.flexalon.com/docs/shapeLayout) |
| `ShapeRotationDegrees` (`float`) | Rotates the formation around the plane **without rotating the children** | [Shape Layout](https://www.flexalon.com/docs/shapeLayout) |
| `Plane`, `PlaneAlign` | The plane the shape is built on, and per-child alignment on its normal axis | [Class FlexalonShapeLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonShapeLayout.html) |

The first child is placed at the centre and later children fill concentric
layers outward — so child order maps to distance from the centre, which is
what makes it usable for a leader-plus-ranks formation.

## `FlexalonAlignLayout` — alignment without arrangement

| Property | What it decides | Source |
|---|---|---|
| `HorizontalAlign`, `VerticalAlign`, `DepthAlign` (`Align`) | Where each child sits within the **layout's** size | [Class FlexalonAlignLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonAlignLayout.html) |
| `HorizontalPivot`, `VerticalPivot`, `DepthPivot` (`Align`) | Which part of the **child's own** box is placed at that alignment | [Class FlexalonAlignLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonAlignLayout.html) |

This is the layout for "everything sits on the floor / against the wall"
without otherwise arranging anything: children keep their relationships, and
each child's `Offset`, `Rotation`, `Scale`, and size on its own
`FlexalonObject` do the rest. Align/pivot as a pair is the same two-box
mechanic `FlexalonConstraint` uses.

## `FlexalonRandomLayout` — randomized within bounds

| Property group | Members | Notes | Source |
|---|---|---|---|
| Seed | `RandomSeed` (`int`) | Layout re-runs constantly; a seed is what keeps results stable across recomputes rather than reshuffling every frame | [Random Layout](https://www.flexalon.com/docs/randomLayout) |
| Position | `RandomizePositionX/Y/Z`, `PositionMin`/`PositionMax` (+ per-axis `PositionMinX`…) | Per-axis opt-in, then bounds | [Class FlexalonRandomLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonRandomLayout.html) |
| Rotation | `RandomizeRotationX/Y/Z`, `RotationMin`/`RotationMax` (`Quaternion`, + per-axis floats) | Same shape as position | [Class FlexalonRandomLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonRandomLayout.html) |
| Size | `RandomizeSizeX/Y/Z`, `SizeMin`/`SizeMax` | Randomizes the **available** size — the API states children must be set to `Fill` for it to have any effect | [Class FlexalonRandomLayout](https://www.flexalon.com/docs/api/Flexalon.FlexalonRandomLayout.html) |
| Align | `HorizontalAlign`, `VerticalAlign`, `DepthAlign` | Aligns each child within the randomized size — this is how randomly sized props still sit *on* a surface rather than through it | [Random Layout](https://www.flexalon.com/docs/randomLayout) |

`FlexalonRandomLayout` **replaces** the arrangement; `FlexalonRandomModifier`
perturbs one that another layout already produced. Choose the modifier
whenever the underlying order still matters.
