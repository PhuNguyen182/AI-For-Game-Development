# Scene and Prefab Conflicts

Sources (Docs bases in SKILL.md): [editor] Manual/class-EditorManager.html, [smart] Manual/SmartMerge.html, [yaml] Manual/UnityYAML.html, [scene] Manual/YAMLSceneExample.html, [attr] git-scm.com/docs/gitattributes, [co] git-scm.com/docs/git-checkout, [merge] git-scm.com/docs/git-merge.

## Serialization mode (Edit > Project Settings > Editor > Asset Serialization > Mode) [editor]

| Mode | Merge consequence |
|---|---|
| `Force Text` (default) | The only mode where line diffs, conflicts and UnityYAMLMerge work |
| `Force Binary` | Whole-file conflict only; resolution is picking one file |
| `Mixed` | Existing text assets stay mergeable, new assets default to Binary; a scene that "suddenly" conflicts as a blob is a new binary asset, not a git regression |

## UnityYAMLMerge [smart]

| Item | Value |
|---|---|
| Windows | `C:\Program Files\Unity\Editor\Data\Tools\UnityYAMLMerge.exe` |
| macOS | `/Applications/Unity/Unity.app/Contents/Helpers/UnityYAMLMerge` |
| Invocation | `merge -p <base> <remote> <local> <merged>`; the tool's own usage names `<left>` = theirs, `<right>` = mine |
| Unattended run | Add `-h` (headless: no error dialogs) and `--fallback none`; otherwise the shipped `mergespecfile.txt` hands an unresolved conflict to a GUI tool, which hangs a merge with no one at the screen (both flags in the usage text of Unity 6000.0's `UnityYAMLMerge.exe`). With them, a same-field clash exits non-zero and writes the left (theirs) value with no markers: the file looks resolved and is not (`resolve-merge-conflicts` step 6) |
| Fallback | `mergespecfile.txt` decides handling of unresolved conflicts and unknown files; its syntax is not documented, so check the shipped file in the Editor's `Tools` directory |

**Caveat:** those paths are default-install only (Unity Hub nests the tool under the version folder). Resolve the real path per machine and never commit it.

## Wiring

Unity documents only the interactive mergetool. The automatic merge driver form below is derived by mapping Unity's argument order onto git's `%O` ancestor, `%B` other, `%A` current/output placeholders [attr]; it is not published by Unity.

```gitconfig
[merge]
	tool = unityyamlmerge

[mergetool]
	keepBackup = false

[mergetool "unityyamlmerge"]
	trustExitCode = false
	cmd = '<path to UnityYAMLMerge>' merge -p "$BASE" "$REMOTE" "$LOCAL" "$MERGED"

[merge "unityyamlmerge"]
	name = Unity SmartMerge
	driver = '<path to UnityYAMLMerge>' merge -h -p --fallback none %O %B %A %A
	recursive = binary
```

```gitattributes
*.unity          merge=unityyamlmerge -text
*.prefab         merge=unityyamlmerge -text
*.asset          merge=unityyamlmerge -text
*.controller     merge=unityyamlmerge -text
*.anim           merge=unityyamlmerge -text
*.physicMaterial merge=unityyamlmerge -text
*.mat            merge=unityyamlmerge -text
```

`-text` turns off end-of-line conversion, so `core.autocrlf=true` cannot mark every line of a scene changed; files are stored byte-for-byte as Unity's serializer wrote them (LF in practice; the Manual does not state it). Never `eol=lf`: it implies `text`, and some `.asset` files are binary under Force Text (`LightingData.asset`, baked NavMesh and terrain data), so `git add` rewrites CR LF byte pairs inside them (checked on git 2.56: a NUL-bearing file lost its CR bytes). `*.controller`, `*.anim`, `*.physicMaterial`, `*.mat` are included on the assumption they are UnityYAML under Force Text. The driver runs during `merge`, `rebase`, `cherry-pick` and `revert`; the mergetool section runs only on `git mergetool`, which is for a person's terminal (it prompts, and `keepBackup` would leave `*.orig` files Unity gives a `.meta`). An agent runs the tool directly on the three stages (`resolve-merge-conflicts` step 6).

## Taking one side

| Command | Effect |
|---|---|
| `git ls-files -u <path>` | Lists the unmerged stages (1 ancestor, 2 `HEAD`, 3 `MERGE_HEAD`) so you see which sides differ before discarding one |
| `git checkout --ours <path>` / `--theirs <path>` | Writes stage 2 / stage 3 over the working file |
| `git checkout -m <path>` | Recreates the conflict markers, undoing a resolution attempt |
| `git checkout --conflict=diff3 <path>` | As `-m` plus the ancestor section, to tell "added on one side" from "changed on both"; `zdiff3` shrinks the region |

**Caveat:** during `git rebase` and `git pull --rebase`, `--ours` is the branch being rebased onto and `--theirs` is your own work being replayed. Check whether a rebase is in flight before naming a side, because the wrong choice still yields a valid scene and no error.

## Why a scene that loads is not a verified merge

UnityYAML is a custom library: no comments, no multi-document restructuring, not the full YAML spec [yaml], so generic YAML tools can emit files Unity cannot load. Structure [scene]: a GameObject lists components in `m_Component`, each component points back with `m_GameObject`, hierarchy is in the Transform's `m_Children`, and roots are in a `SceneRoots` document.

| Failure | Mechanism | Symptom |
|---|---|---|
| Dangling `fileID` | A kept reference targets a document from the discarded side | Loads; field reads `None` at runtime |
| Duplicated component | Both sides added it with different `fileID`s | Two instances run |
| Orphaned component | Document survived but its `fileID` left `m_Component` | Absent from Inspector, no diagnostic |
| Reordered `m_Children` | Merge order matches neither side | Sibling order and index lookups shift |
| Lost `SceneRoots` entry | Root `fileID` dropped | Object in file but not in hierarchy |
| Reparent vs delete | One side moved an object under a parent the other deleted | Object attached under the surviving parent (derived, not documented) |

Cross-asset references resolve by GUID and fail the same silent way; see [meta-files-and-guids.md](meta-files-and-guids.md).
