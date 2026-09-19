# Debugging Tools — Entities Hierarchy & Systems Windows

Sources: [Entities Hierarchy window](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/editor-hierarchy-window.html), [Systems window](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/editor-systems-window.html).
Covers: SKILL.md §4 — **"Confirm the built layout in the Entities Hierarchy and Systems windows before claiming it"**.

Archetype membership and system update order are emergent results of baking and
attribute resolution, not declarations — these two windows are where the built
result is read back. Frame-time evidence for a performance claim comes from
`unity-profiler-diagnostics`, not from here.

| Window | What it decides | Source |
|---|---|---|
| `Window > Entities > Hierarchy` | Shows an entity's *actual* baked component set, per World, so a component assumed present can be confirmed or disproved | [Entities Hierarchy window](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/editor-hierarchy-window.html) |
| Authoring / Runtime / Mixed data modes | Switches between the GameObject view and the baked entity view — the direct way to see whether baking produced what the authoring data implied | [Entities Hierarchy window](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/editor-hierarchy-window.html) |
| `Window > Entities > Systems` | Shows the resolved system hierarchy grouped by `ComponentSystemGroup`, which is the only reliable check that `[UpdateBefore]`/`[UpdateAfter]` had the intended effect | [Systems window](https://docs.unity3d.com/Packages/com.unity.entities@6.6/manual/editor-systems-window.html) |

**Critical caveat**: a system that never appears in the Systems window did not
fail to order — it failed to be created at all, usually because its query
matched nothing and it was skipped, or because it landed in a World the window
is not showing. Check presence before debugging order.
