# Root Links — Unity Manual, Scripting API, and the Hub CLI

Source: [Unity Manual](https://docs.unity3d.com/Manual/index.html), [Unity Scripting API](https://docs.unity3d.com/ScriptReference/index.html), [Unity Hub Manual](https://docs.unity3d.com/hub/manual/index.html).
Covers: SKILL.md §4 — **"Pin the editor version from `ProjectVersion.txt` before writing anything else"**.

Unity publishes one documentation set per editor version, and `docs.unity3d.com` without a version segment
serves the **current** release rather than the one this project builds with. Every link in this folder is
written against the unversioned root for that reason; the authority for what the project's editor actually
accepts is the binary itself, not the page. Flags are added, renamed and retired between versions with no
redirect, so confirm any flag this folder names against `Unity -help` — or the versioned page at
`https://docs.unity3d.com/<version>/Documentation/Manual/` — before a job depends on it.

| Root | Holds | Source |
|---|---|---|
| Editor command line | The full argument list a headless invocation is built from | [Unity Editor command line arguments](https://docs.unity3d.com/Manual/EditorCommandLineArguments.html) |
| Scripting API — build | `BuildPipeline`, `BuildPlayerOptions`, `BuildReport`, `EditorUserBuildSettings`, `PlayerSettings` | [Scripting API index](https://docs.unity3d.com/ScriptReference/index.html) |
| Log files | Where the editor writes when nobody passed `-logFile`, per platform | [Log files](https://docs.unity3d.com/Manual/LogFiles.html) |
| Licensing | Seat activation, manual activation files, and the licensing client | [Managing your Unity licence](https://docs.unity3d.com/Manual/ManagingYourUnityLicense.html) |
| Hub CLI | Headless editor and module installation on an agent | [Unity Hub CLI](https://docs.unity3d.com/hub/manual/HubCLI.html) |
| Accelerator | The shared import cache a fleet of agents can point at | [Unity Accelerator](https://docs.unity3d.com/Manual/UnityAccelerator.html) |

## The version pin lives in the project, not here

| File | What it states | Why the job needs it |
|---|---|---|
| `ProjectSettings/ProjectVersion.txt` | `m_EditorVersion` — the exact editor build | Any other version silently upgrades the project on open, and that upgrade is committed to the workspace |
| same file | `m_EditorVersionWithRevision` — version plus the changeset in parentheses | The Hub CLI needs the changeset to install a version that is no longer the latest |

Read both from the repository the job checked out. A version supplied in a job parameter instead is a second
source of truth that drifts the first time someone upgrades the project and forgets the pipeline.