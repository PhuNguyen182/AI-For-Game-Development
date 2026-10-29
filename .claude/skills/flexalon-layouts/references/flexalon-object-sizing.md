# Flexalon Object Sizing

Pages: `/docs/flexalonObject`, API `FlexalonObject`, `SizeType`, `MinMaxSizeType`, `Directions`.

## `SizeType` per axis (`WidthType`, `HeightType`, `DepthType`)
| Type | Meaning | Choose when |
|---|---|---|
| `Component` | From the adapter and attached components; empty GameObject = 1 ([adapters.md](adapters.md)) | Content decides size |
| `Fixed` | Explicit value (`Width`/`Height`/`Depth`, `Size`) | Design constant |
| `Fill` | Factor of the space the parent layout allocated: `WidthOfParent` etc., `0.5` is half | Consume available space |
| `Layout` | Computed from the object's own layout and children | Container shrink-wraps |

`Fill` child under a `Layout` parent on the same axis is circular. Flexible wrap and `SpaceBetween` likewise do nothing while the direction axis is `Layout`.

Older docs say "Parent" where the current enum member is `SizeType.Fill`.

## Min / max (v4.1)
`MinWidthType`/`MinWidth`/`MinWidthOfParent` (+ Height/Depth, `MinSize`), same for `Max*`. `MinMaxSizeType`: `Fixed`, `Fill` (factor of parent), `None` (min: cannot shrink; max: infinity).
A min type other than `None` also opts the object into being shrunk below its `Fixed` size (docs example: width 3 in a 2x2 cell with min 0 shrinks to 2). Applied amount: `FlexalonResult.ShrinkSize`.

## Spacing
| | Where | Read by |
|---|---|---|
| `Margin` | Around the object | The parent's layout (spaces siblings) |
| `Padding` | Inside the object | Its own layout (shrinks child space) |

`Directions` struct: `Right/Left/Top/Bottom/Back/Front`. Per-item margin when spacing differs per child; layout `Gap` when uniform.

## Offset, rotation, scale
| Property | Applied | Effect |
|---|---|---|
| `Rotation` | Before layout | Box grows to encapsulate the rotated object |
| `Scale` | Before layout | Layout sees the scaled size |
| `Offset` | After layout | Final position only; siblings do not move (nudge, hover lift, overlap) |

## Opt-outs
- `SkipLayout` (v4.1): parent layout ignores this child and leaves its position/rotation alone.
- `UseDefaultAdapter` (v4.3): unchecked, measures as an empty GameObject ([adapters.md](adapters.md)).
