# Caching and Log Parsing — what survives between runs, and what the log admits

Source: [Unity Accelerator](https://docs.unity3d.com/Manual/UnityAccelerator.html), [Unity Editor command line arguments](https://docs.unity3d.com/Manual/EditorCommandLineArguments.html), [Log files](https://docs.unity3d.com/Manual/LogFiles.html).
Covers: SKILL.md §4 — **"Keep `Library/` warm without letting correctness depend on it"**, **"Write the log to a file and to stdout, and assert on its content rather than on the absence of an error"**.

Two decisions a job makes about state: what it carries from the last run, and what it reads out of this one.
They are related — a cache reused across an editor upgrade produces import failures that look like code
failures, and the log is the only place that distinction is visible.

## What `Library/` holds and how it is keyed

| Path | Holds | Safe to reuse when |
|---|---|---|
| `Library/Artifacts` | Imported asset results — the bulk of a cold run's cost | The editor version and the platform match the run about to start |
| `Library/PackageCache` | Resolved packages for the committed manifest | The manifest and lock file are unchanged, or package resolution runs again |
| `Library/Bee`, `Library/il2cpp*` | Incremental build data for the scripting backend | The same platform and scripting backend; stale data here produces link-time failures with no source line |
| `Library/ShaderCache` | Compiled shader variants | Freely; a stale entry is recompiled rather than mis-served |
| `Library/*.lock` | The single-instance lock | **Never** — a copied lock file makes a fresh workspace look occupied |

The cache key is therefore at minimum **editor version + build target**, and in practice also the package
manifest's hash. A key that omits the editor version is the classic CI defect: the project upgrades, the old
`Library/` is restored anyway, and the run fails on imports nobody changed.

## Rules the cache must not break

| Rule | Reason |
|---|---|
| A release-candidate build starts from a clean import | A cached artifact is unprovable; the one build that ships is the one build that should be reproducible from the repository alone |
| A cache is never shared between projects or branches with different manifests | Package resolution and asset GUIDs differ, and the failures surface far from the cause |
| A cache is a speed optimisation only — no job step may require its presence | The first run on a new agent has no cache, and any step that depends on one fails on exactly that run |
| The lock file is excluded from whatever is archived or restored | It is per-process state, not cache |

## The Accelerator, when one agent is not enough

| Flag | Effect | Source |
|---|---|---|
| `-cacheServerEndpoint <host:port>` | Points the import pipeline at a shared Accelerator instance | [Unity Accelerator](https://docs.unity3d.com/Manual/UnityAccelerator.html) |
| `-cacheServerNamespacePrefix <name>` | Separates namespaces so unrelated projects do not share entries | same |
| `-cacheServerEnableDownload`, `-cacheServerEnableUpload` | Control direction; a build fleet usually downloads and uploads, a one-off job only downloads | same |

The Accelerator moves import results between agents, so a fresh agent starts warm. It replaces neither the
`Library/` decision above nor the clean-import rule for a release candidate.

## Reading the log

Collect the log as an artifact on every run, including successful ones — a comparison against the last green
run is the fastest way to explain a new failure, and it only exists if it was kept.

| Read for | Line to find | Why it settles something |
|---|---|---|
| The verdict | `Build completed with a result of '<result>'` | States the outcome even when the process exit code does not |
| Compilation | `error CS****` with its file and line | The `-executeMethod` target never ran; nothing after this point is evidence |
| Import trouble | Repeated importer errors on assets nobody touched | Points at a stale or mismatched cache rather than at the change under test |
| Timing | `Refreshing native plugins` or an import step as the last line before a timeout | The run hung rather than failed; a hang and a failure route differently |
| Licence | `Failed to activate/update license` | The run stopped before compilation, per [licensing-and-editor-provisioning.md](licensing-and-editor-provisioning.md) |

Assert on a **positive** line. A grep for errors that finds none is indistinguishable from a run that never
started, and a pipeline that reads the second as success is worse than one with no check at all.
