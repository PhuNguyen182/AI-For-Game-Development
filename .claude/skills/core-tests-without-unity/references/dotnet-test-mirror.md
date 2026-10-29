# dotnet test Mirror

Sources: [a] C# compiler `https://docs.unity.com/en-us/engine/6000.0/manual/programming-environment/overview-of-dot-net-in-unity/csharp-compiler`, [b] .NET profile support `.../overview-of-dot-net-in-unity/dotnet-profile-support`, [c] asmdef importer `.../script-compilation/assembly-definition-files/class-assembly-definition-importer`, [d] UTF Edit Mode vs Play Mode `com.unity.test-framework@2.0/manual/edit-mode-vs-play-mode-tests.html`, [e] Configure language version https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/configure-language-version, [f] Common MSBuild items https://learn.microsoft.com/en-us/visualstudio/msbuild/common-msbuild-project-items, [g] Unity NUnit package https://docs.unity3d.com/Packages/com.unity.ext.nunit@2.0/manual/index.html, [h] NUnit 4.0 migration https://docs.nunit.org/articles/nunit/release-notes/Nunit4.0-MigrationGuide.html.

## Unity side the mirror must match

| Setting | Fact that decides |
|---|---|
| `noEngineReferences` | "Unity does not add references to UnityEditor or UnityEngine assemblies when it compiles the assembly" [c]: the precondition that makes linking the sources possible |
| Edit Mode marker | Tests are Edit Mode by default when the assembly's only platform is Editor; other platforms need `[RequiresPlayMode(false)]` [d] |
| C# version | Unity 6.0: C# 9.0, with init-only setters, covariant returns, module initializers, `SkipLocalsInit` and unmanaged calling conventions unsupported; records need a self-declared `IsExternalInit` [a] |
| Api Compatibility Level | .NET Standard 2.1 is the default; the alternative is .NET Framework [b]. Read it in Player Settings before choosing the TFM |
| NUnit | `com.unity.ext.nunit` is "based on NUnit version 3.5" [g] |
| `Assets/csc.rsp` | Extra compiler options and defines Unity applies; the mirror repeats each one or drops none silently |

## Layout

| Path | Fact that decides |
|---|---|
| `Tests.Dotnet/` at the repo root, outside `Assets/` | Unity never imports it; the root itself holds Unity-generated `.csproj`/`.sln` files that get overwritten |
| `Tests.Dotnet/Game.Core.Mirror/Game.Core.Mirror.csproj` | Library over linked Core sources; `AssemblyName` `Game.Core` so `InternalsVisibleTo` and type names match the editor build |
| `Tests.Dotnet/Game.Core.Mirror.Tests/Game.Core.Mirror.Tests.csproj` | Test project over linked test sources; `AssemblyName` `Game.Core.Tests` for the same reason |
| `.gitignore` | `Tests.Dotnet/**/bin/`, `Tests.Dotnet/**/obj/` |

```xml
<!-- Tests.Dotnet/Game.Core.Mirror/Game.Core.Mirror.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>netstandard2.1</TargetFramework>
    <LangVersion>9.0</LangVersion>
    <AssemblyName>Game.Core</AssemblyName>
    <RootNamespace>Game.Core</RootNamespace>
    <EnableDefaultCompileItems>false</EnableDefaultCompileItems>
    <Nullable>disable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <Compile Include="..\..\Assets\Game.Core\**\*.cs"
             Exclude="..\..\Assets\Game.Core\Tests\**"
             Link="%(RecursiveDir)%(Filename)%(Extension)" />
  </ItemGroup>
</Project>
```

```xml
<!-- Tests.Dotnet/Game.Core.Mirror.Tests/Game.Core.Mirror.Tests.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <LangVersion>9.0</LangVersion>
    <AssemblyName>Game.Core.Tests</AssemblyName>
    <IsPackable>false</IsPackable>
    <EnableDefaultCompileItems>false</EnableDefaultCompileItems>
  </PropertyGroup>
  <ItemGroup>
    <Compile Include="..\..\Assets\Game.Core\Tests\**\*.cs"
             Link="Tests\%(RecursiveDir)%(Filename)%(Extension)" />
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="..\Game.Core.Mirror\Game.Core.Mirror.csproj" />
    <!-- Exact versions, recorded in docs/tech-stack.md; NUnit stays on 3.x. -->
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="$(TestSdkVersion)" />
    <PackageReference Include="NUnit" Version="$(NUnitVersion)" />
    <PackageReference Include="NUnit3TestAdapter" Version="$(NUnitAdapterVersion)" />
  </ItemGroup>
</Project>
```

The three version properties live in `Tests.Dotnet/Directory.Build.props`, so nothing outside `Tests.Dotnet/` is affected.

## Settings that decide whether the mirror is honest

| Setting | Fact that decides |
|---|---|
| `LangVersion` | Pin the editor's version (`9.0` for Unity 6.0) [a]. `latest` is machine-dependent and "makes builds unreliable" [e]; `default` follows the SDK, so the mirror accepts syntax Unity rejects |
| Core `TargetFramework` | `netstandard2.1` to match the default compat level [b]: an API missing in Unity fails here too. Project on the .NET Framework level → the mirror cannot match exactly; `Needs-decision` |
| Test `TargetFramework` | Needs a runnable TFM; an LTS the CI agent's SDK has. A newer `LangVersion` than the TFM's default "isn't supported" [e]; an older one (9.0) is allowed |
| `Link` metadata | "The notational path to be displayed when the file is physically located outside the influence of the project file" [f]: display only, the file on disk stays the single source |
| `EnableDefaultCompileItems` false | Stops the SDK globbing stray `.cs` under `Tests.Dotnet/` into the build |
| Exclude `Tests\**` from Core | Otherwise test sources compile into `Game.Core` and NUnit becomes a Core dependency |
| NUnit major version | Unity's runner is 3.5-based [g]; NUnit 4 moves classic asserts (`Assert.AreEqual`) to `NUnit.Framework.Legacy.ClassicAssert` and is not source-compatible with 3.x [h], so shared files stop compiling in one runner |
| Packages the Core asmdef references (NRandom, MemoryPack, …) | Same package at the same version from NuGet, including any source generator; a version gap is a runner disagreement waiting to happen |

## Running

| Command | Fact that decides |
|---|---|
| `dotnet test Tests.Dotnet/Game.Core.Mirror.Tests/Game.Core.Mirror.Tests.csproj --logger "trx;LogFileName=core-mirror.trx"` | Always pass the project path; a bare `dotnet test` at the root meets Unity's generated `.sln` and `.csproj` files instead of the mirror |
| Executed count | Compare with the Edit Mode count for `Game.Core.Tests`; a filtered or uncompiled file shows only as a lower count |

## Disagreement triage (SKILL.md step 7)

| Symptom | Likely cause | Route |
|---|---|---|
| Compiles in mirror, fails in Editor | C# feature Unity lists as unsupported [a], or an API outside its class libraries | Fix the source; tighten the mirror config |
| Compiles in Editor, fails in mirror | Missing package, `csc.rsp` define, or a Unity reference that should not be in Core | Mirror config, or a boundary leak (`shared-core-boundary-audit`) |
| Same test, different result | Hash order, culture, float codegen | `core-determinism` |

Unverified: whether `netstandard2.1` plus `LangVersion` 9.0 rejects every C# 9 feature Unity lists as unsupported (it rejects features whose runtime types are missing from `netstandard2.1`, not necessarily all); which NUnit 3.x attributes added after 3.5 Unity's runner ignores; the `csc.rsp` location and semantics on the project's editor version.
