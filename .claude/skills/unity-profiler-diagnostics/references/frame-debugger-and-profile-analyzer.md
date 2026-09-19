# Frame Debugger and Profile Analyzer — batch attribution and before-and-after proof

Sources: [Frame Debugger](https://docs.unity3d.com/Manual/FrameDebugger.html), [Profile Analyzer](https://docs.unity3d.com/Manual/com.unity.performance.profile-analyzer.html), [Rendering module](https://docs.unity3d.com/Manual/ProfilerRendering.html).
Covers: SKILL.md §4 — **"Take a batching or draw-call regression to the Frame Debugger, not to a timing module"**, **"Back any before-and-after claim with the Profile Analyzer"**.

Two tools that answer questions no Profiler module can. The Frame Debugger
explains a draw-call sequence and never times it; the Profile Analyzer turns
many frames into one defensible figure. Fixing what either reveals — batching
setup, material variants, GPU instancing — is `unity-urp-rendering`'s and
`unity-engineer`'s work.

## Frame Debugger

| Subject | What it decides | Source |
|---|---|---|
| Draw-call list | Freezes one frame and replays its calls in submission order, so the render target's state at any point is inspectable — this is the only view of what actually reached the GPU | [Frame Debugger](https://docs.unity3d.com/Manual/FrameDebugger.html) |
| Batch-break reason | States why a call could not be batched with the one before it — a different material, a different texture, a shadow-casting flag, a changed render state — which is the actual answer to "why did draw calls jump" | [Frame Debugger](https://docs.unity3d.com/Manual/FrameDebugger.html) |
| No timing data | It reports ordering and state only; a call that appears once is not thereby cheap, and a long list is not thereby the bottleneck — pair it with the Rendering or GPU Usage module for cost | [Frame Debugger](https://docs.unity3d.com/Manual/FrameDebugger.html) |
| Remote use | Attaches to a connected development player, so a batching problem that only appears on device is inspectable where it happens rather than being reproduced in the Editor | [Frame Debugger](https://docs.unity3d.com/Manual/FrameDebugger.html) |
| Shader property panel | Shows the properties and keywords the selected call was issued with, which is how a "wrong variant" suspicion is confirmed instead of assumed | [Frame Debugger](https://docs.unity3d.com/Manual/FrameDebugger.html) |

## Profile Analyzer

| Subject | What it decides | Source |
|---|---|---|
| Aggregation across frames | Produces median, mean, and distribution per marker over a whole capture, which is what makes a claim about typical behaviour possible at all | [Profile Analyzer](https://docs.unity3d.com/Manual/com.unity.performance.profile-analyzer.html) |
| Compare view | Loads two captures side by side and reports the per-marker delta, so a regression hidden inside an improved total still surfaces | [Profile Analyzer](https://docs.unity3d.com/Manual/com.unity.performance.profile-analyzer.html) |
| Input | Consumes Profiler captures, so both sides must be saved at capture time; there is no way to reconstruct a comparison from a session that was not saved | [Profile Analyzer](https://docs.unity3d.com/Manual/com.unity.performance.profile-analyzer.html) |
| Comparability | The two captures must come from the same device, the same scene, and a similar frame count, or the delta measures the difference in conditions rather than the change | [Profile Analyzer](https://docs.unity3d.com/Manual/com.unity.performance.profile-analyzer.html) |
| Median over mean | A few catastrophic frames drag the mean while the median describes the frame a player actually sees — quote both when they disagree, because the disagreement is itself the finding | [Profile Analyzer](https://docs.unity3d.com/Manual/com.unity.performance.profile-analyzer.html) |

**Critical caveat**: a change that lowers median frame time while raising the
maximum has traded steady cost for hitching. On a fixed frame budget that is
usually a regression, not a win — report both numbers rather than the one
that supports the change.
