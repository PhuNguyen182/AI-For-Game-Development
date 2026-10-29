---
name: tech-vendor-dependency-risk-assessment
description: "Judge whether a plugin, SDK or engine dependency is safe to build on: maintenance, release cadence, backing, licence, lock-in, exit path — keep, mitigate or replace. Use when a dependency's future is in doubt."
user-invocable: false
---

# Tech Vendor / Dependency Risk Assessment

Not for: whether a new candidate is adoptable here — IL2CPP, engine version, `Game.Core.*` determinism, manifest duplication (`practical-fit-screening`), this project's own code (`code-reviewer`), trivial swappable utilities (say so and stop), SDK integration (`sdk-platform-engineer`), the exit-cost rubric (`tco-reversibility-scoring`), recording a standard (`engineering-standard-adr-authoring`).

## Steps
1. **Maintenance from activity and succession, not stars or downloads** — commit/release cadence, response time on breaking issues, single maintainer vs company/community. No readable repository (closed-source SDK) → record the signal as `unavailable`, score lock-in and exit cost higher; never infer health from vendor marketing.
2. **Licence against the project's commercial plans** — restrictions on commercial use, revenue share above a threshold, attribution the stores reject. This can end the assessment.
3. **Lock-in by depth, not call count** — one contained module is low; types shaping Shared Core data structures are high (removal changes the game's own model).
4. **Exit cost** — the `tco-reversibility-scoring` exit-cost bucket: effort and calendar time to replace if the vendor vanished tomorrow.
5. **Platform reach** against every GDD platform including planned ones; an unsupported committed platform is a decision already made.
6. **Weight lock-in and exit cost by gameplay criticality** — a rendering, physics or netcode foundation warrants scrutiny an analytics helper does not.
7. **Verdict is one of four, with a date or trigger:** keep; keep with a named mitigation (e.g. wrap behind an internal interface); replace now; replace by `<date or trigger>`. Weigh the replacement's own cost — keep-with-mitigation is often right when replacement is prohibitive.
8. **Precedent-setting verdict** (e.g. a 3-strikes escalation from `technical-architect`) → route the vetting rule to `engineering-standard-adr-authoring`.
9. Write the assessment in English (`core.md` Language).

## Never
- Accept "it works fine today" as a reason to skip the assessment or as evidence against replacement — the risk is the future.

## Output
```
## Vendor Risk Assessment — <dependency> <version>
- Maintenance signal: active / slowing / stalled / abandoned / unavailable — <evidence>
- Licence: pass / concern — <licence and clause>
- Integration lock-in: low / medium / high — <what it reaches into>
- Exit cost: <tco-reversibility-scoring bucket> — <effort and calendar estimate>
- Platform reach: pass/fail per committed and planned platform
- Gameplay criticality: low / medium / high
- Verdict: keep / keep with mitigation: <mitigation> / replace now / replace by <date or trigger>
- Routed to: `sdk-platform-engineer` to act; `engineering-standard-adr-authoring` if it sets precedent
```
On request only, add `Known limitations`, `Latent concerns` and `Future remediation`, each with its re-assessment trigger.

## Example
- "Rock solid for two years, nothing to assess" → declined: working today is evidence about the present; the maintenance signal had stalled eight months ago. Verdict keep with mitigation (wrap behind an internal interface).
