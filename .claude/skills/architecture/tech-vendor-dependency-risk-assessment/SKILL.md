---
name: tech-vendor-dependency-risk-assessment
description: >
  Due-diligence rubric for judging whether a third-party plugin, SDK, or
  engine-level dependency is safe to keep building on — maintenance signal
  (release cadence, single-maintainer versus company-backed), license
  compatibility with commercial shipping, integration lock-in depth, exit
  cost, and platform reach against every committed platform — ending in a
  keep / keep-with-mitigation / replace-now / replace-on-timeline verdict.
  Use before committing to a foundational dependency, or when a repeated
  failure traces back to one.
  Not for: reviewing this project's own code (`code-reviewer`), trivial
  swappable utilities, SDK integration work (`tech-lead-sdk-platform`),
  the scoring rubric (`tco-reversibility-scoring`), recording the outcome as
  a standard (`engineering-standard-adr-authoring`).
---

# Tech Vendor / Dependency Risk Assessment — keep, mitigate, or replace

## 1. Objective
Give the CTO — and Technical Architect surfacing a concerning dependency — a consistent rubric for judging whether a third-party plugin, SDK, or library is safe to keep building on, so foundational vendor risk is caught before it becomes a repeated production failure.

## 2. Role
Act as a vendor-risk technical due-diligence reviewer: the person who asks what happens when this dependency stops being maintained, not whether it works today.

## 3. When to invoke this skill
- Before committing to a new third-party plugin, SDK, or library as a foundational dependency.
- When Technical Architect escalates a repeated technical failure that traces back to a specific dependency, to decide whether it gets replaced.
- When a dependency's maintenance signal visibly changes — a maintainer steps away, a release cadence stalls, a license changes.
- Negative trigger: the code under question is this project's own — that is `code-reviewer`'s job, and this rubric measures nothing useful about it.
- Negative trigger: a trivial, easily-swappable utility with no gameplay-critical surface — formalising that risk costs more than the risk.
- Negative trigger: the dependency is already chosen and the work is integrating it — that is `tech-lead-sdk-platform`.

## 4. How to use this skill
1. **Read maintenance signal from activity and succession, not from stars or download counts** — recent commit and release cadence, historical response time to breaking issues, and whether a single maintainer or a company/community with succession backs it. Popularity is a lagging indicator; an abandoned project stays popular for years.
2. **Check the license against this project's actual commercial plans** — some free SDKs restrict commercial use, impose revenue share above a threshold, or require attribution the target stores will not accept. This can end the assessment before anything else is scored.
3. **Measure integration lock-in by how deep the dependency reaches, not by how much code calls it** — one contained module calling it heavily is low lock-in; a dependency whose types shape Shared Core data structures is high, because removing it changes the game's own model.
4. **Score exit cost with `tco-reversibility-scoring`'s exit-cost bucket** — answer the concrete question of what replacing it would take if the vendor disappeared tomorrow, in effort and calendar time.
5. **Check platform reach against every platform in the GDD, including planned ones** — a dependency that does not support a committed future platform is a decision already made against that platform, whether or not anyone has noticed.
6. **Weight lock-in and exit cost by gameplay criticality** — a rendering, physics, or netcode foundation deserves scrutiny an analytics helper does not. The same lock-in score means something different at each end of that range.
7. **Conclude with one of four verdicts, never a summary of concerns** — keep as-is; keep with a named mitigation (wrap it behind an internal interface to cut lock-in); replace now; replace on a defined timeline. A verdict without a date or a trigger is not a verdict.
8. **Write the assessment in English**, per `language-and-comments.md`'s Working language section — it is a durable record other roles act on; the Vietnamese reply to the GD is the final message, not the document.
9. **Route the verdict onward when it sets precedent** — a 3-strikes escalation from Technical Architect makes the outcome a standing rule for how future dependencies get vetted, and that belongs in `engineering-standard-adr-authoring` rather than in this one assessment.
10. **Ask when maintenance signal cannot be established** — a closed-source SDK with no public repository has no readable cadence. Say the signal is unavailable and score lock-in and exit cost higher for it; do not infer health from the vendor's own marketing.

## 5. Specific goals / tasks this skill performs
- Produce a keep / mitigate / replace verdict for any foundational third-party dependency, backed by maintenance, license, lock-in, exit-cost, and platform-reach checks.
- Catch vendor risk before it becomes a repeated production failure rather than after.
- Name a concrete mitigation whenever the verdict is "keep with mitigation", not a general intention to reduce coupling.
- Escalate precedent-setting verdicts into a recorded standard.
- Out of scope: this project's own code quality (`code-reviewer`), day-to-day SDK integration (`tech-lead-sdk-platform`), trivial swappable utilities.

## 6. Output format
```
## Vendor Risk Assessment — <dependency name> <version>
- Maintenance signal: active / slowing / stalled / abandoned / unavailable — <evidence>
- License: pass / concern — <license and the specific clause>
- Integration lock-in: low / medium / high — <what it reaches into>
- Exit cost: <from tco-reversibility-scoring> — <effort and calendar estimate>
- Platform reach: pass/fail per committed platform, including planned
- Gameplay criticality: low / medium / high
- Rule compliance: assessment written in English, per Working language
- Verdict: keep / keep with mitigation: <the mitigation> / replace now / replace by <date or trigger>
- Routed to: `tech-lead-sdk-platform` to act; `engineering-standard-adr-authoring` if this sets precedent
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line verdict rationale with all three fields:
```
- Known limitations: <what this assessment could not verify — closed source, unpublished roadmap>
- Latent concerns: <risks not yet realised: single maintainer still active, license unchanged so far>
- Future remediation: <the re-assessment trigger for each — the cadence gap, license change, or platform commitment that forces a revisit>
```

## 7. Examples
**Example 1**
- Input: three consecutive Code Review failures traced to an unmaintained third-party physics plugin.
- Output: maintenance signal abandoned (no release in two years, issues unanswered), gameplay criticality high, lock-in high — its types appear in Shared Core. Verdict: replace now. Routed to `engineering-standard-adr-authoring`, since a 3-strikes escalation makes the vetting rule itself the durable outcome.

**Example 2**
- Input: "it has been rock solid for two years, there is nothing to assess."
- Output: declined as a reason to skip the assessment. Working today is evidence about the present; this rubric measures the future, and the maintenance signal had in fact stalled eight months ago. Assessed as normal — verdict landed on keep with mitigation, wrapping it behind an internal interface to cut lock-in from high to low before the risk matures.

**Example 3**
- Input: an actively-maintained ad mediation SDK, evaluated before integration, already wrapped behind an interface.
- Output: signal active, license compatible, lock-in low, exit cost low, all committed platforms covered. Verdict: keep, no mitigation needed — adding one would be complexity with nothing to buy.

## 8. Edge cases & guardrails
- Never accept "it works fine today" as evidence against replacement — the risk is about the future, and a stalled maintainer is the signal, not current behaviour.
- Never recommend "replace now" without weighing the replacement's own cost — keep-with-mitigation is often the responsible call for a risky dependency when replacement is currently prohibitive.
- Never infer maintenance health from vendor marketing or download counts when the repository is unreadable — record the signal as unavailable and raise the lock-in weighting instead.
- Never leave a verdict without a date or a trigger — "replace eventually" is the outcome this rubric exists to prevent.
- If the dependency is trivial and swappable, say so and stop; formalising it is overhead this skill's own scope rules out.
