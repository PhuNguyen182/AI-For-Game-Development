---
name: git-unity-repo
description: "Git for Unity: YAML scene/prefab conflicts with UnityYAMLMerge, .meta and GUID integrity, Git LFS pointer vs content, .gitignore/.gitattributes for Unity. Use for Unity-specific git setup or asset conflicts."
user-invocable: false
---

# Unity Repository Git

Not for: generic history repair or a missing/corrupt LFS object in the store (`git-recovery`); anchoring a command (`git-safety-anchor`); tracing a commit (`git-forensics`); choosing which scene content is correct (`gameplay-engineer`).
Docs: https://docs.unity3d.com/Manual/ (unversioned root, Unity 6.5 when written; confirm Editor menu paths against the installed version) · https://git-lfs.com · https://git-scm.com/docs. The repo had no `ProjectVersion.txt` to pin against.

| Reference | Read when |
|---|---|
| [scene-and-prefab-conflicts.md](references/scene-and-prefab-conflicts.md) | A `.unity`, `.prefab` or `.asset` is in conflict, or wiring UnityYAMLMerge |
| [meta-files-and-guids.md](references/meta-files-and-guids.md) | Moving, renaming or deleting assets, a `.meta` conflict, or a reference broke with no diff on the referencing file |
| [ignore-surface-and-lfs.md](references/ignore-surface-and-lfs.md) | Writing or auditing `.gitignore`/`.gitattributes`, a `ProjectVersion.txt` or `packages-lock.json` conflict, a binary checked out as small text, or LFS locking |
| [routine-workflows.md](references/routine-workflows.md) | Syncing with the remote, reverting a merge, a release-branch cherry-pick, worktrees, UPM git packages, a large clone, maintenance, a pull request, commit signing, case-only renames, long paths, a shallow clone, a release tag |

## Steps
1. **Confirm Asset Serialization is Force Text** (Edit > Project Settings > Editor) before treating any scene or prefab as mergeable; `Force Binary` and new assets under `Mixed` are blobs that only conflict whole-file.
2. **Wire UnityYAMLMerge as the merge driver** rather than merging YAML by hand, per the scene reference.
3. **Resolve an in-progress scene or prefab conflict with `resolve-merge-conflicts`** — UnityYAMLMerge first, else a merge at GameObject/component/field level from the three stages. Take one side wholesale only when the stages show the other side added nothing; otherwise its additions are listed and reapplying them in the Editor goes to `gameplay-engineer` (`Next:`). Check for a rebase in progress first: `--ours`/`--theirs` invert there.
4. **A scene that opens is not a scene that merged correctly** — verify the specific objects the merge touched. Which side is correct is `gameplay-engineer`'s call; ask if unstated.
5. **Move, rename and delete every asset together with its `.meta`**, preferably in the Editor. A regenerated `.meta` is a reference break, not a cosmetic diff.
6. **For a `.meta` conflict, take one `guid` side whole** after searching the tree for the discarded GUID; importer settings below it may be line-merged.
7. **Track `ProjectSettings/`, `Packages/manifest.json`, `Packages/packages-lock.json`, all `.meta` and `.gitattributes`; ignore `/Library/`, `/Temp/`, `/Logs/`, `/obj/`, `/UserSettings/` (root-anchored) and generated solutions**, per the ignore reference. Stop tracking an already-tracked ignored path with `git rm --cached`.
8. **Decide `ProjectVersion.txt` and `packages-lock.json` conflicts by choosing a version**, never a text merge.
9. **Verify LFS-tracked binaries are content, not pointers**: `git lfs ls-files` shows no `-` marker and `git lfs fsck --dry-run` is clean (without `--dry-run` it moves objects into `.git/lfs/bad`). A clean `git status` proves nothing.
10. **Close the Unity Editor before any command that rewrites the working tree** (`checkout`, `switch`, `restore`, `reset --keep`, `merge`, `pull`, `rebase`, `stash pop`, `bisect`, `lfs pull`); use `git-safety-anchor` first.
11. **Preview `git clean` with `-xdn` and get that list confirmed** in this conversation (dispatched: quoted in the brief); `clean -f` is GD-run. It deletes untracked assets that exist in no commit, stash or reflog.
12. **Unmergeable files several people edit** (binary assets, a scene too contended to merge): mark them `lockable` and `git lfs lock` before editing, per the ignore reference.
13. **Ask for the Unity version if unstated.** Author ignore rules, attributes and commit messages in English; commits per `git-commit`.

## Never
- Merge `.unity`/`.prefab` YAML by raw text hunk, across document (`--- !u!`) boundaries.
- Add `*.meta` to `.gitignore` or route it through LFS.
- Commit a machine-local absolute path (UnityYAMLMerge) into a shared config.
- Convert committed history with `git lfs migrate` as an attribute edit; it rewrites commits (`git-recovery`, `git-safety-anchor`).

## Output
```
## Unity Repository Work — <asset, conflict or configuration>
- Serialization: Force Text | other — <constraint>
- Merge driver: configured | not — <consequence>
- Conflict resolution: <side taken wholesale; what to reapply in the Editor>
- GUID impact: <references broken or preserved; `.meta` files involved>
- Ignore/track changes: <entries and reason>
- LFS: <pointer or content verified, how — or none involved>
- Editor state: <closed before rewrite, or no rewrite>
- Known limitations: <Editor-side validation still owed>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "The conflict is only a few lines, fix them; it opens fine" -> declined: opening proves only that it parsed. Merged per component from the three stages, checked every `fileID` the merge touched, and reported Editor validation as owed.
