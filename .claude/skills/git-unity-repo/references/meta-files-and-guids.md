# `.meta` Files and GUIDs

Sources (Docs base in SKILL.md): [meta] Manual/AssetMetadata.html, [refresh] Manual/AssetDatabaseRefreshing.html, [vcs] Manual/Versioncontrolintegration.html, [scene] Manual/YAMLSceneExample.html, [co] git-scm.com/docs/git-checkout.

## What a `.meta` holds [meta]

One per asset and per folder in `Assets`. It holds the asset's `guid` (32 hex chars, the only stable handle other assets store), every importer setting, and for a folder its own GUID (how Unity reconciles empty folders that some VCS cannot store). Unity always hides `.meta` in the Project window; the "Visible meta files" VCS mode is for unsupported VCS [vcs].

**Caveat:** a GUID is assigned, not derived. A regenerated `.meta` gets a different GUID, and only a commit that still holds the original can restore it.

## How references break

A cross-asset reference is stored as `{fileID, guid, type}` [scene]; paths are never stored, so moves are free while the `.meta` travels with the asset. An asset arriving without its `.meta` is classified by the refresh as a new file and gets a new GUID [refresh]; Unity states a lost `.meta` "breaks all project references to that asset" [meta]. Referencing files are byte-identical, so `git status` and `git diff` show nothing on them; the diff looks like a plain file move.

**Caveat:** here the absence of a diff is the evidence. A missing-reference report on a prefab with no git history is a GUID break by elimination.

## Cases

| Case | Fix |
|---|---|
| Moved/renamed outside the Editor without its `.meta` | Restore the original `.meta` beside the asset at its new path from the pre-move commit, then let Unity refresh; do not re-move |
| `.meta` deleted, asset kept (GUID and import settings both lost) | `git checkout <commit> -- <path>.meta` from the last commit holding it [co] |
| Asset deleted, `.meta` kept (orphan) | Delete the orphan; if the deletion was a mistake, restore the asset first so the pair stays intact |
| Asset tree copied between projects with `.meta` (duplicate GUIDs; resolution can flip between machines; derived, not documented) | Import via `.unitypackage`/Package Manager; if already copied, delete the duplicated side's `.meta` so Unity mints new GUIDs, accepting the break on that side only |
| Folder moved without its folder `.meta` | Move folders in the Editor's Project window |
| `.meta` regenerated to quiet a diff | Revert the commit; the original GUID exists only in history |
| Empty folders appear/disappear after a pull | Documented Unity behaviour; do not commit placeholder files |

## `.meta` merge conflicts

| Region | Resolution |
|---|---|
| `guid` line | Take one side whole, never a blend. Discarding a GUID breaks every asset referencing it with no diff, so first search the tree for the discarded GUID string and list the referrers; prefer the side other assets already reference (the search result decides) |
| Importer settings | Line-level merge is legitimate |
| Both sides added the same asset independently | Two GUIDs for one path; keeping one `.meta` orphans references authored against the other |
| Inspect candidates | `git show :2:<path>.meta` (HEAD) and `git show :3:<path>.meta` (incoming). In a rebase `HEAD` is the upstream plus the commits already replayed, and `:3:` the branch's own commit |

## Practice

- Move, rename and delete in the Editor; if you must use the file system, move the asset and its `.meta` together [meta].
- Commit an asset and its `.meta` in the same commit.
- Never ignore `*.meta`; every clone would mint its own GUIDs.
- `Assets > Reimport` re-reads the existing `.meta` and `Reimport All` rebuilds `Library/`; neither repairs a wrong GUID on disk [refresh].
- Keep the Editor closed during a checkout that moves assets: a mid-checkout refresh can treat a half-written tree as additions and deletions and mint GUIDs.

Locating the pre-move commit is `git-forensics`; restoring from an unreachable one is `git-recovery`.
