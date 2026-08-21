# Volumes & Environment — Exposure, Fog, Sky

Sources: [Local Volumetric Fog](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/Local-Volumetric-Fog.html), [HDRP Manual index](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/index.html).
Covers: SKILL.md §4 — **"Author environment through Volume overrides, not per-camera values"**.

HDRP routes environment behaviour — not just post-processing — through the
Volume system, so exposure, fog, and sky are authored the same way a bloom
override is. The post-process effect catalog itself belongs to
`unity-post-processing`; this file covers the environment side HDRP alone has.

| Subject | What it decides | Source |
|---|---|---|
| Volume scope | Global applies wherever the camera's volume layer mask sees it; local requires a trigger collider and applies inside it | [HDRP Manual index](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/index.html) |
| Priority | Decides which volume wins where several overlap — how a room overrides the world baseline | [HDRP Manual index](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/index.html) |
| Blend Distance | The fade band outside a local volume; zero produces a visible pop as the camera crosses the boundary | [HDRP Manual index](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/index.html) |
| Exposure override | HDRP is physically based, so exposure is an authored environment property rather than a camera setting | [HDRP Manual index](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/index.html) |
| Visual Environment and Sky | Selects and configures the sky type the scene renders and lights from | [HDRP Manual index](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/index.html) |
| Fog override | Global fog and its volumetric component, gated by the Asset's Volumetrics feature | [Local Volumetric Fog](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/Local-Volumetric-Fog.html) |
| Local Volumetric Fog | A per-region volumetric density field, distinct from the global fog override | [Local Volumetric Fog](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/Local-Volumetric-Fog.html) |

**Critical caveat**: the manual's Volumes and Lighting sections carry the full
override catalog, which is larger than this list and changes between versions —
browse the index for an override not named here rather than assuming it does
not exist.
