# Adapters — how `SizeType.Component` is measured and how scale is applied

Sources: [Adapters](https://www.flexalon.com/docs/adapters), [Interface Adapter](https://www.flexalon.com/docs/api/Flexalon.Adapter.html), [Class FlexalonAspectRatioAdapter](https://www.flexalon.com/docs/api/Flexalon.FlexalonAspectRatioAdapter.html), [Class FlexalonColliderAdapter](https://www.flexalon.com/docs/api/Flexalon.FlexalonColliderAdapter.html).
Covers: SKILL.md §4 — **"Confirm which adapter measures an object before fighting its size"**.

An adapter decides two things: what size a `SizeType.Component` axis
resolves to from the attached Unity components, and what the pipeline does to
the gameObject's `localScale` and components once layout is known. Almost
every "the object is the wrong size" or "why is my scale being overwritten"
question is an adapter question, not a layout one. Size *intent* lives in
[flexalon-object-sizing.md](flexalon-object-sizing.md).

## Built-in default adapters

Used whenever `FlexalonObject.UseDefaultAdapter` is set (v4.3).

| Component | Measured size | What happens to scale | Source |
|---|---|---|---|
| `TMP_Text` | The size of the text; **the `RectTransform` is resized to fit it** | Scale set to the `FlexalonObject.Scale` value | [Adapters](https://www.flexalon.com/docs/adapters) |
| `RectTransform` | The rect transform's size | Scale set to the `FlexalonObject.Scale` value | [Adapters](https://www.flexalon.com/docs/adapters) |
| `MeshRenderer` | The renderer's local bounds | **Scaled uniformly where possible** — this is why a mesh does not stretch to a non-uniform box | [Adapters](https://www.flexalon.com/docs/adapters) |
| `SpriteRenderer` | The sprite's size | Scaled uniformly; depth scale is 1 | [Adapters](https://www.flexalon.com/docs/adapters) |
| `Collider` | The collider's local bounds, per collider type | Scaled uniformly where possible | [Adapters](https://www.flexalon.com/docs/adapters) |
| `Collider2D` | The collider's local bounds | Scaled uniformly where possible; depth scale is 1 | [Adapters](https://www.flexalon.com/docs/adapters) |
| `Canvas` (uGUI) | Non-root canvases and World Space canvases are adapted as `RectTransform`s | **Root canvas sizes are never modified** — Unity owns them | [Adapters](https://www.flexalon.com/docs/adapters) |
| `Image` (uGUI) | If **only one** axis is `Component`, it is set from the sprite's aspect ratio | Scale set to the `FlexalonObject.Scale` value | [Adapters](https://www.flexalon.com/docs/adapters) |
| Empty GameObject | Size 1 per axis | — | [Enum SizeType](https://www.flexalon.com/docs/api/Flexalon.SizeType.html) |

**Critical caveat**: the default adapter for a `MeshRenderer`, sprite, or
collider **writes `localScale`**. Any other system that also writes
`localScale` — a tween, an animation clip, a script — is in a fight with the
pipeline for the same value. Route scale through `FlexalonObject.Scale`, or
uncheck `UseDefaultAdapter` and take over sizing yourself.

## Adapter components you can add

| Component | What it changes | Use when | Source |
|---|---|---|---|
| `FlexalonAspectRatioAdapter` | Maintains an explicit `Width`:`Height` ratio when only one or two size axes are set | The object has no component to measure but must keep a ratio — a placeholder frame, a video surface | [Class FlexalonAspectRatioAdapter](https://www.flexalon.com/docs/api/Flexalon.FlexalonAspectRatioAdapter.html) |
| `FlexalonColliderAdapter` | **Resizes the collider itself** to match the Flexalon size, instead of scaling the gameObject | Scaling the object would distort its visuals or its physics material, but the collider must still match the layout box | [Adapters](https://www.flexalon.com/docs/adapters) |
| `UseDefaultAdapter = false` | Measures the object as if empty, ignoring every attached component | A renderer's bounds (a particle system, an oversized mesh, a bounding helper) is the wrong sizing authority | [Class FlexalonObject](https://www.flexalon.com/docs/api/Flexalon.FlexalonObject.html) |

Both built-in adapter components derive from `FlexalonComponent`, so adding
one to a gameObject replaces the default adapter for that node — there is no
stacking, one adapter wins.

## The `Adapter` interface

| Member | Contract | Source |
|---|---|---|
| `Measure(FlexalonNode node, Vector3 size, Vector3 min, Vector3 max)` | Update **only** the axes reported as `SizeType.Component` by `node.GetSizeType()`, return bounds that include the passed-in size and the auto size, and **ensure the result fits within `min`/`max`** | [Interface Adapter](https://www.flexalon.com/docs/api/Flexalon.Adapter.html) |
| `TryGetScale(FlexalonNode node, out Vector3 scale)` | Return `true` plus the desired **local** scale if the gameObject's scale should be modified | [Interface Adapter](https://www.flexalon.com/docs/api/Flexalon.Adapter.html) |
| `TryGetRectSize(FlexalonNode node, out Vector2 rectSize)` | Return `true` plus the desired rect size if a `RectTransform` should be resized | [Interface Adapter](https://www.flexalon.com/docs/api/Flexalon.Adapter.html) |
| `FlexalonNode.SetAdapter(Adapter)` | Installs a custom adapter on a node — `Flexalon.GetOrCreateNode(gameObject).SetAdapter(yourObject)` | [Adapters](https://www.flexalon.com/docs/adapters) |
| `FlexalonNode.Adapter` | The adapter currently active for a node — the read to make when diagnosing a size | [Interface FlexalonNode](https://www.flexalon.com/docs/api/Flexalon.FlexalonNode.html) |

```csharp
using UnityEngine;
using Flexalon;

namespace Game.Client.Layout
{
    // Sizes an object from a runtime-generated mesh instead of renderer bounds.
    public class ProceduralMeshAdapter : MonoBehaviour, Adapter
    {
        [SerializeField] private MeshFilter source;

        public Bounds Measure(FlexalonNode node, Vector3 size, Vector3 min, Vector3 max)
        {
            Vector3 measured = size;
            Bounds meshBounds = this.source.sharedMesh.bounds;

            for (int i = 0; i < 3; i++)
            {
                if (node.GetSizeType(i) == SizeType.Component)
                {
                    measured[i] = meshBounds.size[i];
                }

                measured[i] = Mathf.Clamp(measured[i], min[i], max[i]);
            }

            return new Bounds(Vector3.zero, measured);
        }

        public bool TryGetScale(FlexalonNode node, out Vector3 scale)
        {
            scale = Vector3.one;
            return false;
        }

        public bool TryGetRectSize(FlexalonNode node, out Vector2 rectSize)
        {
            rectSize = Vector2.zero;
            return false;
        }
    }
}
```

**Critical caveat**: `Measure` must respect `min`/`max` itself — the
interface states it as the adapter's obligation, not something the pipeline
applies afterwards. Returning bounds outside them produces a size that no
later step corrects. `UpdateSize` in the docs' prose corresponds to the
`TryGetScale`/`TryGetRectSize` pair in the current API; implement those, and
never touch the `Transform` from inside an adapter.

## Diagnosing a wrong size

| Symptom | First check | Source |
|---|---|---|
| Object is size 1 for no reason | It has no measurable component, or `UseDefaultAdapter` is unchecked | [Enum SizeType](https://www.flexalon.com/docs/api/Flexalon.SizeType.html) |
| Mesh looks squashed or refuses to fill a non-uniform box | The mesh adapter scales **uniformly where possible** by design — use a `Fixed` size or a different adapter | [Adapters](https://www.flexalon.com/docs/adapters) |
| An image stretches instead of keeping its ratio | More than one axis is set to `Component`; the `Image` adapter derives the ratio only when exactly one is | [Adapters](https://www.flexalon.com/docs/adapters) |
| A canvas ignores its Flexalon size | It is a root canvas — Unity owns those; put the layout on a child | [Adapters](https://www.flexalon.com/docs/adapters) |
| `localScale` keeps being overwritten | The default adapter is writing it every update — see the caveat above | [Adapters](https://www.flexalon.com/docs/adapters) |
| The number is wrong but the source is unclear | Read `FlexalonResult.AdapterBounds` vs `LayoutBounds` on the object, per [core-concepts-and-pipeline.md](core-concepts-and-pipeline.md) | [Class FlexalonResult](https://www.flexalon.com/docs/api/Flexalon.FlexalonResult.html) |
