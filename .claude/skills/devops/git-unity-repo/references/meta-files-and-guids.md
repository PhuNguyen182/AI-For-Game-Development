# `.meta` Files and GUIDs — the Reference Break Git Cannot Show

Sources: [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html), [Refreshing the Asset Database](https://docs.unity3d.com/Manual/AssetDatabaseRefreshing.html), [Version control integrations](https://docs.unity3d.com/Manual/Versioncontrolintegration.html), [YAML scene file example](https://docs.unity3d.com/Manual/YAMLSceneExample.html), [git-checkout](https://git-scm.com/docs/git-checkout).
Covers: SKILL.md §4 — "Move, rename and delete every asset together with its `.meta` file", "Treat a regenerated `.meta` as a reference break rather than a cosmetic diff".

Holds the reference model behind every "the icon went missing and nothing
changed" report: what a `.meta` stores, why Unity resolves references through
the GUID inside it rather than the asset's path, and therefore why a lost
`.meta` breaks referencing assets whose files git reports as untouched. The
`fileID` graph *inside* one scene or prefab is a different mechanism and lives
in [scene-and-prefab-conflicts.md](scene-and-prefab-conflicts.md); recovering
the pre-move commit itself is `git-forensics` and `git-recovery` territory.

- [What a `.meta` holds](#what-a-meta-holds)
- [How a reference resolves](#how-a-reference-resolves)
- [The failure chain](#the-failure-chain)
- [Case table](#case-table)
- [`.meta` merge conflicts](#meta-merge-conflicts)
- [Correct practice](#correct-practice)

## What a `.meta` holds

Unity creates one `.meta` file per asset **and per folder** inside `Assets`,
sitting beside it as a hidden sibling.

| Content | Role | Source |
|---|---|---|
| `guid: <32 hex chars>` | The asset's unique internal identifier — the only stable handle other assets store | [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html) |
| Importer settings | Every import option for that asset (texture compression, model rig, audio format), so the same source file imports identically on every machine | [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html) |
| Folder `.meta` | Gives a folder its own GUID, which is how Unity reconciles empty folders against version control systems that cannot store them | [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html) |
| Visibility | Hidden by default; the Version Control project settings offer a "Visible meta files" mode for VCS platforms Unity does not integrate with | [Version control integrations](https://docs.unity3d.com/Manual/Versioncontrolintegration.html) |
| Project view | Unity always hides `.meta` files in its own Project window regardless of the visibility mode | [Version control integrations](https://docs.unity3d.com/Manual/Versioncontrolintegration.html) |

**Critical caveat**: a `.meta` is not a cache. Deleting it does not cause a
recompute of the same value — the GUID is assigned, not derived, so a
regenerated `.meta` carries a *different* GUID and there is nothing to
regenerate it back from except a commit that still holds the original.

## How a reference resolves

| Fact | Consequence | Source |
|---|---|---|
| Unity "assigns unique internal IDs to detect new files in the `Assets` folder" | Identity is the ID, not the path | [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html) |
| Those IDs allow "assets to be moved or renamed without breaking references" | A path change is free *as long as the `.meta` travels with it* | [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html) |
| A cross-asset reference is stored as `{fileID: …, guid: …, type: …}` inside the referencing scene, prefab or ScriptableObject | The referencing file names the GUID it wants; it never names a path | [YAML scene file example](https://docs.unity3d.com/Manual/YAMLSceneExample.html) |
| A refresh checks "if any files in the `Assets` and `Packages` folders have been added, modified, or deleted since the last check" and updates the Asset Database | An asset arriving without its `.meta` reads as a brand-new file, which is exactly when a fresh GUID is minted | [Refreshing the Asset Database](https://docs.unity3d.com/Manual/AssetDatabaseRefreshing.html) |
| Unity's own statement: losing a `.meta` "breaks all project references to that asset — textures lose material assignments, scripts become unassigned components" | The breakage is total for that asset, not partial | [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html) |

## The failure chain

Each link below is individually unremarkable; the combination is what makes
this class of bug hard to attribute.

| Link | What happens | Source |
|---|---|---|
| An asset arrives without a matching `.meta` | The refresh classifies it as an added file rather than a moved one | [Refreshing the Asset Database](https://docs.unity3d.com/Manual/AssetDatabaseRefreshing.html) |
| Unity mints a new GUID and writes a new `.meta` | The old GUID now belongs to nothing in the project | [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html) |
| Every prefab, scene and ScriptableObject holding the old GUID now points at a missing asset | The stored `{guid: …}` is unresolvable, so the field reads as `None`/missing | [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html) |
| None of those referencing files were edited | Their bytes are byte-identical, so `git status`, `git diff` and any diff-based review show **nothing** on any of them | synthesized |
| The only files git shows as changed are the moved asset and its new `.meta` | The diff looks like an innocuous file move, which is why it passes review | synthesized |
| The symptom surfaces later, in a scene nobody touched | Attribution points at whoever last opened that scene, not at whoever moved the asset | synthesized |

**Critical caveat**: this is the one failure in this skill where the absence of
a diff is the *evidence*, not the reassurance. A missing-reference report whose
referencing prefab shows no git history at all is a GUID break by elimination.

## Case table

| Case | Symptom | Mechanism | Narrowest fix | Source |
|---|---|---|---|---|
| Asset moved or renamed outside the Editor without its `.meta` | References to it break project-wide; the asset itself looks fine in the Project window | The refresh sees a deleted file and an unrelated added file; the added one gets a new GUID | Restore the original `.meta` alongside the asset at its new path from the pre-move commit, then let Unity refresh — do not re-move the asset | [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html) |
| `.meta` deleted, asset kept | Same total reference break, plus every import setting for that asset resets to the importer default | The GUID and the import settings live in the same file, so both are lost together | Restore the `.meta` from the last commit that had it (`git checkout <commit> -- <path>.meta`) rather than re-authoring import settings | [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html), [git-checkout](https://git-scm.com/docs/git-checkout) |
| Asset deleted, `.meta` kept (orphan) | No visible error; the `.meta` lingers in the repository describing nothing | The refresh removes the asset from the database and the stray `.meta` has no asset to pair with | Delete the orphan `.meta`; if the asset was deleted by mistake, restore the asset *before* deleting anything so the pair stays intact | [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html) |
| Asset tree copy-pasted between projects, `.meta` files included | Two different assets claim the same GUID; references resolve to whichever the Asset Database happened to register, and can flip between machines | GUIDs are unique per assignment, not per project, so copying the `.meta` copies the identity | Import through a `.unitypackage` or the Package Manager instead of a file-system copy; if already copied, delete the duplicated side's `.meta` files so Unity mints fresh GUIDs, accepting the reference break that causes on that side only | synthesized |
| Folder moved without its folder `.meta` | Every asset beneath it can be treated as new even when the individual asset `.meta` files survived | The folder's own GUID is part of the metadata Unity tracks | Move folders through the Editor's Project window, which relocates the folder `.meta` with its contents | [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html) |
| `.meta` regenerated to "fix" a noisy diff | A cosmetically clean diff and a project-wide reference break in the same commit | Regeneration replaces the `guid` line | Revert the commit; the original GUID exists only in history | [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html) |
| Empty folder appears or disappears after a pull | Unity adds or removes folders based on which `.meta` files it can see | Unity reconciles empty folders itself because some VCS platforms cannot store them | Nothing — this is documented Unity behaviour, not a defect; do not "fix" it by committing a placeholder file | [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html) |

## `.meta` merge conflicts

A conflicted `.meta` is two questions in one file, and they have opposite
answers.

| Region in conflict | Correct resolution | Why | Source |
|---|---|---|---|
| The `guid` line | Take one side wholesale — never a blended value, and prefer the side already present in the branch history that other assets were authored against | A GUID is an identity, so the only valid values are the two that exist; anything else names no asset | [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html) |
| Importer settings below the GUID | Genuinely mergeable, and the one part of this skill where a line-level resolution is legitimate | These are independent import options, not a graph of references | [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html) |
| Both sides added the same asset independently | Two assets with two GUIDs and one path; keeping one `.meta` orphans references authored against the other | The duplicate arose before either side existed for the other to reference | synthesized |
| Inspecting the two candidate GUIDs | `git show :2:<path>.meta` and `git show :3:<path>.meta` read the two staged versions without touching the working tree | Stage 2 is `HEAD`'s version, stage 3 is the incoming one | [git-checkout](https://git-scm.com/docs/git-checkout) |

**Critical caveat**: resolving a `guid` conflict is not a formatting decision.
Whichever side is discarded, every asset that referenced the discarded GUID
breaks, and — per the failure chain above — none of those assets will appear in
the resulting diff. Enumerate the referencing assets by searching the tree for
the discarded GUID string before choosing, not afterwards.

## Correct practice

| Practice | Reason | Source |
|---|---|---|
| Move, rename and delete assets from the Editor's Project window | Unity relocates the `.meta` with the asset and updates the Asset Database in one operation, so no GUID is ever reassigned | [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html) |
| When a file-system move is unavoidable, move the asset and its `.meta` in the same operation | Unity's own rule: "if you move or rename an asset outside of Unity, you must move or rename the `.meta` file to match" | [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html) |
| Commit an asset and its `.meta` in the same commit | A commit holding one without the other is a broken tree that any checkout of that commit reproduces | synthesized |
| Never add `*.meta` to `.gitignore` | The GUID is project state, not machine state; ignoring it guarantees every clone mints its own GUIDs | [Asset metadata](https://docs.unity3d.com/Manual/AssetMetadata.html) |
| Treat `Assets > Reimport` as re-running the importer, not as regenerating identity | Reimport re-reads the existing `.meta`; it does not mint a new GUID, which is why it is safe and also why it fixes nothing about a broken reference | [Refreshing the Asset Database](https://docs.unity3d.com/Manual/AssetDatabaseRefreshing.html) |
| Treat `Reimport All` as a `Library/` rebuild with a long stall, and never as a reference repair | It rebuilds imported artifacts from the assets and `.meta` files already on disk, so a wrong GUID on disk stays wrong | [Refreshing the Asset Database](https://docs.unity3d.com/Manual/AssetDatabaseRefreshing.html) |
| Keep the Editor closed during a checkout that moves assets | A refresh triggered mid-checkout can classify a half-written tree as additions and deletions, minting GUIDs from a state that never existed | [Refreshing the Asset Database](https://docs.unity3d.com/Manual/AssetDatabaseRefreshing.html) |

Recovering an original GUID always means reading it out of history, which makes
the pre-move commit the artifact that matters; locating that commit is
`git-forensics`, and restoring from an unreachable one is `git-recovery`.
