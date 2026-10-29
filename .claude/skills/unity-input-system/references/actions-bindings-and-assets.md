# Actions, Bindings, Interactions, Processors

Docs (1.20 manual): `Actions`, `action-assets`, `action-type-reference`, `bindings`, `composite-bindings`, `control-schemes`, `about-project-wide-actions`, `generate-cs-api-from-actions`, `Interactions`, `built-in-interactions`, `Processors`, `built-in-processors`.

## The asset
- `.inputactions` holds maps, actions, bindings and schemes; authoring elsewhere fragments the source of truth.
- Project-wide actions: one asset preloaded, kept alive and enabled by default, reachable through the static hub. A manually created asset starts disabled and its owner must enable it.
- Action map = the enable/disable unit (swap Player and UI maps as a pair when a menu opens).
- Generated C# class: a rename becomes a compile error instead of a silent runtime miss.
- `InputActionReference`: serialized reference to one action, replacing a string lookup.
- An action never enabled yields its default value forever and raises nothing.

## Action types
| Type | Behaviour |
|---|---|
| `Button` | Performs once when actuation crosses the press point; resolves competing controls to the most actuated |
| `Value` | Performs continuously while actuated, same conflict resolution |
| `PassThrough` | No phases, no conflict resolution; every bound control reports independently |

## Composites
| Binding | Note |
|---|---|
| 1D Axis | Tie-breaking property decides when both keys are held; unset = arbitrary |
| 2D / 3D Vector | Mode decides whether a diagonal is normalised; unset makes keyboard diagonals faster than a stick |
| One / Two Modifiers | Chord: value passes only while the modifier(s) are held |

## Control Schemes
- Empty device-requirement list matches nothing: bindings read as ignored.
- Binding groups let one action carry keyboard and gamepad paths without a device check in gameplay code.

## Interactions
A Processor rewrites the value; an Interaction decides when phases happen, so it can stop an action firing at all.

| Interaction | Performs when | Cancels when |
|---|---|---|
| Press | Crosses the press point, falls back, or both (behaviour setting) | n/a for press-only |
| Hold | Held above press point for the full duration (while still held) | Released early |
| Tap | Released within the duration | Held past it: a slow tap becomes nothing, not a hold |
| Slow Tap | Released after the minimum duration (inverse of Tap; often swapped by mistake) | Released too early |
| Multi Tap | Full tap sequence within count, spacing and per-tap duration | A tap held too long or gap too long |

A Hold on a button players tap reads as a dead binding; nothing in the Inspector or console says so.

## Processors
| Processor | Note |
|---|---|
| Clamp | Min/max |
| Invert, Invert Vector 2/3 | Right place for inverted-look, not a sign flip in gameplay code |
| Normalize, Normalize Vector 2/3 | Range to 0..1 (or -1..1 when min is below the zero point); vector to unit length |
| Scale, Scale Vector 2/3 | Sensitivity belongs here |
| Axis Deadzone | Below min snaps to zero, above max clamps; triggers and single axes |
| Stick Deadzone | Applied to the vector magnitude, so diagonals are not penalised like a per-axis deadzone |

Project default deadzones apply unless a binding overrides them. A custom Interaction/Processor must be registered before any asset names it; most "custom" requests are a built-in plus timing logic that belongs in Shared Core.
