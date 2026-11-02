---
name: new-project
description: "Bootstrap a Unity project: CLAUDE.md, asmdefs, git + LFS, perf budget, .workflow/. Use for a new or adopted project."
argument-hint: "<project path, or 'new'>"
---

# /new-project

## 1. Identity — one `AskUserQuestion` call (≤4 questions)
- **Questions:** Profile · platforms · multiplayer · render pipeline.
- **Answers:** write them into `CLAUDE.md`, plus its 3-line Summary from the GDD or the GD's pitch.
- **Unity version:** from `ProjectSettings/ProjectVersion.txt`.

## 2. Project
- **Opening:** no project yet → plugin skill `unity:new-unity-project`, else verify it opens (`unity status` / `unity pipeline list`).
- **Editor settings:** Force Text serialization, Visible Meta Files.
- **Tooling:** Unity CLI alias, build targets, MCP servers → `CLAUDE.md`.

## 3. Packages (`unity:unity-package-management`)
- **Always:** Input System, Test Framework, the chosen render pipeline.
- **Multiplayer:** → the foundation `/decide` picks at the first multiplayer feature's CP1 — never preinstalled.
- **Third-party:** anything third-party → `security-reviewer` first.

## 4. Structure — `gameplay-engineer`
- **`Shared` feature:** the `Shared` feature, in the feature layout (`csharp-standards` → naming-convention.md → Folders).
- **Asmdefs:** asmdef `name` = `rootNamespace` = folder path:
```
Assets/_Project/Scripts/Shared/                 _Project.Scripts.Shared                  refs Shared.Core, Shared.DataModels
Assets/_Project/Scripts/Shared/DataModels/      _Project.Scripts.Shared.DataModels       noEngineReferences: true
Assets/_Project/Scripts/Shared/Core/            _Project.Scripts.Shared.Core             noEngineReferences: true, refs DataModels
Assets/_Project/Scripts/Shared/Tests/EditMode/  _Project.Scripts.Shared.Tests.EditMode   Editor only, refs Core + DataModels + NUnit
Assets/_Project/Scripts/Shared/Tests/PlayMode/  _Project.Scripts.Shared.Tests.PlayMode   Play Mode, refs Shared + Core + DataModels + NUnit
Assets/_Project/Scripts/Shared/Server/          _Project.Scripts.Shared.Server           only when multiplayer
```
- **Empty assemblies:** this skeleton is the one place empty assemblies are allowed: the placeholder tests below need them.
- **Later features:** every later M/L feature gets the same layout, only the folders it uses, under `Assets/_Project/Scripts/<Feature>/` (`/feature` step 4).
- **Adopted project:** an adopted project keeps its existing code where it is.
- **Placeholder tests:** one passing placeholder test per test assembly proves the test command.
- **Test command:** write the test command into `CLAUDE.md`.

## 5. Git — `git-expert` with skill `git-unity-repo`, before the Editor opens (or with it closed)
- **Base files:** Unity `.gitignore`, `.gitattributes` (UnityYAMLMerge, LFS for binaries), `git lfs install`.
- **Never committed:** never commit `Library/`, `Temp/`, `Logs/`, `UserSettings/`.
- **Signing globs:** keep the framework `.gitignore`'s signing/credential globs (`*.keystore`, `*.jks`, `*.p12`, `.env*`, service-account JSON, ...).
- **Raw-dump globs:** keep the framework `.gitignore`'s `.workflow/evidence/**` raw-dump globs (`logcat_*.txt`, `syslog*.txt`, `*.ips`, `*.crash`).
- **Both glob sets:** the signing and raw-dump globs sit outside the `Framework repo only` block and must stay in every game project.
- **Memory and search:** per skills `mem`, `code-search`:
  - **`.gitignore` additions:** `.gitignore` += `.memory/.index/`, `.memory/.state/`.
  - **`.gitattributes` addition:** `.gitattributes` += `.memory/traces/** text eol=lf linguist-generated` (never `-diff`: the pre-commit secret scan reads diffs).
  - **Copied files:** copy `.xerjignore` and `.memory/sources.txt` from the framework root.
  - **Notes:** `.memory/notes/` starts empty.
- **Framework block:** delete the copied `.gitignore`'s `Framework repo only` block, down to its end marker: the project commits its traces and its framework backlog.
- **Framework backlog source:** `.workflow/framework-backlog.md` comes from `.claude/templates/framework-backlog.md` (the session-start hook creates it; copy the template if absent).
- **Framework backlog commit:** `.workflow/framework-backlog.md` is committed with the project.

## 6. Perf budget — `AskUserQuestion`, recommended first
| Profile | Recommended default |
|---|---|
| hyper-casual | 60 fps (16.6 ms) on Android low-end · 0 B GC/frame steady state · ≤ 100 draw calls · ≤ 500 MB RAM · ≤ 150 MB install |
| mid-core | 30–60 fps on Android mid + oldest supported iOS · 0 B GC/frame steady state · ≤ 200 draw calls · ≤ 1 GB RAM |
| hard-core | GD-defined per tier |

- **Answer:** write the answer into `CLAUDE.md` → Perf budget, every metric with its unit and tier.
- **Left-out metric:** a metric left out gets no verdict from `performance-qa-engineer`.

## 7. State
- **Workflow state:** create `.workflow/bugs.md` from `/fix`'s template and `.workflow/features/`.
- **Staging:** stage nothing yet: step 9 asks once for the bootstrap commit (`.workflow/`, `.memory/`, the setup).
- **Code search:** `CLAUDE.md` → Code search: `xerj prefix <kebab project name>` when `xerj` is installed, else `Grep`.
- **Tech stack:** create `docs/tech-stack.md` from `references/tech-stack-template.md`, filled from `Packages/manifest.json`, `ProjectSettings/` and the answers above.

## 8. CI — only if the GD wants it now
- **Pipeline:** `ci-cd-engineer`: build + test pipeline for the build targets, manual trigger.

## 9. Report
- **Contents:** what was set up, what was asked and answered, what is still empty in `CLAUDE.md`.
- **Bootstrap commit:** one `AskUserQuestion` for the bootstrap commit: commit now (Khuyến nghị) / not yet.
