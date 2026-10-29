---
name: practical-fit-screening
description: "Hard-gate whether the project can adopt a candidate package: duplication vs manifest, engine and C# version, scripting backend, platforms, licence, Core boundary, maintenance. Use before ranking research candidates."
user-invocable: false
---

# Practical Fit Screening

Not for: finding candidates (`technology-scouting-sweep`), source trust (`source-credibility-grading`), ranking survivors (`solution-comparison-report`), device measurement (`rd-engineer`), integrating the winner (`sdk-platform-engineer`), keep/replace verdict on a dependency already in the project (`tech-vendor-dependency-risk-assessment`).

## Steps
1. **Check what the project already has first** — `Packages/manifest.json`, asmdefs, existing skills. A covered capability turns the question into "what does the existing one fail to do".
2. **Run hard gates and drop failures immediately**; never score or rank a candidate that failed one.
3. **Licence** — read the repository's own LICENSE file only (identifier: https://spdx.org/licenses). MIT, Apache-2.0, BSD, Unlicense pass; GPL/AGPL block shipped game code; Asset Store EULA, source-available or any non-commercial clause need the GD's explicit acceptance.
4. **Scripting backend, not just platform** — IL2CPP AOT-compiles and strips, so `System.Reflection.Emit`, runtime code generation and unconstrained generic virtual calls pass in the Editor and fail on device. Mono-only means PC-only.
5. **Engine and C# version** — the project's configured compiler decides what compiles, not the README (`csharp-standards` → `coding-principles.md` Modern C# syntax).
6. **`Game.Core.*` determinism** — a candidate pulling `UnityEngine` types, wall-clock time or unseeded randomness is blocked for Core (`coding-principles.md` Shared Core integrity) but may still pass for `Game.Client.*`.
7. **Mobile cost as a gate** — added binary size, per-ABI natives, hot-path allocation (`performance-and-algorithms.md` Memory discipline). PC-only fit fails a cross-platform feature.
8. **Soft criteria for survivors only** — maintenance and bus factor, adoption, integration effort, documentation, removal path. Exit cost: Low (hidden behind an interface) / Medium / High (its types appear in gameplay signatures).
9. **Gate needs a build, a device or a GD licence decision → `UNKNOWN`** with the exact question, routed to `rd-engineer`; never guess a pass.
10. **State every gate's verdict, passes included.**

## Output
```
## Fit Screen — <candidate> for <capability>
- Already in project: <package or API covering this | nothing found>
| Hard gate | Verdict | Evidence |
|---|---|---|
| Licence for commercial shipping | PASSED / BLOCKED / UNKNOWN | <SPDX id, LICENSE URL> |
| Engine and C# language version | PASSED / BLOCKED / UNKNOWN | <required vs project's> |
| Scripting backend and platforms | PASSED / BLOCKED / UNKNOWN | <IL2CPP AOT, per-ABI natives> |
| Game.Core.* determinism boundary | PASSED / BLOCKED / NOT APPLICABLE | <UnityEngine, clock or RNG dependency> |
| Mobile size and hot-path cost | PASSED / BLOCKED / UNKNOWN | <added size, allocation behaviour> |
- Soft criteria: <maintenance, adoption, integration effort, documentation>
- Exit cost: <Low / Medium / High — why>
- Decision: ADOPTABLE / BLOCKED — <deciding gate>
- Routed to: <solution-comparison-report / rd-engineer / technology-scouting-sweep>
```
On request only, add `Known limitations`, `Latent concerns` and `Future remediation`, each with its re-screen trigger.

## Example
- "It is GPL but only used internally in the Editor" → declined as an assumption: whether the tool ships in the build decides it; gate stays BLOCKED pending the GD's explicit acceptance.
