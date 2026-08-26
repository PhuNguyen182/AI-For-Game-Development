---
name: git-unity-repo
description: >
  Git for a Unity project — the failures git cannot see. Covers `.unity`,
  `.prefab` and `.asset` YAML conflicts with Force Text serialization and
  UnityYAMLMerge (`merge.unityyamlmerge`, `.gitattributes`), `.meta` files
  and the GUID break a regenerated one causes, the ignore surface
  (`Library/`, `Temp/`, `Logs/`, `UserSettings/` versus tracked
  `ProjectSettings/` and `Packages/packages-lock.json`), recurring
  `ProjectVersion.txt` conflicts, Git LFS pointer corruption, and why the
  Editor must be closed before a working-tree rewrite. Not for: generic
  history repair (`git-recovery`), anchoring a command
  (`git-safety-anchor`), tracing a commit (`git-forensics`).
---

# Unity Repository Git — Scene Merges, `.meta` GUIDs, the Ignore Surface, and LFS

## Bundled resources

### References
Read-only context, loaded on demand so SKILL.md itself stays short. "Read when" is a real condition, not a restatement of the topic.

| File | Contents | Read when |
|---|---|---|
| [root-links.md](references/root-links.md) | Unity Manual and Git LFS documentation roots, plus the Unity version this skill's paths and settings are pinned to | Starting any task here, or confirming an Editor setting path against the installed Unity version |
| [scene-and-prefab-conflicts.md](references/scene-and-prefab-conflicts.md) | Force Text serialization, wiring UnityYAMLMerge through `.gitattributes` and git config, the take-one-side strategy, `checkout --ours`/`--theirs`, and why a scene that opens can still be wrong | A `.unity`, `.prefab` or `.asset` file is in conflict, or scene merges keep needing manual fixing |
| [meta-files-and-guids.md](references/meta-files-and-guids.md) | What a `.meta` holds, how Unity assigns and resolves GUIDs, the silent reference break from a regenerated `.meta`, orphan metas, and GUID collisions from copied asset trees | Moving, renaming or deleting assets, or a reference broke with no visible change to the referencing object |
| [ignore-surface-and-lfs.md](references/ignore-surface-and-lfs.md) | The ignore and track lists with the reason for each entry, `ProjectVersion.txt` and `packages-lock.json` conflict handling, `.gitattributes` LFS patterns, `git lfs fsck`, pointer-file symptoms | Setting up or auditing `.gitignore`/`.gitattributes`, or a binary asset checks out as a small text file |

## 1. Objective
Keep a Unity project's git history trustworthy for the failures git itself reports as success: a scene or prefab YAML that merged cleanly line by line and is now internally inconsistent, a `.meta` file regenerated with a fresh GUID so every reference to that asset silently resolves to nothing, an LFS-tracked texture checked out as a 130-byte pointer file, and a `git checkout` run under a live Editor that reimports over files still changing. Each of these produces a green `git status` and a broken project, which is why they need handling that git's own tooling does not provide.

## 2. Role
Act as the Unity repository specialist for the devops track — the skill reached for whenever a git operation meets Unity's own file formats, its GUID reference model, its generated directories, or its large binary assets.

## 3. When to invoke this skill
- A `.unity`, `.prefab`, `.asset`, `.controller`, or `.mat` file is in conflict, or scene merges keep needing hand repair.
- Assets are being moved, renamed, or deleted, or a reference broke without any visible change to the object holding it.
- `.gitignore` or `.gitattributes` is being written or audited for this project.
- A texture, audio clip, or model checks out as a small text file, or `git lfs` reports missing objects.
- A working-tree rewrite is planned and the Editor's state has to be accounted for.
- Negative trigger: recovering commits or repairing a corrupt object store — that's `git-recovery`.
- Negative trigger: producing the backup ref before a command runs — that's `git-safety-anchor`.
- Negative trigger: which commit changed this asset and when — that's `git-forensics`.

## 4. How to use this skill
1. **Confirm Asset Serialization is Force Text before treating any scene or prefab as mergeable** — binary serialization makes every scene an opaque blob where the only outcome is a whole-file conflict, so verify the project setting first rather than diagnosing merge behaviour that was never possible. Resolve the setting's path against the installed Editor version, which [root-links.md](references/root-links.md) pins.
2. **Wire UnityYAMLMerge as the merge driver rather than merging YAML by hand** — it understands Unity's object graph where a line-based merge does not; configure it in `.gitattributes` and git config per [scene-and-prefab-conflicts.md](references/scene-and-prefab-conflicts.md).
3. **Default to taking one side of a scene or prefab conflict wholesale, then reapplying the other side in the Editor** — a hand-resolved YAML conflict can produce a file that parses and loads while holding a dangling reference or a duplicated component, and the Editor is the only tool that validates the result.
4. **Never treat a scene that opens as a scene that merged correctly** — the failure mode here is a project that loads and misbehaves, so confirm the specific objects the merge touched, not just that the Editor accepted the file.
5. **Move, rename and delete every asset together with its `.meta` file** — Unity stores the asset's GUID in the `.meta`, and separating them makes the Editor mint a new GUID on reimport.
6. **Treat a regenerated `.meta` as a reference break rather than a cosmetic diff** — every prefab, scene, and ScriptableObject that pointed at the old GUID now points at nothing, and git reports no change to any of those files, per [meta-files-and-guids.md](references/meta-files-and-guids.md).
7. **Track `ProjectSettings/` and `Packages/packages-lock.json`, and ignore `Library/`, `Temp/`, `Logs/`, `obj/`, `UserSettings/` and generated solution files** — the tracked half is project state that must be identical across machines, and the ignored half is regenerable output whose churn hides real diffs, per [ignore-surface-and-lfs.md](references/ignore-surface-and-lfs.md).
8. **Resolve `ProjectVersion.txt` and `packages-lock.json` conflicts by deciding a version rather than merging text** — these encode a single project-wide choice, so a merged intermediate value is a state no machine was ever in.
9. **Verify an LFS-tracked binary checked out as real content rather than as a pointer** — a pointer file is a valid text file that git reports as clean while the asset is unusable; check size or run `git lfs fsck` before declaring a checkout complete.
10. **Confirm the Unity Editor is closed before any command that rewrites the working tree** — `checkout`, `reset --hard`, `clean`, and a branch switch all change assets while the Editor's asset database is watching them, which can leave `Library/` inconsistent with what is on disk.
11. **Preview `git clean` with `-xdn` and get the deletion list confirmed** — losing `Library/` costs a slow reimport, but the same command deletes untracked assets that exist in no commit and no stash.
12. **Author every ignore rule, attribute line, and commit message in English** — per `language-and-comments.md`'s Working language section, with commit messages following `commit-message.md`.
13. **Ask which Unity version and which side of a conflict is authoritative when either is unstated** — the Editor setting paths differ across versions, and choosing a side of a scene conflict is a content decision this skill does not own.

## 5. Specific goals / tasks this skill performs
- Resolve a `.unity`, `.prefab` or `.asset` conflict, stating which side was taken and what must be reapplied in the Editor.
- Configure Force Text serialization and UnityYAMLMerge so future scene merges are handled by a Unity-aware driver.
- Diagnose a broken asset reference back to a GUID change, and identify the `.meta` that caused it.
- Author or audit `.gitignore` and `.gitattributes` for this project, with the reason for each entry.
- Decide a `ProjectVersion.txt` or `packages-lock.json` conflict rather than merging it.
- Confirm LFS-tracked assets checked out as content, and diagnose pointer-file symptoms.
- Out of scope: recovering lost commits or repairing the object store (`git-recovery`), producing the anchor for a destructive command (`git-safety-anchor`), tracing a change to its commit (`git-forensics`), and the content decision about which version of a scene is correct (`unity-engineer`).

## 6. Output format
```
## Unity Repository Work — <the asset, conflict, or configuration handled>
- Serialization: Force Text confirmed | binary — <what that constrained>
- Merge driver: UnityYAMLMerge configured | not configured — <consequence>
- Conflict resolution: <which side was taken wholesale, and what must be reapplied in the Editor>
- GUID impact: <references broken or preserved, and the `.meta` files involved>
- Ignore/track changes: <entries added or removed, with the reason>
- LFS: <pointer or content verified, and how — or "no LFS-tracked file involved">
- Editor state: <confirmed closed before the working-tree rewrite, or why no rewrite occurred>
- Layer: repository metadata | Game.Client.*
- Known limitations: <what still needs Editor-side validation>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Known limitations` above with all three fields:
```
- Known limitations: <what still needs Editor-side validation — omit this line entirely if there are genuinely none>
- Latent concerns: <failure modes not yet triggered: assumptions that hold only under current conditions, thresholds not yet reached, trade-offs knowingly deferred>
- Future remediation: <the concrete fix for each concern above, each with the condition that should trigger it>
```

## 7. Examples
**Example 1**
- Input: "Two people edited the main menu scene and the merge is a mess."
- Output: confirmed Force Text, then took the incoming side wholesale with `git checkout --theirs` rather than resolving the YAML, and reported the four GameObjects the other side had added so `ui-ux-programmer` can reapply them in the Editor. Also wired UnityYAMLMerge in `.gitattributes` and git config so the next conflict gets a Unity-aware driver.

**Example 2**
- Input: "The YAML conflict is only a few lines, just fix those and commit — it opens fine in Unity."
- Output: declined as a completion criterion — a scene that opens can still hold a dangling reference or a duplicated component, and a line-level resolution of Unity YAML is exactly how that happens. Took one side wholesale instead, listed what to reapply, and reported that Editor-side validation is still owed before this counts as resolved.

**Example 3**
- Input: "All the ability icons show as missing references after I reorganised the art folders."
- Output: traced it to `.meta` files left behind when the assets were moved with the OS file explorer rather than through the Editor, so Unity minted new GUIDs on reimport. Reported the affected GUIDs, that no referencing prefab shows any diff in git, and that recovering the original GUIDs from the pre-move commit is the narrowest fix.

## 8. Edge cases & guardrails
- Never hand-merge a `.unity` or `.prefab` conflict line by line — the result can parse, load, and still hold a dangling reference or a duplicated component that no git tooling will flag.
- Never treat "the scene opens in Unity" as verification that a merge was correct; confirm the specific objects the merge touched.
- Never move or delete an asset without its `.meta`, and never regenerate a `.meta` to fix a diff — a new GUID breaks every reference to that asset while git reports the referencing files as unchanged.
- Never commit `Library/`, `Temp/`, `Logs/`, `obj/`, or generated solution files; their churn buries real diffs and they are regenerable by definition.
- Never merge `ProjectVersion.txt` or `packages-lock.json` — a blended value is a state no machine ever had; decide one side.
- Never declare a checkout complete without confirming LFS-tracked assets are content rather than pointer files; git reports a pointer-only tree as clean.
- Never run `checkout`, `reset --hard`, `clean`, or a branch switch with the Editor open on this repository — reimporting over changing files can leave the asset database inconsistent with disk.
- If the Unity version or which side of a conflict is authoritative is unstated, ask — setting paths differ across versions, and picking a scene's content is a decision for `unity-engineer`.
- `git clean -xdf` requires an explicit confirmation of the `-xdn` preview list in the current conversation; untracked assets it deletes exist in no commit, no stash, and no reflog.
