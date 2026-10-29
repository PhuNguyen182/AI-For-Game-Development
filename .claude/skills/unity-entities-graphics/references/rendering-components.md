# The rendering component set

Sources: `manual/entities-graphics-features.html`, `api/Unity.Rendering.html` and per-type pages.

Baking a prefab gives the best data layout; reproducing the set by hand is a runtime-creation technique ([runtime-creation-and-performance.md](runtime-creation-and-performance.md)).

| Component | Decides |
|---|---|
| `RenderMeshArray` | Shared component holding the mesh and material lists entities index into; differing values partition chunks |
| `MaterialMeshInfo` | Unmanaged, Burst-friendly; selects the mesh and material index from that array (per-entity half) |
| `RenderMeshDescription` | Shadow casting, light probe usage, layer; input to `RenderMeshUtility.AddComponents`, not a per-frame component |
| `RenderBounds` | Culling bounds; wrong bounds show as an object vanishing at screen edges |
| `RenderMeshUnmanaged` | Mesh and rendering properties during baking |
| `RenderMeshUtility` | Static helper; `AddComponents` populates all of the above |
| `LocalToWorld` | From the Entities transform system; without it nothing is drawn |
