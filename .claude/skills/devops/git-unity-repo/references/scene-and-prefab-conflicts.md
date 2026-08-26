# Scene and Prefab Conflicts — Serialization Mode, UnityYAMLMerge, and Take-One-Side Resolution

Sources: [Editor settings](https://docs.unity3d.com/Manual/class-EditorManager.html), [Smart merge](https://docs.unity3d.com/Manual/SmartMerge.html), [Text-based scene files](https://docs.unity3d.com/Manual/TextSceneFormat.html), [UnityYAML](https://docs.unity3d.com/Manual/UnityYAML.html), [YAML scene file example](https://docs.unity3d.com/Manual/YAMLSceneExample.html), [git-checkout](https://git-scm.com/docs/git-checkout), [git-merge](https://git-scm.com/docs/git-merge), [gitattributes](https://git-scm.com/docs/gitattributes).
Covers: SKILL.md §4 — "Confirm Asset Serialization is Force Text before treating any scene or prefab as mergeable", "Wire UnityYAMLMerge as the merge driver rather than merging YAML by hand", "Default to taking one side of a scene or prefab conflict wholesale, then reapplying the other side in the Editor", "Never treat a scene that opens as a scene that merged correctly".

Holds the mechanism behind a `.unity`/`.prefab`/`.asset` conflict: the
serialization mode that decides whether a text merge is even possible, the
Unity-aware merge driver, and why the honest default is to discard one side
rather than reconcile YAML. The content decision — which side's objects are
the correct ones — belongs to `unity-engineer`, not here.

- [Precondition — Asset Serialization mode](#precondition--asset-serialization-mode)
- [UnityYAMLMerge — the Unity-aware driver](#unityyamlmerge--the-unity-aware-driver)
- [Wiring the driver](#wiring-the-driver)
- [Taking one side wholesale](#taking-one-side-wholesale)
- [Inspecting a conflict before choosing a side](#inspecting-a-conflict-before-choosing-a-side)
- [Why a scene that loads is not a verified merge](#why-a-scene-that-loads-is-not-a-verified-merge)

## Precondition — Asset Serialization mode

The setting lives at **Edit > Project Settings > Editor > Asset Serialization
> Mode**. It governs whether scenes, prefabs and other native assets are
written as UnityYAML text or as an opaque binary blob, and therefore whether
any of the rest of this file applies.

| Mode | Unity's own wording | Consequence for a merge | Source |
|---|---|---|---|
| `Force Text` | "Convert all assets to Text mode, including new assets. This is the default option." | The only mode under which a diff, a line-level conflict, or UnityYAMLMerge can operate at all | [Editor settings](https://docs.unity3d.com/Manual/class-EditorManager.html) |
| `Force Binary` | "Convert all assets to Binary mode, including new assets." | Every native asset is a binary blob; git can only report a whole-file conflict and the sole resolution is picking one file | [Editor settings](https://docs.unity3d.com/Manual/class-EditorManager.html) |
| `Mixed` | "Assets in Binary mode remain in Binary mode, and Assets in Text mode remain in Text mode. Unity uses Binary mode by default for new assets." | The dangerous middle: existing scenes stay mergeable while every newly created one silently is not | [Editor settings](https://docs.unity3d.com/Manual/class-EditorManager.html) |

**Critical caveat**: `Mixed` produces a project where merge behaviour depends
on when each asset was created, so a scene that "suddenly" conflicts as a
binary blob is not a git regression — it is a new asset that was never text.
Read the mode before diagnosing merge behaviour, not after.

## UnityYAMLMerge — the Unity-aware driver

Unity ships a merge tool that understands its object graph rather than the
file's lines. It is documented for command-line use and for wiring into
third-party version control.

| Item | Value | Source |
|---|---|---|
| Purpose | Merges scene and prefab files "in a semantically correct way" instead of by line | [Smart merge](https://docs.unity3d.com/Manual/SmartMerge.html) |
| Windows path | `C:\Program Files\Unity\Editor\Data\Tools\UnityYAMLMerge.exe` (also `C:\Program Files (x86)\...` for a 32-bit install) | [Smart merge](https://docs.unity3d.com/Manual/SmartMerge.html) |
| macOS path | `/Applications/Unity/Unity.app/Contents/Helpers/UnityYAMLMerge` | [Smart merge](https://docs.unity3d.com/Manual/SmartMerge.html) |
| Invocation | `merge -p <base> <remote> <local> <merged>` | [Smart merge](https://docs.unity3d.com/Manual/SmartMerge.html) |
| Fallback | Ships with `mergespecfile.txt`, which "determines how it handles unresolved conflicts and unknown files", so it can serve as the primary merge tool rather than a scene-only one | [Smart merge](https://docs.unity3d.com/Manual/SmartMerge.html) |
| Hub page | Listed under Unity's Version control topics alongside the Perforce and diff-tool integrations | [Version control](https://docs.unity3d.com/Manual/VersionControl.html) |

**Critical caveat**: an installed-per-version Editor puts the tool under that
version's own directory (e.g. a Unity Hub layout nests it beneath the version
folder), so the two documented paths above are the default-install case, not a
guarantee. Resolve the real path on the machine before writing it into config,
and never commit a machine-local absolute path into a shared file.

## Wiring the driver

Two distinct git mechanisms exist, and they are not interchangeable. A
**mergetool** is invoked on demand by `git mergetool`; a **merge driver** is
invoked automatically by `git merge` for any path whose `merge` attribute names
it. Unity documents only the first.

| Mechanism | Config section | When it runs | Source |
|---|---|---|---|
| Mergetool | `[mergetool "unityyamlmerge"]` with `cmd` | Only when a human runs `git mergetool` after a conflict | [Smart merge](https://docs.unity3d.com/Manual/SmartMerge.html) |
| Merge driver | `[merge "unityyamlmerge"]` with `name`, `driver`, `recursive` | Automatically, during the merge itself, for every path whose attribute selects it | [gitattributes](https://git-scm.com/docs/gitattributes#_defining_a_custom_merge_driver) |

Unity's documented mergetool form, quoted exactly:

```gitconfig
[merge]
	tool = unityyamlmerge

[mergetool "unityyamlmerge"]
	trustExitCode = false
	cmd = '<path to UnityYAMLMerge>' merge -p "$BASE" "$REMOTE" "$LOCAL" "$MERGED"
```

The driver form is not published by Unity. It is derived by mapping Unity's own
`merge -p <base> <remote> <local> <merged>` argument order onto git's driver
placeholders — `%O` ancestor, `%B` other branch, `%A` current version and the
file the result must be written to:

```gitconfig
[merge "unityyamlmerge"]
	name = Unity SmartMerge
	driver = '/Applications/Unity/Unity.app/Contents/Helpers/UnityYAMLMerge' merge -p %O %B %A %A
	recursive = binary
```

| Field | Meaning | Source |
|---|---|---|
| `merge.<driver>.name` | "gives the driver a human-readable name" — shown in git's own messages | [gitattributes](https://git-scm.com/docs/gitattributes#_defining_a_custom_merge_driver) |
| `merge.<driver>.driver` | The command line, constructed from `%O` (common ancestor), `%A` (current version, and the output path), `%B` (other branch's version) | [gitattributes](https://git-scm.com/docs/gitattributes#_defining_a_custom_merge_driver) |
| `merge.<driver>.recursive` | Which driver to use for the internal merge of intermediate ancestors; `binary` keeps recursive-merge ancestors out of the YAML tool | [gitattributes](https://git-scm.com/docs/gitattributes#_defining_a_custom_merge_driver) |
| `trustExitCode = false` | Do not treat the tool's exit status as proof the merge succeeded — Unity's own documented value | [Smart merge](https://docs.unity3d.com/Manual/SmartMerge.html) |
| Argument mapping onto `%O %B %A %A` | Derived from Unity's CLI order, not published by Unity as a driver line | synthesized |

The attribute side selects the driver per pattern. Every extension below is a
UnityYAML native asset when Asset Serialization is `Force Text`:

```gitattributes
*.unity           merge=unityyamlmerge eol=lf
*.prefab          merge=unityyamlmerge eol=lf
*.asset           merge=unityyamlmerge eol=lf
*.controller      merge=unityyamlmerge eol=lf
*.anim            merge=unityyamlmerge eol=lf
*.physicMaterial  merge=unityyamlmerge eol=lf
*.mat             merge=unityyamlmerge eol=lf
```

| Pattern | Asset it covers | Source |
|---|---|---|
| `*.unity` | Scenes | [Text-based scene files](https://docs.unity3d.com/Manual/TextSceneFormat.html) |
| `*.prefab` | Prefabs, including prefab variants and nested prefabs | [Text-based scene files](https://docs.unity3d.com/Manual/TextSceneFormat.html) |
| `*.asset` | ScriptableObject assets and most `ProjectSettings/` files | [Text-based scene files](https://docs.unity3d.com/Manual/TextSceneFormat.html) |
| `*.controller`, `*.anim` | Animator Controllers and Animation clips | synthesized |
| `*.physicMaterial`, `*.mat` | Physics materials and materials | synthesized |
| `eol=lf` | Prevents a CRLF rewrite from making every line of a scene appear changed on a Windows checkout | [gitattributes](https://git-scm.com/docs/gitattributes#_end_of_line_conversion) |
| `merge=<driver>` semantics | "3-way merge is performed using the specified custom merge driver" | [gitattributes](https://git-scm.com/docs/gitattributes#_performing_a_three_way_merge) |

## Taking one side wholesale

When the driver is absent or leaves conflicts, the defensible resolution is to
keep one side's file intact and reapply the other side's intent through the
Editor. Git records three versions of a conflicted path in the index, and these
commands select among them.

| Command | Effect | Source |
|---|---|---|
| `git checkout --ours <path>` | Writes index "stage #2 (`ours`)" — the version from `HEAD` — over the working-tree file | [git-checkout](https://git-scm.com/docs/git-checkout) |
| `git checkout --theirs <path>` | Writes index "stage #3 (`theirs`)" — the version from `MERGE_HEAD` | [git-checkout](https://git-scm.com/docs/git-checkout) |
| `git ls-files -u <path>` | Lists the three unmerged stages so it is visible which sides actually differ before one is discarded | [git-merge](https://git-scm.com/docs/git-merge) |
| `git checkout -m <path>` | Recreates the conflicted state with markers, undoing a resolution attempt without restarting the merge | [git-checkout](https://git-scm.com/docs/git-checkout) |
| `git checkout --conflict=diff3 <path>` | Same as `-m`, but adds the `\|\|\|\|\|\|\|` section holding the common ancestor, which is what makes a Unity YAML hunk legible as "added on one side" versus "changed on both" | [git-checkout](https://git-scm.com/docs/git-checkout), [git-merge](https://git-scm.com/docs/git-merge) |
| `git checkout --conflict=zdiff3 <path>` | `diff3` with matching lines near a hunk's edges hoisted out, shrinking the conflict region | [git-merge](https://git-scm.com/docs/git-merge) |
| Index stage numbering | Stage 1 is the common ancestor, stage 2 is `HEAD`, stage 3 is `MERGE_HEAD` | [git-merge](https://git-scm.com/docs/git-merge) |

**Critical caveat**: `--ours` and `--theirs` invert during a rebase. Git's own
wording: "during `git rebase` and `git pull --rebase`, `ours` and `theirs` may
appear swapped; `--ours` gives the version from the branch the changes are
rebased onto, while `--theirs` gives the version from the branch that holds
your work that is being rebased." Choosing a side by name rather than by
verifying which operation is in flight is how the wrong scene gets kept, and
because the result is a valid scene file nothing downstream reports an error.
Check for a rebase in progress before naming a side.

## Inspecting a conflict before choosing a side

| Fact | Why it decides something | Source |
|---|---|---|
| UnityYAML is "a custom-optimized YAML library" that does not implement the full YAML spec | A generic YAML-aware merge or formatting tool can emit valid YAML that Unity cannot load | [UnityYAML](https://docs.unity3d.com/Manual/UnityYAML.html) |
| Comments are not recognized by UnityYAML | A resolution cannot leave an explanatory comment behind in the file | [UnityYAML](https://docs.unity3d.com/Manual/UnityYAML.html) |
| Multiple documents in one file are not handled | The document-per-object layout is fixed; a merge cannot restructure it | [UnityYAML](https://docs.unity3d.com/Manual/UnityYAML.html) |
| A GameObject lists its components as `m_Component: - component: {fileID: 330585546}` | The membership edge lives on the GameObject, so a component's own document surviving a merge proves nothing about it still being attached | [YAML scene file example](https://docs.unity3d.com/Manual/YAMLSceneExample.html) |
| Each component points back with `m_GameObject: {fileID: 330585543}` | The link is two-sided, so a one-sided hunk resolution can leave it half-formed | [YAML scene file example](https://docs.unity3d.com/Manual/YAMLSceneExample.html) |
| Hierarchy lives in the Transform's `m_Children`, and scene roots in a `SceneRoots` document | Parenting and root membership are separate lists that a line merge can update inconsistently | [YAML scene file example](https://docs.unity3d.com/Manual/YAMLSceneExample.html) |

## Why a scene that loads is not a verified merge

Unity loading a file proves the YAML parsed and the `fileID` graph was walkable
enough to instantiate — not that the graph says what either author meant.

| Failure | Mechanism | What the Editor shows | Source |
|---|---|---|---|
| Dangling `fileID` | A hunk kept a reference whose target document came from the discarded side, so the reference resolves to nothing | Loads; the field reads as `None`/missing at runtime rather than erroring on open | [YAML scene file example](https://docs.unity3d.com/Manual/YAMLSceneExample.html) |
| Duplicated component | Both sides added the same component as separate documents with distinct `fileID`s, and both entries survived in `m_Component` | Loads; two instances of the component run, doubling whatever it does per frame | [YAML scene file example](https://docs.unity3d.com/Manual/YAMLSceneExample.html) |
| Orphaned component document | The component document survived but its `fileID` was dropped from the owning GameObject's `m_Component` list | Loads; the component is simply absent from the Inspector, with no diagnostic | [YAML scene file example](https://docs.unity3d.com/Manual/YAMLSceneExample.html) |
| Broken `m_Children` ordering | A Transform's `m_Children` merged into a different order than either side had | Loads; sibling draw order and any index-based lookup shift silently | [YAML scene file example](https://docs.unity3d.com/Manual/YAMLSceneExample.html) |
| Lost `SceneRoots` entry | A root Transform's `fileID` did not survive into the `SceneRoots` document | Loads; the object exists in the file but not in the hierarchy | [YAML scene file example](https://docs.unity3d.com/Manual/YAMLSceneExample.html) |
| Reparented-versus-deleted collision | One side moved an object under a new parent while the other deleted the old parent | Loads, with the object attached under whichever parent survived | synthesized |

Every row above yields a green `git status`, a clean parse, and a project that
misbehaves at runtime — which is why the objects the merge actually touched are
the verification target, and why the file cannot be signed off from the fact
that the Editor accepted it. Reference resolution across assets runs on GUIDs
rather than `fileID`s and fails the same silent way; see
[meta-files-and-guids.md](meta-files-and-guids.md).
