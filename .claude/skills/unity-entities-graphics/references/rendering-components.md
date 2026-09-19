# The Rendering Component Set

Sources: [Entities Graphics Features](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/entities-graphics-features.html), [Unity.Rendering namespace](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/api/Unity.Rendering.html).
Covers: SKILL.md §4 — **"Let baking produce the rendering component set wherever the content is design-time"**.

What an entity needs in order to render, and which of it baking supplies for
free. Hand-assembly belongs to runtime creation only —
[runtime-creation-and-performance.md](runtime-creation-and-performance.md).

| Component | What it decides | Source |
|---|---|---|
| `RenderMeshArray` | Shared component holding the mesh and material lists many entities index into — being shared, differing values partition chunks, so one array across a population keeps the archetype dense | [RenderMeshArray](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/api/Unity.Rendering.RenderMeshArray.html) |
| `MaterialMeshInfo` | Unmanaged, Burst-friendly component selecting which mesh and material index this entity uses from that array — the per-entity half of the pair | [MaterialMeshInfo](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/api/Unity.Rendering.MaterialMeshInfo.html) |
| `RenderMeshDescription` | Describes shadow casting, light probe usage, and layer for `RenderMeshUtility.AddComponents` — the runtime-creation input, not a per-frame component | [RenderMeshDescription](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/api/Unity.Rendering.RenderMeshDescription.html) |
| `RenderBounds` | The bounds culling uses — wrong bounds show up as an object vanishing at screen edges rather than as an error | [RenderBounds](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/api/Unity.Rendering.RenderBounds.html) |
| `RenderMeshUnmanaged` | Defines mesh and rendering properties during baking | [RenderMeshUnmanaged](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/api/Unity.Rendering.RenderMeshUnmanaged.html) |
| `RenderMeshUtility` | Static helper whose `AddComponents` populates all of the above on an entity | [RenderMeshUtility](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/api/Unity.Rendering.RenderMeshUtility.html) |
| `LocalToWorld` | Supplied by the Entities transform system, not this package — an entity without it has no place to be drawn | [Overview](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/overview.html) |

**Critical caveat**: baking a prefab is the preferred route precisely because
it produces the best data layout. Reproducing the same set by hand is legal but
gives up that layout, so it is a runtime-creation technique rather than an
alternative authoring style.
