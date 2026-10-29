---
name: core-tests-without-unity
description: "Game.Core asmdef noEngineReferences, Game.Core.Tests in Edit Mode, optional dotnet test mirror: csproj linking Assets/ sources, LangVersion 9.0, netstandard2.1, NUnit-only tests. Use when Core tests must run without scenes or outside the Editor."
user-invocable: false
---

# Core Tests Without Unity

Not for: test assembly attributes, Unity comparers and `-runTests` (`unity-test-framework`), which cases to write (`risk-based-test-planning`), the CI stage and report publishing (`jenkins-pipeline-authoring`), the replay test itself (`core-determinism`), bootstrapping the asmdefs on a new project (`new-project`), auditing a diff for `UnityEngine` leaks (`shared-core-boundary-audit`).
Docs: Unity manual `https://docs.unity.com/en-us/engine/6000.0/manual/` (replace `6000.0` with the project's editor) and UTF `https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/`; Microsoft Learn for MSBuild and `LangVersion`. Unity 6.0 compiles C# 9 with listed unsupported features; Api Compatibility Level defaults to .NET Standard 2.1.

| Reference | Read when |
|---|---|
| [dotnet-test-mirror.md](references/dotnet-test-mirror.md) | `docs/tech-stack.md` or an ADR adopts a `dotnet test` mirror, the mirror fails to build, or it disagrees with the Edit Mode run |

## Steps
1. **Check `Game.Core.asmdef` has `noEngineReferences: true`** and references only assemblies that are engine-free themselves (layout: `new-project`). With the flag set, Unity adds no `UnityEngine`/`UnityEditor` references, so a leak fails compilation instead of review. Flag false or an engine-bound reference → fix it in the same change if Core is in scope (an `Assets/` write holds the Editor, `core.md` Tools), else report it to `technical-architect`.
2. **Run Core tests from `Game.Core.Tests` in Edit Mode by default** — Editor-only platform, NUnit reference, per `unity-test-framework` steps 2–3. No Play Mode for Core. Criterion: the fixture appears under EditMode in the Test Runner and the run executes more than zero tests.
3. **Write every Core test mirror-ready, mirror or not**: NUnit attributes and constraints only; no `UnityEngine`, `UnityEditor` or `UnityEngine.TestTools` (`[UnityTest]`, `LogAssert`, allocation constraint); fixtures as C# data, not files under `Assets/`; inject the seed and clock (`unity-test-framework` step 5). A test that needs a Unity API is not a Core test → `Game.Client.Tests`.
4. **Add a `dotnet test` mirror only when `docs/tech-stack.md` or an ADR adopts it.** Not adopted and a real need exists (CI without an Editor licence, a sub-second loop) → `Needs-decision`, `Next: cto` with the cost; never create one on your own.
5. **Build the adopted mirror per [dotnet-test-mirror.md](references/dotnet-test-mirror.md)**: link the same `Assets/` sources, never copy; pin `LangVersion` to the editor's C# version and the TFM to the Api Compatibility Level; pin package versions to what Unity resolves. Criterion: `dotnet build` succeeds with zero edits under `Assets/`.
6. **Never change a source to satisfy one runner.** A `#if` added for the mirror, or a Core file needing `#if UNITY_*` to compile, is drift or a boundary leak → report it (`shared-core-boundary-audit` step 7), don't work around it.
7. **Mirror adopted (step 4) → run both runners and compare; a test that passes in only one runner is not a pass.** Record pass/fail and the executed count per runner; counts must match. A disagreement is a defect: runtime difference (hashing, culture, float) → `core-determinism`; compile difference → the mirror config, per the same file. Never `[Ignore]` it to go green.
8. **Hand the CI wiring to `ci-cd-engineer`** (`jenkins-pipeline-authoring`): the mirror is an extra stage, not a replacement for the Edit Mode run, unless the adopting ADR says so; an empty result set fails the stage.

## Never
- Report a mirror pass as evidence for the shipped build — CoreCLR is neither the Editor's Mono nor a player's IL2CPP; device behaviour needs a Player run (`build-release-engineer`, on the GD's request).
- Put the mirror's `.csproj` or `.sln` at the project root — Unity's IDE integration regenerates `<asmdef>.csproj` and the `.sln` there and overwrites them.

## Output
```
## Core Tests Without Unity — <module>
- Core asmdef: noEngineReferences <true | false → fixed / reported>; references <engine-free | list>
- Runners: Edit Mode <assembly> · dotnet mirror <adopted by docs/tech-stack.md | ADR-NNN | not adopted>
- Mirror config: <TFM, LangVersion, linked globs, NUnit version> | n/a
- Results: Edit Mode <pass/fail, count, command> · mirror <pass/fail, count, command> — or "not run"
- Runner disagreement: <test → cause → routed to> | none
- Known limitations: <e.g. no Player run>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "The mirror is green, drop the Edit Mode run to save CI time" → declined: only the editor compiles with Unity's compiler and class libraries; the mirror can pass code Unity rejects. Both stages stay unless an ADR says otherwise.
