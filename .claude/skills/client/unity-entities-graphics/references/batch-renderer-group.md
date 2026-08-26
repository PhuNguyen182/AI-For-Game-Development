# BatchRendererGroup — What the Package Is Built On

Source: [The BatchRendererGroup API](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/batch-renderer-group-api.html).
Covers: SKILL.md §4 — **"Measure batching as instances per draw command"**.

Background for reasoning about batching behaviour, not an API this skill calls.
Entities Graphics drives `BatchRendererGroup` internally; the metrics and tools
that expose the result are in
[runtime-creation-and-performance.md](runtime-creation-and-performance.md).

| Subject | What it decides | Source |
|---|---|---|
| What it is | The Unity Engine API connecting Entities Graphics to the rendering backend — the layer that turns entity data into batched draws | [BatchRendererGroup API](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/batch-renderer-group-api.html) |
| Whether to call it | Normal Entities Graphics use never touches it directly; it is handled internally | [BatchRendererGroup API](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/batch-renderer-group-api.html) |
| Unified code path | Unity 2022.1 replaced the earlier implementations with one path, with better performance, flexibility, and test coverage | [BatchRendererGroup API](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/batch-renderer-group-api.html) |
| Why it matters here | It explains *why* draw calls group the way they do, which is what makes a fragmented-batch diagnosis actionable rather than a guess | [BatchRendererGroup API](https://docs.unity3d.com/Packages/com.unity.entities.graphics@6.6/manual/batch-renderer-group-api.html) |

**Critical caveat**: writing custom `BatchRendererGroup` code is outside this
skill's scope. A requirement that genuinely needs it is a rendering-architecture
decision, not an Entities Graphics configuration task.
