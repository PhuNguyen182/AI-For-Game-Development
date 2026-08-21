# Root Links — NRandom v2.0.2

Source: the root index pages listed below, as provided for this skill.
Covers: the whole skill — provenance and version anchor for every file in
this folder.

Anchors every link in this folder to the NRandom v2.0.2 release. Anything
this skill cites resolves under one of these roots; anything that does not
is out of scope for the skill, not merely undocumented here.

| Root | Holds | Source |
|---|---|---|
| GitHub repository (README) | Usage guide, installation steps, Unity integration section | [nuskey8/NRandom](https://github.com/nuskey8/NRandom) |
| Source tree, pinned to `v2.0.2` | `IRandom`/`RandomEx`/algorithm/collection implementation | [NRandom @ v2.0.2 — src/NRandom](https://github.com/nuskey8/NRandom/tree/v2.0.2/src/NRandom) |
| NuGet package | Version history, install command | [NRandom on NuGet](https://www.nuget.org/packages/NRandom) |

Every source-tree link in this folder is pinned to the `v2.0.2` tag — the
latest tagged release at authoring time — so a cited method or field still
exists at that exact commit even if `main` later changes. Confirm the
project's installed NRandom version against this pin before trusting a cited
signature; re-verify against the live source tree if the project has since
upgraded. NRandom requires .NET Standard 2.1 or higher — the same floor as
this project's other `dotnet-*` skills and Unity's default Api Compatibility
Level.
