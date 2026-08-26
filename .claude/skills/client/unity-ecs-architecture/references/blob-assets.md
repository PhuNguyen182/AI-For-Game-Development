# Blob Assets — Immutable Data Shared by Reference

Sources: [Store immutable data with blob assets](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/blob-assets-intro.html), [Create a blob asset](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/blob-assets-create.html).
Covers: SKILL.md §4 — **"Move immutable bulk data behind a `BlobAssetReference<T>`"**.

The mechanism for data that many entities read and none of them writes — a
damage curve, a loot table, a navmesh. It is the alternative to copying the
same table into every component instance.

| Subject | What it decides | Source |
|---|---|---|
| `BlobAssetReference<T>` | A component-storable handle to one shared, permanently immutable allocation; copying the component copies the handle, not the data | [Blob assets intro](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/blob-assets-intro.html) |
| No managed data | A blob cannot contain regular arrays, strings, or object references — use `BlobArray<T>` and `BlobString` instead, or the build fails rather than degrading | [Blob assets intro](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/blob-assets-intro.html) |
| Immutability | Written once at construction and never modified — anything that must change per entity is an ordinary component, not blob content | [Blob assets intro](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/blob-assets-intro.html) |
| `BlobBuilder` | Allocates the root, populates nested arrays, then produces the reference; the builder itself is disposed after construction | [Create a blob asset](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/blob-assets-create.html) |
| Built during baking | Constructing the blob in a Baker means it is authored once into the entity scene rather than rebuilt at load | [Create a blob asset](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/blob-assets-create.html) |

**Critical caveat**: internal blob pointers are relative offsets, which is what
makes a blob relocatable and serializable — and also why a blob struct must
never be copied field-by-field out of its allocation. Read through the
reference, never around it.
