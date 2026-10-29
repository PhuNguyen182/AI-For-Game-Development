# Frame Debugger and Profile Analyzer

Docs: https://docs.unity3d.com/Manual/FrameDebugger.html · https://docs.unity3d.com/Manual/com.unity.performance.profile-analyzer.html

Fixing what either reveals (batching setup, material variants, GPU instancing) is `unity-urp-rendering` / `unity-performance-engineer`.

## Frame Debugger
| Subject | Rule |
|---|---|
| Draw-call list | Freezes one frame and replays calls in submission order; the only view of what reached the GPU |
| Batch-break reason | Why a call could not batch with the previous (material, texture, shadow flag, render state): the answer to "why did draw calls jump" |
| No timing data | A call that appears once is not cheap and a long list is not the bottleneck; pair with Rendering or GPU Usage for cost |
| Remote use | Attaches to a connected development player, so a device-only batching problem is inspected where it happens |
| Shader property panel | Properties and keywords of the selected call; confirms a "wrong variant" suspicion |

## Profile Analyzer
| Subject | Rule |
|---|---|
| Aggregation | Median, mean and distribution per marker over a capture |
| Compare view | Two captures side by side with per-marker delta; surfaces a regression hidden in an improved total |
| Input | Saved Profiler captures; a comparison cannot be rebuilt from an unsaved session |
| Comparability | Same device, scene and similar frame count, or the delta measures conditions |
| Median vs mean | A few bad frames drag the mean; the median is the frame a player sees. Quote both when they disagree |

A change that lowers median frame time but raises the maximum has traded steady cost for hitching, usually a regression on a fixed budget: report both.
