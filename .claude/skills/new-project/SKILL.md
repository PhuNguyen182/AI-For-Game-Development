---
name: new-project
description: "Bootstrap a Unity project for this framework: CLAUDE.md, packages, Game.Core/Game.Client asmdefs and test assemblies, git + LFS, per-device-tier perf budget from the profile, .workflow/ state, optional CI. Use for a new or adopted project."
argument-hint: "<project path, or 'new'>"
---

# /new-project

## 1. Identity — one `AskUserQuestion` call (≤4 questions)
Profile · platforms · multiplayer · render pipeline. Write them into `CLAUDE.md`, plus its 3-line Summary from the GDD or the GD's pitch. Unity version from `ProjectSettings/ProjectVersion.txt`.

## 2. Project
- No project yet → plugin skill `unity:new-unity-project`, else verify it opens (`unity status` / `unity pipeline list`).
- Editor settings: Force Text serialization, Visible Meta Files. Unity CLI alias, build targets, MCP servers → `CLAUDE.md`.

## 3. Packages (`unity:unity-package-management`)
Always: Input System, Test Framework, the chosen render pipeline. Multiplayer → the foundation `/decide` picks — never preinstalled. Anything third-party → `security-reviewer` first.

## 4. Structure — `gameplay-engineer`
```
Assets/Game.Core/Game.Core.asmdef                 noEngineReferences: true
Assets/Game.Core/Tests/Game.Core.Tests.asmdef     Editor only, refs Game.Core + NUnit
Assets/Game.Client/Game.Client.asmdef             refs Game.Core
Assets/Game.Client/Tests/Game.Client.Tests.asmdef Play Mode, refs Game.Client + Game.Core
Assets/Game.Server/…                              only when multiplayer
```
One passing placeholder test per test assembly proves the test command; write that command into `CLAUDE.md`.

## 5. Git — `git-expert` with skill `git-unity-repo`
Unity `.gitignore`, `.gitattributes` (UnityYAMLMerge, LFS for binaries), `git lfs install`. Never commit `Library/`, `Temp/`, `Logs/`, `UserSettings/`.
Memory and search (skills `mem`, `code-search`): `.gitignore` += `.memory/.index/`, `.memory/.state/`; `.gitattributes` += `.memory/traces/** text eol=lf linguist-generated` (never `-diff`: the pre-commit secret scan reads diffs); copy `.xerjignore` and `.memory/sources.txt` from the framework root; `.memory/notes/` starts empty.

## 6. Perf budget — `AskUserQuestion`, recommended first
| Profile | Recommended default |
|---|---|
| hyper-casual | 60 fps (16.6 ms) on Android low-end · 0 B GC/frame steady state · ≤ 100 draw calls · ≤ 500 MB RAM · ≤ 150 MB install |
| mid-core | 30–60 fps on Android mid + oldest supported iOS · 0 B GC/frame steady state · ≤ 200 draw calls · ≤ 1 GB RAM |
| hard-core | GD-defined per tier |
Write the answer into `CLAUDE.md` → Perf budget, every metric with its unit and tier; a metric left out gets no verdict from `performance-qa-engineer`.

## 7. State
Create `.workflow/bugs.md` from `/fix`'s template and `.workflow/features/`. Commit `.workflow/` and `.memory/`.
`CLAUDE.md` → Code search: `xerj prefix <kebab project name>` when `xerj` is installed, else `Grep`.
Create `docs/tech-stack.md` from `references/tech-stack-template.md`, filled from `Packages/manifest.json`, `ProjectSettings/` and the answers above.

## 8. CI — only if the GD wants it now
`ci-cd-engineer`: build + test pipeline for the build targets, manual trigger.

## 9. Report
What was set up, what was asked and answered, what is still empty in `CLAUDE.md`. Ask before the first commit.
