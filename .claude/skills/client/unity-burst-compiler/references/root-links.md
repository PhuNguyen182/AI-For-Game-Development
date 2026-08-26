# Root Links — Burst 1.8

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder to the Burst package, version 1.8. Anything
this skill cites resolves under one of these roots; anything that does not is
out of scope for the skill, not merely undocumented here.

| Root | Holds | Source |
|---|---|---|
| Manual | HPC# subset, compilation model, Inspector, AOT settings, aliasing | [Burst Manual index](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/index.html) |
| Scripting API | `BurstCompileAttribute`, `FloatMode`, `FunctionPointer<T>`, `SharedStatic<T>` | [Burst API index](https://docs.unity3d.com/Packages/com.unity.burst@1.8/api/index.html) |

Every other link in this `references/` folder is a specific page under these
roots, pinned to `@1.8`. Substitute the version the project actually installs
(`Window > Package Manager` or `manifest.json`) before relying on a member;
nearby versions generally keep the same page slugs, but option defaults have
changed between releases and the pinned page is the one to trust.
