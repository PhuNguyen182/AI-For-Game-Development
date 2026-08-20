# BatchRendererGroup

Covers SKILL.md step 4's diagnostic use — understanding what Entities Graphics is built on, without needing to call the API directly.

## Manual
- [The BatchRendererGroup API](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/batch-renderer-group-api.html) — `BatchRendererGroup` is the Unity Engine API Entities Graphics is built on top of; it's what connects Entities Graphics to the rendering backend. Using Entities Graphics normally means never touching this API directly — it's handled internally. Unity 2022.1 introduced a unified code path replacing earlier implementations, with better usability, performance, flexibility, and test coverage.

Knowing this exists is mainly useful for reasoning about *why* batching behaves the way it does (see [runtime-creation-and-performance.md](runtime-creation-and-performance.md)'s performance-measurement guidance) — not for writing custom `BatchRendererGroup` code, which is outside this skill's normal scope.
