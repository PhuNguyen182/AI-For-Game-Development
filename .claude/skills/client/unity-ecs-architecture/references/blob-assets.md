# Blob Assets

Covers SKILL.md step 8 (immutable bulk data shared by reference instead of duplicated per entity).

## Manual
- [Store immutable data with blob assets](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/blob-assets-intro.html) — a blob asset is permanent, unchangeable data referenced by component via `BlobAssetReference<T>`; must contain no managed data (no regular arrays/strings/objects).
- [Create a blob asset](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/blob-assets-create.html) — building a blob asset with `BlobBuilder`: allocate, populate, then create the immutable reference.

Note: Aspects (`IAspect`) are **obsolete and removed as of the Entities 6.x line** (deprecated starting in the 1.x line, then dropped) — the recommended replacement is to use `Component`/`EntityQuery` APIs directly (`SystemAPI.Query<T>`, `IJobEntity`, `IJobChunk`) rather than wrapping component access in an aspect struct.
