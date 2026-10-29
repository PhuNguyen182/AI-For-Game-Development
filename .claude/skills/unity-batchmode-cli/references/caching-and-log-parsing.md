# Caching and log parsing

Source: [Unity Accelerator](https://docs.unity3d.com/Manual/UnityAccelerator.html), [Command line arguments](https://docs.unity3d.com/Manual/EditorCommandLineArguments.html).

A cache reused across an editor upgrade produces import failures that look like code failures; the log is where that shows.

## `Library/`
| Path | Reuse when |
|---|---|
| `Library/Artifacts` | Editor version and platform match |
| `Library/PackageCache` | Manifest and lock unchanged, or resolution reruns |
| `Library/Bee`, `Library/il2cpp*` | Same platform and scripting backend; stale data gives link-time failures with no source line |
| `Library/ShaderCache` | Freely; stale entries are recompiled |
| `Library/*.lock` | Never; a copied lock makes a fresh workspace look occupied |

Cache key: editor version + build target + package manifest hash. Omitting the editor version is the classic defect.

Rules:
- A release candidate starts from a clean import.
- Never share a cache between projects or branches with different manifests.
- No step may require the cache; the first run on a new agent has none.
- Exclude the lock file from archive and restore.

## Accelerator
- `-cacheServerEndpoint <host:port>`: shared import cache.
- `-cacheServerNamespacePrefix <name>`: separate unrelated projects.
- `-cacheServerEnableDownload`, `-cacheServerEnableUpload`: direction; a fleet does both, a one-off job only downloads.

It does not replace the `Library/` decision or the clean-import rule.

## Reading the log
Keep the log as an artifact on every run, green ones too, to diff against the last green.

| Read for | Line | Settles |
|---|---|---|
| Verdict | `Build completed with a result of '<result>'` | Outcome even when the exit code lies |
| Compilation | `error CS****` | `-executeMethod` never ran |
| Import trouble | Repeated importer errors on untouched assets | Stale or mismatched cache |
| Hang | `Refreshing native plugins` or an import step as last line before a timeout | Hang, not failure; routes differently. Set a job-level timeout and pass `-accept-apiupdate` so the prompt is answered rather than waited on |
| Licence | `Failed to activate/update license` | Stopped before compilation |

Assert on a positive line: a grep that finds no error equals a run that never started.
