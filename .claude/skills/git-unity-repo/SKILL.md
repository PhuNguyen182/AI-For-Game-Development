---
name: git-unity-repo
description: "UnityYAMLMerge, .meta/GUID integrity, Git LFS, .gitattributes. Use for Unity git setup or asset conflicts."
user-invocable: false
---

# Unity Repository Git

- **Not for:** generic history repair or a missing/corrupt LFS object in the store (`git-recovery`); anchoring a command (`git-safety-anchor`); tracing a commit (`git-forensics`).
- **Not for:** choosing which scene content is correct (`gameplay-engineer`).
- **Docs:** https://docs.unity3d.com/Manual/ (unversioned root, Unity 6.5 when written; confirm Editor menu paths against the installed version) · https://git-lfs.com · https://git-scm.com/docs.
- **Version pin:** the repo had no `ProjectVersion.txt` to pin against.

## References
- **[scene-and-prefab-conflicts.md](references/scene-and-prefab-conflicts.md):** a `.unity`, `.prefab` or `.asset` is in conflict, or wiring UnityYAMLMerge.
- **[meta-files-and-guids.md](references/meta-files-and-guids.md):** moving, renaming or deleting assets, a `.meta` conflict, or a reference broke with no diff on the referencing file.
- **[ignore-surface-and-lfs.md](references/ignore-surface-and-lfs.md):** writing or auditing `.gitignore`/`.gitattributes`, a `ProjectVersion.txt` or `packages-lock.json` conflict, a binary checked out as small text, or LFS locking.
- **[routine-workflows.md](references/routine-workflows.md):** syncing with the remote, reverting a merge, a release-branch cherry-pick, worktrees, UPM git packages, a large clone, maintenance.
  - **Also:** a pull request, commit signing, case-only renames, long paths, a shallow clone, a release tag.

## Scripts
- **[unity.gitattributes](scripts/unity.gitattributes):** adapt into `.gitattributes` (after the UnityYAMLMerge block) → the LFS lines for binary extensions and `LightingData.asset`.

## Steps
1. **Confirm Asset Serialization is Force Text:** Edit > Project Settings > Editor, before treating any scene or prefab as mergeable.
   - **Blobs:** `Force Binary` and new assets under `Mixed` only conflict whole-file.
2. **Wire UnityYAMLMerge as the merge driver:** rather than merging YAML by hand, per the scene reference.
3. **Resolve an in-progress scene or prefab conflict with `resolve-merge-conflicts`:** UnityYAMLMerge first, else a merge at GameObject/component/field level from the three stages.
   - **One side wholesale:** only when the stages show the other side added nothing; otherwise its additions are listed and reapplying them in the Editor goes to `gameplay-engineer` (`Next:`).
   - **Rebase in progress:** check first; `--ours`/`--theirs` invert there.
4. **A scene that opens is not a scene that merged correctly:** verify the specific objects the merge touched.
   - **Correct side:** `gameplay-engineer`'s call; `Needs-decision`, `Next: gameplay-engineer`, when unstated.
   - **Editor validation:** still owed after a merge; report it as owed.
5. **Move, rename and delete every asset together with its `.meta`:** preferably in the Editor. A regenerated `.meta` is a reference break, not a cosmetic diff.
6. **For a `.meta` conflict, take one `guid` side whole:** after searching the tree for the discarded GUID; importer settings below it may be line-merged.
7. **Track and ignore:**
   - **Track:** `ProjectSettings/`, `Packages/manifest.json`, `Packages/packages-lock.json`, all `.meta` and `.gitattributes`.
   - **Ignore:** `/Library/`, `/Temp/`, `/Logs/`, `/obj/`, `/UserSettings/` (root-anchored) and generated solutions, per the ignore reference.
   - **Already tracked:** stop tracking an already-tracked ignored path with `git rm --cached`.
8. **Decide `ProjectVersion.txt` and `packages-lock.json` conflicts by choosing a version:** never a text merge.
9. **Verify LFS-tracked binaries are content, not pointers:** `git lfs ls-files` shows no `-` marker and `git lfs fsck --dry-run` is clean (without `--dry-run` it moves objects into `.git/lfs/bad`).
   - **Not evidence:** a clean `git status` proves nothing.
10. **Close the Unity Editor before any command that rewrites the working tree:** `checkout`, `switch`, `restore`, `reset --keep`, `merge`, `pull`, `rebase`, `stash pop`, `bisect`, `lfs pull`.
    - **Anchor:** use `git-safety-anchor` first.
11. **Preview `git clean` with `-xdn`:** get that list confirmed in this conversation (dispatched: quoted in the brief); `clean -f` is GD-run.
    - **Why:** it deletes untracked assets that exist in no commit, stash or reflog.
12. **Unmergeable files several people edit:** binary assets, a scene too contended to merge: mark them `lockable` and `git lfs lock` before editing, per the ignore reference.
13. **Author in English:** ignore rules, attributes and commit messages; commits per `git-commit`.
14. **Missing input:** Unity version unstated → dispatched agent `Blocked` or `Needs-decision`; main session `AskUserQuestion`.

## Never
- **YAML text hunks:** merging `.unity`/`.prefab` YAML by raw text hunk, across document (`--- !u!`) boundaries.
- **`.meta` handling:** adding `*.meta` to `.gitignore` or routing it through LFS.
- **Local paths:** committing a machine-local absolute path (UnityYAMLMerge) into a shared config.
- **LFS migrate:** converting committed history with `git lfs migrate` as an attribute edit; it rewrites commits (`git-recovery`, `git-safety-anchor`).

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
```

## Example
- **"The conflict is only a few lines, fix them; it opens fine":** declined — opening proves only that it parsed.
  - **Done instead:** merged per component from the three stages, checked every `fileID` the merge touched, and reported Editor validation as owed.
