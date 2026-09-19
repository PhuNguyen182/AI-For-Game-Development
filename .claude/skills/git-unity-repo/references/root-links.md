# Root Links — Unity Manual (unversioned root) and Git LFS

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder to two upstreams: the Unity Manual for
serialization, `.meta`/GUID and project-directory behaviour, and the Git LFS
and Git manual pages for the version-control side. Anything this skill cites
resolves under one of these roots; a Unity behaviour not documented under them
is out of scope for the skill rather than merely unlinked here.

## Version pin

This repository holds **no `ProjectSettings/ProjectVersion.txt`** — its root
contains only `README.md`, so there is no Unity project checked in here to
read a version from. Rather than invent a pin, every Unity link in this folder
uses the **unversioned Manual root** (`https://docs.unity3d.com/Manual/<Page>.html`),
which redirects to whatever release Unity currently publishes as latest; at the
time of authoring that root served **Unity 6.5** (build `6000.5`, page build
date 2026-08-22). Menu paths and Editor setting locations in the sibling files
are therefore 6.5-accurate and unverified against any older Editor — confirm a
setting path against the installed version before acting on it, which is the
same check SKILL.md's own guardrail about unstated Unity versions demands. Once
a Unity project does land in this repository, re-pin these links to
`https://docs.unity3d.com/<major>.<minor>/Documentation/Manual/<Page>.html`
using that file's version, and keep the pin identical across every file here.

| Root | Holds | Source |
|---|---|---|
| Unity Manual index | Every conceptual and how-to page this skill's Unity claims come from | [Unity User Manual](https://docs.unity3d.com/Manual/index.html) |
| Manual — Version control | The hub for Unity's VCS material: integrations, SmartMerge, diff tooling | [Version control](https://docs.unity3d.com/Manual/VersionControl.html) |
| Manual — Version control integrations | Perforce/UVCS integration settings, and the Hidden vs. Visible `.meta` files mode | [Version control integrations](https://docs.unity3d.com/Manual/Versioncontrolintegration.html) |
| Manual — Smart merge | UnityYAMLMerge: per-platform executable path, git wiring, `mergespecfile.txt` fallback | [Smart merge](https://docs.unity3d.com/Manual/SmartMerge.html) |
| Manual — Editor settings | Asset Serialization mode (Mixed / Force Binary / Force Text) under Edit > Project Settings > Editor | [Editor settings](https://docs.unity3d.com/Manual/class-EditorManager.html) |
| Manual — Asset metadata | What a `.meta` holds, asset IDs, and the move/rename-outside-Unity rule | [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html) |
| Manual — Text-based scene files | The text serialization sub-tree: UnityYAML dialect, scene example, class ID reference | [Text-based scene files](https://docs.unity3d.com/Manual/TextSceneFormat.html) |
| Manual — Default project directories | Which top-level folders Unity generates and which it says to exclude from version control | [Default project directories](https://docs.unity3d.com/Manual/default-directories.html) |
| Manual — Package Manager files | `Packages/manifest.json` properties, and the lock file's purpose and `enableLockFile` | [Project manifest file](https://docs.unity3d.com/Manual/upm-manifestPrj.html), [Lock files](https://docs.unity3d.com/Manual/upm-conflicts-auto.html) |
| Git LFS home | Install, `git lfs track`, and the pointer-substitution model in one page | [Git Large File Storage](https://git-lfs.com) |
| Git LFS man pages | Per-subcommand reference (`install`, `fsck`, `pull`, `checkout`, `ls-files`, `env`) | [git-lfs/docs/man](https://github.com/git-lfs/git-lfs/tree/main/docs/man) |
| Git reference | Conflict stages, `--ours`/`--theirs`, attribute and merge-driver syntax | [git-checkout](https://git-scm.com/docs/git-checkout), [git-merge](https://git-scm.com/docs/git-merge), [gitattributes](https://git-scm.com/docs/gitattributes) |

## Topic → file map

| Topic | File | Source |
|---|---|---|
| Asset Serialization modes and where the setting lives | [scene-and-prefab-conflicts.md](scene-and-prefab-conflicts.md) | [Editor settings](https://docs.unity3d.com/Manual/class-EditorManager.html) |
| UnityYAMLMerge executable paths, `.gitattributes` wiring, `merge.*.driver`, fallback | [scene-and-prefab-conflicts.md](scene-and-prefab-conflicts.md) | [Smart merge](https://docs.unity3d.com/Manual/SmartMerge.html), [gitattributes](https://git-scm.com/docs/gitattributes#_defining_a_custom_merge_driver) |
| Take-one-side resolution, `--ours`/`--theirs`, the rebase inversion, `--conflict=diff3` | [scene-and-prefab-conflicts.md](scene-and-prefab-conflicts.md) | [git-checkout](https://git-scm.com/docs/git-checkout), [git-merge](https://git-scm.com/docs/git-merge) |
| Why a scene that parses and loads is not a verified merge (`fileID`, `m_Children`) | [scene-and-prefab-conflicts.md](scene-and-prefab-conflicts.md) | [YAML scene file example](https://docs.unity3d.com/Manual/YAMLSceneExample.html) |
| `.meta` contents, GUID-based reference resolution, and the silent break chain | [meta-files-and-guids.md](meta-files-and-guids.md) | [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html) |
| Per-case `.meta` failures: moved, deleted, orphaned, duplicated GUID, conflicted | [meta-files-and-guids.md](meta-files-and-guids.md) | [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html), [Refreshing the Asset Database](https://docs.unity3d.com/Manual/AssetDatabaseRefreshing.html) |
| The ignore/track surface with a reason per entry, and what Unity regenerates | [ignore-surface-and-lfs.md](ignore-surface-and-lfs.md) | [Default project directories](https://docs.unity3d.com/Manual/default-directories.html) |
| `ProjectVersion.txt` and `packages-lock.json` as single-decision files | [ignore-surface-and-lfs.md](ignore-surface-and-lfs.md) | [Lock files](https://docs.unity3d.com/Manual/upm-conflicts-auto.html) |
| LFS `.gitattributes` patterns, pointer-file symptom, and the LFS command surface | [ignore-surface-and-lfs.md](ignore-surface-and-lfs.md) | [Git Large File Storage](https://git-lfs.com), [git-lfs/docs/man](https://github.com/git-lfs/git-lfs/tree/main/docs/man) |

## Disclosed gaps

| Page / area | Issue |
|---|---|
| `ProjectSettings/ProjectVersion.txt` | Absent from this repository, so the Unity version could not be read. Links use the unversioned Manual root instead of a pin, per the Version pin section above. |
| `.gitattributes` wiring for UnityYAMLMerge | [Smart merge](https://docs.unity3d.com/Manual/SmartMerge.html) documents only the `[mergetool "unityyamlmerge"]` form invoked interactively via `git mergetool`. It does **not** document `*.unity merge=unityyamlmerge` or a `merge.unityyamlmerge.driver` entry; that shape comes from [gitattributes](https://git-scm.com/docs/gitattributes#_defining_a_custom_merge_driver)'s generic custom-merge-driver contract and is marked `synthesized` where it appears. |
| `ProjectVersion.txt` conflict handling | Not documented by Unity as a version-control topic on any page fetched here; its rows in [ignore-surface-and-lfs.md](ignore-surface-and-lfs.md) are `synthesized` from the file's single-value content and the Editor's upgrade-on-open behaviour. |
| Unity ignore list beyond the documented folders | [Default project directories](https://docs.unity3d.com/Manual/default-directories.html) states the exclusion rule only for `Library/`, `Temp/` and `UserSettings/`. Entries for `Logs/`, `obj/`, IDE project files, build outputs, `.vs/`, `.idea/` and crash-report folders are `synthesized` from what generates them, not quoted from Unity. |
| `Assets > Reimport` menu path | No dedicated Manual page for the menu command resolved (`reimport-assets.html` returns 404). [Refreshing the Asset Database](https://docs.unity3d.com/Manual/AssetDatabaseRefreshing.html) is cited instead for the refresh mechanism the command drives. |
| Duplicate GUIDs from a copied asset tree | Not covered by any Unity page fetched here; the row is `synthesized` from the GUID-uniqueness property [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html) does state. |
| `mergespecfile.txt` contents | [Smart merge](https://docs.unity3d.com/Manual/SmartMerge.html) names the file and its role but the fetched text does not enumerate its syntax — treat any specific fallback rule as needing a check against the shipped file in the Editor's `Tools` directory. |
