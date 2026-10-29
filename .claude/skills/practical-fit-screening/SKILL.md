---
name: practical-fit-screening
description: "Hard-gate whether the project can adopt a candidate package, technique or service: duplication, engine and C# version, scripting backend, platforms, licence, Core boundary, pricing, data compliance. Use before ranking research candidates."
user-invocable: false
---

# Practical Fit Screening

Not for: finding candidates (`technology-scouting-sweep`), source trust (`source-credibility-grading`), ranking survivors (`solution-comparison-report`), device measurement (`rd-engineer`), integrating the winner (`sdk-platform-engineer`), keep/replace verdict on a dependency already in the project (`tech-vendor-dependency-risk-assessment`).

## Steps
1. **Check what the project already has first** — `docs/tech-stack.md`, `Packages/manifest.json`, asmdefs, `Assets/Plugins/` and any other vendor folder or DLL under `Assets/` (Asset Store and `.unitypackage` SDKs never reach the manifest), existing skills. A covered capability turns the question into "what does the existing one fail to do".
2. **Run hard gates and drop failures immediately**; never score or rank a candidate that failed one. The subject type picks the gates — package/SDK: all but the two service rows; technique: engine and C#, backend, Core boundary, hot-path cost, plus licence only when a reference implementation's code is reused; hosted service: all rows, the package gates applied to its Unity SDK. A gate that does not apply is `NOT APPLICABLE`, never skipped.
3. **Licence** — read the repository's own LICENSE file only (identifier: https://spdx.org/licenses); Asset Store: the licence named on the package page. MIT, Apache-2.0, BSD, Unlicense pass; GPL/AGPL block shipped game code; Asset Store EULA, source-available or any non-commercial clause need the GD's explicit acceptance.
4. **Scripting backend, not just platform** — IL2CPP AOT-compiles and strips, so `System.Reflection.Emit`, runtime code generation and unconstrained generic virtual calls pass in the Editor and fail on device. Mono-only means PC-only.
5. **Engine and C# version** — the project's configured compiler decides what compiles, not the README (`csharp-standards` → `coding-principles.md` Modern C# syntax).
6. **`Game.Core.*` determinism** — a candidate pulling `UnityEngine` types, wall-clock time or unseeded randomness is blocked for Core (`coding-principles.md` Shared Core integrity) but may still pass for `Game.Client.*`.
7. **Mobile cost as a gate** — added binary size, per-ABI natives, hot-path allocation (`performance-and-algorithms.md` Memory discipline). PC-only fit fails a cross-platform feature.
8. **Hosted service only** — pricing at the project's projected scale, read from the vendor's current pricing page (free tier limits included); data compliance against `CLAUDE.md` → Compliance (COPPA/GDPR, data residency, player-data deletion) and whether player data can be exported on exit. Long-term vendor health is `tech-vendor-dependency-risk-assessment`, not this gate.
9. **Soft criteria for survivors only** — maintenance and bus factor, adoption, integration effort, documentation, removal path. Exit cost: Low (hidden behind an interface) / Medium / High (its types appear in gameplay signatures).
10. **Gate needs a build, a device or a GD decision → `UNKNOWN`** with the exact question — build or device to `rd-engineer`, licence or pricing to the GD (`Needs GD`); never guess a pass.
11. **State every gate's verdict, passes included.**

## Output
```
## Fit Screen — <candidate> for <capability>
- Subject type: package/SDK / technique / hosted service
- Already in project: <package, plugin or API covering this — where found | nothing found>
| Hard gate | Verdict | Evidence |
|---|---|---|
| Licence for commercial shipping | PASSED / BLOCKED / UNKNOWN / NOT APPLICABLE | <SPDX id, LICENSE URL> |
| Engine and C# language version | PASSED / BLOCKED / UNKNOWN | <required vs project's> |
| Scripting backend and platforms | PASSED / BLOCKED / UNKNOWN | <IL2CPP AOT, per-ABI natives> |
| Game.Core.* determinism boundary | PASSED / BLOCKED / NOT APPLICABLE | <UnityEngine, clock or RNG dependency> |
| Mobile size and hot-path cost | PASSED / BLOCKED / UNKNOWN | <added size, allocation behaviour> |
| Service pricing at projected scale | PASSED / BLOCKED / UNKNOWN / NOT APPLICABLE | <pricing URL, retrieved date, cost at scale> |
| Data compliance and export | PASSED / BLOCKED / UNKNOWN / NOT APPLICABLE | <COPPA/GDPR, residency, export path> |
- Soft criteria: <maintenance, adoption, integration effort, documentation>
- Exit cost: <Low / Medium / High — why>
- Decision: ADOPTABLE / BLOCKED — <deciding gate>
- Routed to: <solution-comparison-report / rd-engineer / technology-scouting-sweep>
```
On request only, add `Known limitations`, `Latent concerns` and `Future remediation`, each with its re-screen trigger.

## Example
- "It is GPL but only used internally in the Editor" → declined as an assumption: whether the tool ships in the build decides it; gate stays BLOCKED pending the GD's explicit acceptance.
