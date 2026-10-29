# Ignore Surface, Single-Decision Files, Git LFS

Sources (Docs bases in SKILL.md): [dirs] Manual/default-directories.html, [manifest] Manual/upm-manifestPrj.html, [lock] Manual/upm-conflicts-auto.html, [lfs] git-lfs.com and github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-*.adoc, [attr] git-scm.com/docs/gitattributes.

## Ignore

Entries marked * are Unity's own instruction to exclude [dirs]; the rest are derived from what generates them.

| Entry | Why |
|---|---|
| `Library/`* | Per-computer working directory; Unity regenerates it on open (slow reimport only) |
| `Temp/`* | Cleared every time Unity closes |
| `UserSettings/`* | Personal preferences; also holds Editor session tokens |
| `Logs/` | Per-machine Editor logs |
| `obj/`, `[Bb]uild/`, `[Bb]uilds/`, `*.apk`, `*.aab` | Compiler and build output, reproducible |
| `*.csproj`, `*.sln` | Generated per machine; conflict on every package change |
| `*.userprefs`, `.vs/`, `.idea/` | Per-developer IDE state |
| `*.unitypackage` | Duplicates content already in `Assets/` |
| Crash-report output (`sysinfo.txt`, `crashlytics-build.properties`, `*/Crashes/`) | Per-machine dumps that can carry machine and path details |

**Caveat:** `.gitignore` does not affect already-tracked paths. Adding `Library/` to a repo that tracks it changes nothing until `git rm -r --cached Library`.

## Track

`Assets/` (with every `.meta`), `ProjectSettings/` (must be identical across machines; not the same as `UserSettings/`), `Packages/manifest.json`, `Packages/packages-lock.json` (Unity recommends source control [lock]), and `.gitattributes` (an untracked one means no clone applies the LFS filters or merge drivers).

## Single-decision conflicts

A text merge of either file yields a value no machine ever had.

| File | Resolution |
|---|---|
| `ProjectSettings/ProjectVersion.txt` (`m_EditorVersion` and `m_EditorVersionWithRevision`, one fact stated twice) | Decide the team's Editor version and take that side whole. A merge can pair a version with the other side's revision hash. Opening in a newer Editor triggers an irreversible project upgrade, so this is a team decision. A recurring conflict means people are on different Editor versions. Handling is not documented by Unity |
| `Packages/packages-lock.json` | Take one side whole, then open the project to let Package Manager regenerate it, or delete it to rebuild from `manifest.json`. Unity: "Don't manually modify the lock file" [lock] |

Recurring lock churn may be a resolution question: `resolutionStrategy`/`pinnedPackages` in the manifest, or `enableLockFile` (off means non-deterministic indirect dependencies) [manifest].

## LFS attributes

```gitattributes
*.png filter=lfs diff=lfs merge=lfs -text
*.psd filter=lfs diff=lfs merge=lfs -text
*.tga filter=lfs diff=lfs merge=lfs -text
*.exr filter=lfs diff=lfs merge=lfs -text
*.fbx filter=lfs diff=lfs merge=lfs -text
*.wav filter=lfs diff=lfs merge=lfs -text
*.mp3 filter=lfs diff=lfs merge=lfs -text
*.ogg filter=lfs diff=lfs merge=lfs -text
*.mp4 filter=lfs diff=lfs merge=lfs -text
```

`git lfs track "<pattern>"` writes such a line; `git add .gitattributes` is required. `-text` blocks end-of-line conversion on binaries. Do not list `*.meta`: it is small text holding GUID identity.

**Caveat:** a new pattern converts nothing already committed; history keeps the full binaries. `git lfs migrate` rewrites commits, which is a history rewrite.

## Pointer symptom

A texture or model that is a ~130-byte text file starting `version https://git-lfs.github.com/spec/v1` with `oid sha256:` and `size` lines is a pointer. `git status` reports it clean, and Unity imports it as broken (the `.meta`/GUID is intact, so this is not a reference break). Causes: `git lfs install` never ran before the clone (the smudge filter is missing), or `GIT_LFS_SKIP_SMUDGE` was set. Run `git lfs install` then `git lfs pull`; do not re-clone.

## LFS commands

| Command | Fact that decides |
|---|---|
| `git lfs install` | Once per user: registers the `lfs` clean/smudge filters in global config and a pre-push hook |
| `git lfs env` | Confirms the filters are configured before blaming the remote |
| `git lfs ls-files` | `*` = full object, `-` = pointer; any `-` is an unusable asset |
| `git lfs fsck` | Checks LFS files in HEAD, moves corrupt ones to `.git/lfs/bad`; `--objects` verifies hashes and presence, `--pointers` verifies pointer format, `-d` is a dry run |
| `git lfs pull` | Downloads missing content from the remote and writes it to the working tree |
| `git lfs fetch` + `git lfs checkout` | `fetch` fills the local store only; `checkout` writes content from the store and downloads nothing |

**Caveat:** `checkout` against an empty local store reports success and leaves every pointer. Confirm no `-` remains in `git lfs ls-files`. None of this proves the Editor can import the restored files; do any rewrite to check with the Editor closed.
