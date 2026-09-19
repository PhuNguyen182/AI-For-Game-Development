---
name: practical-fit-screening
description: >
  Hard-gate screen deciding whether this project can actually adopt a
  candidate package, SDK or technique. Gates: duplication against
  `Packages/manifest.json` and existing assemblies, engine and C# language
  version, scripting backend (IL2CPP AOT stripping, `System.Reflection.Emit`,
  generic virtual calls), platform and binary-size cost, licence via SPDX
  identifier and LICENSE file, `Game.Core.*` determinism boundary,
  maintenance bus factor, integration and exit cost. Use before ranking any
  candidate. Not for: finding candidates (`technology-scouting-sweep`),
  grading a source's trust (`source-credibility-grading`), ranking the
  survivors (`solution-comparison-report`), measuring on device
  (`rd-engineer`), integrating the winner (`tech-lead-sdk-platform`).
---

# Practical Fit Screening — can this project actually adopt the candidate

## 1. Objective
Drop every candidate this project cannot adopt before any effort goes into ranking it, and state each gate's verdict explicitly so a pass is never confused with an unchecked assumption. It exists to stop four expensive discoveries made late: a licence that forbids shipping, a package that works in the Editor and dies under IL2CPP on device, a dependency that drags `UnityEngine` types into `Game.Core.*`, and a "new" package doing what the project already has.

## 2. Role
Act as the adoption gate for the research track — the screen every external candidate passes before it may appear in a comparison, applying this project's real constraints rather than the candidate's own claims about itself.

## 3. When to invoke this skill
- A candidate set exists and must be reduced to what is genuinely adoptable here.
- A single candidate looks strong and its licence, engine version or platform support is unconfirmed.
- Something is destined for `Game.Core.*` and its dependencies have not been checked against the determinism boundary.
- A mobile target is in scope and the candidate ships native plugins or leans on runtime code generation.
- Negative trigger: no candidates exist yet — that's `technology-scouting-sweep`.
- Negative trigger: the question is whether a source can be trusted at all — that's `source-credibility-grading`.
- Negative trigger: candidates already passed and must be ranked into a recommendation — that's `solution-comparison-report`.
- Negative trigger: the gate needs numbers from a real build or device — that's a spike, owned by `rd-engineer`.
- Negative trigger: the winner is chosen and needs wiring into the project — that's `tech-lead-sdk-platform` or the owning implementation role.

## 4. How to use this skill
1. **Check what the project already has before screening anything external** — read `Packages/manifest.json`, the assembly definitions and the existing skill set. A capability already covered turns the question into "what does the existing one fail to do", which is a different question with a different owner.
2. **Run the hard gates first and drop failures immediately** — licence, scripting backend, engine and language version, determinism boundary. A candidate failing any one of these cannot be adopted at any quality level, so scoring it further only inflates the comparison.
3. **Read the licence against shipping a commercial game** — MIT, Apache-2.0, BSD and Unlicense are safe to link; GPL and AGPL are disqualifying for shipped game code; Asset Store EULA terms, "source-available" and any non-commercial clause need the GD's explicit acceptance, never an assumption. Resolve the identifier at https://spdx.org/licenses.
4. **Verify the scripting backend, not merely the platform** — IL2CPP ahead-of-time compiles and strips, so `System.Reflection.Emit`, runtime code generation and unconstrained generic virtual calls can pass in the Editor and fail on device. A Mono-only candidate is a PC-only candidate.
5. **Check the engine and C# language version the candidate requires against the project's own, per coding-principles.md's Modern C# syntax section** — the project's configured compiler decides what compiles, not the package's README.
6. **Gate anything destined for `Game.Core.*` on determinism, per coding-principles.md's Shared Core integrity section** — a candidate pulling `UnityEngine` types, wall-clock time or unseeded randomness into Core is disqualified there whatever its quality, and may still pass for `Game.Client.*`.
7. **Weigh mobile cost as a gate, not a footnote** — added binary size, per-ABI native libraries, and runtime allocation behaviour in hot paths, per performance-and-algorithms.md's Memory discipline section. Mobile is the tighter budget, so a candidate that only fits on PC fails a cross-platform feature.
8. **Score the soft criteria only for candidates that cleared every hard gate** — maintenance signal and bus factor, adoption breadth, integration effort, documentation quality, and how the project would remove it later.
9. **Rate exit cost by how far the candidate's types would spread** — one hidden behind an interface is cheap to replace; one whose types appear in gameplay signatures across the codebase is a structural commitment that outlives the feature.
10. **State every gate's verdict, including the ones that passed** — an unstated pass is indistinguishable from a gate nobody ran, which is how a licence problem reaches production.
11. **Mark a gate `UNKNOWN` and name what would settle it whenever the answer needs a real build or device** — route that to `rd-engineer` rather than guessing a pass, because a guessed gate is worse than an open one.

## 5. Specific goals / tasks this skill performs
- A pass or fail verdict per hard gate, per candidate, with the evidence behind each.
- Candidates that cannot ship here removed before ranking, with the disqualifying gate named.
- The duplication check against what the project already contains, run first.
- Soft criteria scored only for survivors: maintenance, integration cost, exit cost, mobile cost.
- Gates needing measurement marked `UNKNOWN` with the spike that would settle them.
- Out of scope: finding candidates (`technology-scouting-sweep`), source trust (`source-credibility-grading`), ranking (`solution-comparison-report`), device measurement (`rd-engineer`), integration (`tech-lead-sdk-platform`).

## 6. Output format
```
## Fit Screen — <candidate> for <capability>
- Already in project: <the package or API covering this | nothing found>
| Hard gate | Verdict | Evidence |
|---|---|---|
| Licence for commercial shipping | PASSED / BLOCKED / UNKNOWN | <SPDX id, LICENSE URL> |
| Engine and C# language version | PASSED / BLOCKED / UNKNOWN | <required vs project's> |
| Scripting backend and platforms | PASSED / BLOCKED / UNKNOWN | <IL2CPP AOT, per-ABI natives> |
| Game.Core.* determinism boundary | PASSED / BLOCKED / NOT APPLICABLE | <UnityEngine, clock or RNG dependency> |
| Mobile size and hot-path cost | PASSED / BLOCKED / UNKNOWN | <added size, allocation behaviour> |
- Soft criteria: <maintenance and bus factor, adoption, integration effort, documentation>
- Exit cost: <Low behind an interface / Medium / High — how far its types would spread>
- Decision: ADOPTABLE / BLOCKED — <the gate that decided it>
- Routed to: <solution-comparison-report / rd-engineer / technology-scouting-sweep>
```

**Extended report — emit ONLY when the requester asks for it.** It adds all three fields below the decision:
```
- Known limitations: <gates left UNKNOWN and why — for example no device available to confirm IL2CPP behaviour>
- Latent concerns: <a single-maintainer repository, a licence that changed once already, a platform not yet in scope>
- Future remediation: <the re-screen trigger for each concern — the engine upgrade, platform addition or licence change>
```

## 7. Examples
**Example 1**
- Input: a high-star mesh-processing package for a PC-and-mobile feature.
- Output: licence PASSED as MIT from its LICENSE file; engine version PASSED; scripting backend BLOCKED — it relies on `System.Reflection.Emit`, which IL2CPP cannot AOT compile, so it works in the Editor and fails on device. Decision BLOCKED, and the sweep is re-entered rather than the candidate ranked.

**Example 2**
- Input: "it is GPL but we are only using it internally in the Editor, that is fine."
- Output: declined as an assumption. Editor-only use is a real distinction, but whether the tool ships inside the build decides it, and that is a licence question with commercial consequences. The gate stays BLOCKED pending the GD's explicit acceptance, per §4.

**Example 3**
- Input: a deterministic maths library proposed for `Game.Core.*`.
- Output: licence and version gates PASSED; determinism gate BLOCKED for Core because the library depends on `UnityEngine` types, per the Shared Core integrity rule. Re-screened for `Game.Client.*`, where it passes every gate, and routed on with that boundary stated.

## 8. Edge cases & guardrails
- Never rank a candidate that failed a hard gate; its presence makes the winner's margin look earned when it was not.
- Never accept a licence claim from anywhere but the repository's own LICENSE file — that is the one gate whose error is legally expensive.
- Never treat "works in the Editor" as platform support; the scripting backend, not the Editor, decides what runs on device.
- Never let a candidate into `Game.Core.*` that drags `UnityEngine`, wall-clock time or unseeded randomness with it, per the Shared Core integrity rule.
- Never record a silent pass — a gate with no stated verdict is a gate nobody ran.
- If a gate needs a build, a device or a licence decision the GD owns, mark it `UNKNOWN` with the exact question — do not guess a pass to keep the candidate alive.
