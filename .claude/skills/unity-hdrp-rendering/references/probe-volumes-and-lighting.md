# Adaptive Probe Volumes — Enablement & Boundary

Sources: [Adaptive Probe Volumes](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/probevolumes.html), [Understanding Adaptive Probe Volumes](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/probevolumes-concept.html), [Fix issues with Adaptive Probe Volumes](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/probevolumes-fixissues.html).
Covers: SKILL.md §4 — **"Enable Adaptive Probe Volumes in the Asset and hand placement and baking to the lighting owner"**.

What this skill owns about APV — making it available and knowing what that
requires — and where the line to `unity-lighting` falls. Probe placement,
density tuning, and reading a bad bake are lighting work, not pipeline
configuration.

| Subject | What it decides | Source |
|---|---|---|
| What APV is | Automatically placed probe volumes replacing manually positioned Light Probes for baked indirect lighting | [Understanding APV](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/probevolumes-concept.html) |
| Brick placement | Probes are laid out as bricks whose density follows scene geometry, so geometry changes invalidate the bake | [Understanding APV](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/probevolumes-concept.html) |
| Asset-level enablement | APV must be enabled in the pipeline configuration before any of it is available in a scene — this skill's half | [Adaptive Probe Volumes](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/probevolumes.html) |
| Baking requirement | Indirect lighting must be baked; an unbaked scene shows no APV contribution, which reads as APV not working | [Use Adaptive Probe Volumes](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/probevolumes-use.html) |
| Leaking and seams | The characteristic APV artifacts, with documented adjustment tools — `unity-lighting`'s territory to resolve | [Fix issues with APV](https://docs.unity3d.com/Packages/com.unity.render-pipelines.high-definition@17.5/manual/probevolumes-fixissues.html) |

**Critical caveat**: "APV is not working" splits cleanly into two owners. Not
enabled in the pipeline configuration is this skill's; enabled but unbaked,
leaking, or badly placed is `unity-lighting`'s. Establish which before
starting.
