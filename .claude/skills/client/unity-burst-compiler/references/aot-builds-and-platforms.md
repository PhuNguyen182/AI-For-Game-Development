# AOT Builds & Platform Settings

Sources: [Building your project](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/building-projects.html), [Burst AOT Settings reference](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/building-aot-settings.html).
Covers: SKILL.md §4 — **"Set Burst AOT Settings per target platform explicitly"**.

What changes between Editor Play Mode and a Player build, and the settings that
govern only the latter. Everything here is invisible until an actual build
exists.

| Subject | What it decides | Source |
|---|---|---|
| AOT versus JIT | Player builds compile Burst code ahead of time into dynamic libraries; the Editor JIT-compiles on demand — two different paths, so Play Mode success proves nothing about a build | [Building your project](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/building-projects.html) |
| `Edit > Project Settings > Burst AOT Settings` | Per-platform Burst configuration; scoped to Player builds only, with no effect on Play Mode | [AOT Settings](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/building-aot-settings.html) |
| CPU Architecture | Which instruction sets the build targets on Windows, macOS, Linux, and Android — the setting that decides whether an intrinsic family is even available | [AOT Settings](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/building-aot-settings.html) |
| Platform toolchain support | Burst support and required toolchains differ per target, so a platform added late can fail at build time rather than at authoring time | [Building your project](https://docs.unity3d.com/Packages/com.unity.burst@1.8/manual/building-projects.html) |

**Critical caveat**: a build that produces no Burst-compiled code still runs —
it runs the managed fallback at managed speed. The failure presents as a
device-only performance regression, not as a build error, so check the build
log rather than inferring from the fact that it shipped.
