# Ignore Surface, Single-Decision Files, Git LFS

Sources (Docs bases in SKILL.md): [dirs] Manual/default-directories.html, [manifest] Manual/upm-manifestPrj.html, [lock] Manual/upm-conflicts-auto.html, [lfs] git-lfs.com and github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-*.adoc, [attr] git-scm.com/docs/gitattributes.

## Ignore

Entries marked * are Unity's own instruction to exclude [dirs]; the rest are derived from what generates them. Folder entries are anchored to the project root (`/`): an unanchored `Build/` or `Library/` also drops `Assets/**/Build/` or a plugin's `Library/`, and those assets never reach a commit.

| Entry | Why |
|---|---|
| `/[Ll]ibrary/`* | Per-computer working directory; Unity regenerates it on open (slow reimport only) |
| `/[Tt]emp/`* | Cleared every time Unity closes |
| `/[Uu]ser[Ss]ettings/`* | Personal preferences; also holds Editor session tokens |
| `/[Ll]ogs/` | Per-machine Editor logs |
| `/[Oo]bj/`, `/[Bb]uild/`, `/[Bb]uilds/`, `*.apk`, `*.aab`, `*.pdb` | Compiler and build output, reproducible |
| `/[Mm]emoryCaptures/`, `/[Rr]ecordings/` | Memory Profiler snapshots and Recorder output, per machine |
| `/ServerData/`, `/[Aa]ssets/[Ss]treaming[Aa]ssets/aa/`, `/[Aa]ssets/[Ss]treaming[Aa]ssets/aa.meta` | Addressables build output, rebuilt from the groups |
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

## Line-ending baseline

```gitattributes
* text=auto
*.cs text diff=csharp
*.sh text eol=lf
```

These lines open `.gitattributes`; the UnityYAMLMerge block and the LFS block follow, and the later line wins for the same attribute. `text=auto` normalises only files git detects as text (no NUL byte), so binaries pass untouched, and `core.autocrlf` no longer decides per machine. Added to a repo with history: `git add --renormalize .` in a commit of its own (one large line-ending diff), then list that commit in `.git-blame-ignore-revs` (`git-forensics`).

## LFS attributes

The list matches what `.claude/hooks/pre-commit.ps1` (`$BinaryExt`) blocks outside LFS; keep the two in step. `*.unitypackage`, `*.apk`, `*.aab`, `*.ipa` are ignored, not tracked.

```gitattributes
*.png    filter=lfs diff=lfs merge=lfs -text
*.jpg    filter=lfs diff=lfs merge=lfs -text
*.jpeg   filter=lfs diff=lfs merge=lfs -text
*.tga    filter=lfs diff=lfs merge=lfs -text
*.psd    filter=lfs diff=lfs merge=lfs -text
*.psb    filter=lfs diff=lfs merge=lfs -text
*.tif    filter=lfs diff=lfs merge=lfs -text
*.tiff   filter=lfs diff=lfs merge=lfs -text
*.exr    filter=lfs diff=lfs merge=lfs -text
*.hdr    filter=lfs diff=lfs merge=lfs -text
*.gif    filter=lfs diff=lfs merge=lfs -text
*.bmp    filter=lfs diff=lfs merge=lfs -text
*.fbx    filter=lfs diff=lfs merge=lfs -text
*.obj    filter=lfs diff=lfs merge=lfs -text
*.blend  filter=lfs diff=lfs merge=lfs -text
*.max    filter=lfs diff=lfs merge=lfs -text
*.ma     filter=lfs diff=lfs merge=lfs -text
*.mb     filter=lfs diff=lfs merge=lfs -text
*.wav    filter=lfs diff=lfs merge=lfs -text
*.mp3    filter=lfs diff=lfs merge=lfs -text
*.ogg    filter=lfs diff=lfs merge=lfs -text
*.aif    filter=lfs diff=lfs merge=lfs -text
*.aiff   filter=lfs diff=lfs merge=lfs -text
*.flac   filter=lfs diff=lfs merge=lfs -text
*.mp4    filter=lfs diff=lfs merge=lfs -text
*.mov    filter=lfs diff=lfs merge=lfs -text
*.webm   filter=lfs diff=lfs merge=lfs -text
*.ttf    filter=lfs diff=lfs merge=lfs -text
*.otf    filter=lfs diff=lfs merge=lfs -text
*.zip    filter=lfs diff=lfs merge=lfs -text
*.7z     filter=lfs diff=lfs merge=lfs -text
*.dll    filter=lfs diff=lfs merge=lfs -text
*.so     filter=lfs diff=lfs merge=lfs -text
*.a      filter=lfs diff=lfs merge=lfs -text
*.aar    filter=lfs diff=lfs merge=lfs -text
*.jar    filter=lfs diff=lfs merge=lfs -text
*.bundle filter=lfs diff=lfs merge=lfs -text
LightingData.asset filter=lfs diff=lfs merge=lfs -text
```

`git lfs track "<pattern>"` writes such a line; `git add .gitattributes` is required. `-text` blocks end-of-line conversion on binaries. Do not list `*.meta`: it is small text holding GUID identity.

Size: the hook also sends any other file over 5 MB to LFS, except text Unity YAML (`%YAML` header), which stays in git at any size so UnityYAMLMerge keeps working (`merge=lfs` would replace it). A large binary `.asset` (baked lighting, NavMesh) needs its own LFS line, as `LightingData.asset` above; place LFS lines after the UnityYAMLMerge block, since the later line wins for the same attribute.

**Caveat:** a new pattern converts nothing already committed; history keeps the full binaries. `git lfs migrate` rewrites commits, which is a history rewrite.

## Locking unmergeable files

| Command / attribute | Fact that decides |
|---|---|
| `lockable` on an attribute line | git-lfs checks matching files out read-only until locked, so an edit without a lock is visible at once |
| `git lfs lock <path>` / `git lfs unlock <path>` | Takes or releases the server-side lock; needs host support for the LFS locking API |
| `git lfs locks` | Lists who holds what. With lock verification on (`lfs.<url>.locksverify`), the LFS pre-push hook refuses a push that changes a file another user has locked |
| `git lfs unlock --force <path>` | Breaks another person's lock: GD-only, never on an agent's initiative |

## Pointer symptom

A texture or model that is a ~130-byte text file starting `version https://git-lfs.github.com/spec/v1` with `oid sha256:` and `size` lines is a pointer. `git status` reports it clean, and Unity imports it as broken (the `.meta`/GUID is intact, so this is not a reference break). Causes: `git lfs install` never ran before the clone (the smudge filter is missing), or `GIT_LFS_SKIP_SMUDGE` was set. Run `git lfs install` then `git lfs pull`; do not re-clone.

## LFS commands

| Command | Fact that decides |
|---|---|
| `git lfs install` | Once per user: registers the `lfs` clean/smudge filters in global config and a pre-push hook |
| `git lfs env` | Confirms the filters are configured before blaming the remote |
| `git lfs ls-files` | `*` = full object, `-` = pointer; any `-` is an unusable asset |
| `git lfs fsck --dry-run` | Checks LFS files in HEAD; without `-d`/`--dry-run` it moves corrupt ones to `.git/lfs/bad`. `--objects` verifies hashes and presence, `--pointers` verifies pointer format |
| `git lfs pull` | Downloads missing content from the remote and writes it to the working tree |
| `git lfs fetch` + `git lfs checkout` | `fetch` fills the local store only; `checkout` writes content from the store and downloads nothing |

**Caveat:** `checkout` against an empty local store reports success and leaves every pointer. Confirm no `-` remains in `git lfs ls-files`. None of this proves the Editor can import the restored files; do any rewrite to check with the Editor closed.
