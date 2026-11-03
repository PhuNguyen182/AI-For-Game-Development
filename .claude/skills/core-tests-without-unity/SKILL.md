---
name: core-tests-without-unity
description: "noEngineReferences, Tests/EditMode, dotnet test mirror, LangVersion 9.0. Use when Core tests run outside the Editor."
user-invocable: false
---

# Core Tests Without Unity

- **Not for:** test assembly attributes, Unity comparers and `-runTests` (`unity-test-framework`).
- **Not for:** which cases to write (`risk-based-test-planning`).
- **Not for:** the CI stage and report publishing (`jenkins-pipeline-authoring`).
- **Not for:** the replay test itself (`core-determinism`).
- **Not for:** bootstrapping the asmdefs on a new project (`new-project`).
- **Not for:** auditing a diff for `UnityEngine` leaks (`shared-core-boundary-audit`).
- **Docs:** Unity manual `https://docs.unity.com/en-us/engine/6000.0/manual/` — replace `6000.0` with the project's editor.
  - **UTF:** `https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/`.
  - **Microsoft Learn:** for MSBuild and `LangVersion`.
  - **Version caveat:** Unity 6.0 compiles C# 9 with listed unsupported features; Api Compatibility Level defaults to .NET Standard 2.1.

## References
- **[dotnet-test-mirror.md](references/dotnet-test-mirror.md):** `docs/tech-stack.md` or an ADR adopts a `dotnet test` mirror, the mirror fails to build, or it disagrees with the Edit Mode run.

## Scripts
- **[Combat.Core.Mirror.xml](scripts/Combat.Core.Mirror.xml):** adapt into `TestsDotnet/<Feature>/Core/<Feature>.Core.Mirror.csproj` → library over one engine-free asmdef.
  - **Contents:** linked `Assets/` sources and a `ProjectReference` per asmdef reference.
- **[Combat.Tests.Mirror.xml](scripts/Combat.Tests.Mirror.xml):** adapt into `TestsDotnet/<Feature>/Tests/<Feature>.Tests.Mirror.csproj` → test project over the feature's `Tests/EditMode/` sources.
  - **Contents:** pinned `LangVersion` and NUnit 3.x packages; version properties per [dotnet-test-mirror.md](references/dotnet-test-mirror.md).

## Steps
1. **Check every Core-layer asmdef (`<Feature>/Core`, `<Feature>/DataModels`) has `noEngineReferences: true`:** layout per `csharp-standards` → naming-convention.md → Folders.
   - **References:** only assemblies that are engine-free themselves.
   - **Why:** with the flag set, Unity adds no `UnityEngine`/`UnityEditor` references, so a leak fails compilation instead of review.
   - **Flag false or an engine-bound reference, Core in scope:** fix it in the same change (a write into the main checkout's `Assets/` holds the Editor, `core.md` Tools).
   - **Flag false or an engine-bound reference, Core not in scope:** report it to `technical-architect`.
2. **Run Core tests from the feature's `Tests/EditMode/` assembly (`…<Feature>.Tests.EditMode`) in Edit Mode by default:** Editor-only platform, NUnit reference, per `unity-test-framework` steps 2–3.
   - **Play Mode:** none for Core.
   - **Criterion:** the fixture appears under EditMode in the Test Runner and the run executes more than zero tests.
   - **Code coverage:** comes from this Edit Mode run (`unity-test-framework` step 14); a `dotnet test` mirror gives no Unity coverage figure.
3. **Write every Core test mirror-ready, mirror or not:** NUnit attributes and constraints only.
   - **Banned in Core tests:** `UnityEngine`, `UnityEditor` or `UnityEngine.TestTools` (`[UnityTest]`, `LogAssert`, allocation constraint).
   - **Fixtures:** C# data, not files under `Assets/`.
   - **Seed and clock:** inject them (`unity-test-framework` step 5).
   - **A test that needs a Unity API:** not a Core test → the feature's `Tests/PlayMode/`.
4. **Add a `dotnet test` mirror only when `docs/tech-stack.md` or an ADR adopts it:** never create one on your own.
   - **Not adopted and a real need exists (CI without an Editor licence, a sub-second loop):** `Needs-decision`, `Next: cto` with the cost.
5. **Build the adopted mirror per [dotnet-test-mirror.md](references/dotnet-test-mirror.md):** one `.csproj` per engine-free asmdef, its asmdef references as `ProjectReference`.
   - **Sources:** link the same `Assets/` sources, never copy.
   - **Pins:** `LangVersion` to the editor's C# version and the TFM to the Api Compatibility Level; package versions to what Unity resolves.
   - **Criterion:** `dotnet build` succeeds with zero edits under `Assets/`.
6. **Never change a source to satisfy one runner:** a `#if` added for the mirror, or a Core file needing `#if UNITY_*` to compile, is drift or a boundary leak.
   - **Action:** report it (`shared-core-boundary-audit` step 7), don't work around it.
7. **Mirror adopted (step 4) → run both runners and compare; a test that passes in only one runner is not a pass:** record pass/fail and the executed count per runner; counts must match.
   - **A disagreement is a defect:** never `[Ignore]` it to go green.
   - **Runtime difference (hashing, culture, float):** `core-determinism`.
   - **Compile difference:** the mirror config, per [dotnet-test-mirror.md](references/dotnet-test-mirror.md).
8. **Hand the CI wiring to `ci-cd-engineer` (`jenkins-pipeline-authoring`):** the mirror is an extra stage, not a replacement for the Edit Mode run, unless the adopting ADR says so.
   - **Empty result set:** fails the stage.

## Never
- **Mirror pass as shipped-build evidence:** reporting it as such — CoreCLR is neither the Editor's Mono nor a player's IL2CPP.
  - **Device behaviour:** needs a Player run (`build-release-engineer`, on the GD's request).
- **Mirror files at the project root:** putting the mirror's `.csproj` or `.sln` there — Unity's IDE integration regenerates `<asmdef>.csproj` and the `.sln` there and overwrites them.

## Output
```
## Core Tests Without Unity — <module>
- Core asmdef: noEngineReferences <true | false → fixed / reported>; references <engine-free | list>
- Runners: Edit Mode <assembly> · dotnet mirror <adopted by docs/tech-stack.md | ADR-NNN | not adopted>
- Mirror config: <TFM, LangVersion, linked globs, NUnit version> | n/a
- Results: Edit Mode <pass/fail, count, command> · mirror <pass/fail, count, command> — or "not run"
- Runner disagreement: <test → cause → routed to> | none
```

## Example
- **"The mirror is green, drop the Edit Mode run to save CI time":** declined — only the editor compiles with Unity's compiler and class libraries; the mirror can pass code Unity rejects.
  - **Done instead:** both stages stay unless an ADR says otherwise.
