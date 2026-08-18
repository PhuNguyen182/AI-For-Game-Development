---
name: tech-vendor-dependency-risk-assessment
description: >
  Due-diligence rubric for judging whether a third-party plugin, SDK, or
  engine-level dependency is safe to keep building on — maintenance signal,
  license compatibility, integration lock-in depth, exit cost, and platform
  reach — ending in a keep/mitigate/replace verdict. Use this before
  committing to a new foundational third-party dependency, or when Technical
  Architect escalates a repeated technical failure that traces back to a
  specific dependency (e.g. an unmaintained plugin). Do not use this to
  review the quality or correctness of this project's own code — that's
  code-reviewer's job. Do not use this for a trivial, easily-swappable
  utility with no gameplay-critical surface.
---

# Tech Vendor / Dependency Risk Assessment

## 1. Objective
Give the CTO (and, by extension, Technical Architect surfacing a concerning dependency) a consistent rubric for judging whether a third-party plugin/SDK/library is safe to keep building on, so a foundational vendor risk gets caught before it becomes a repeated production failure.

## 2. Role
Act as a vendor-risk-focused technical due-diligence reviewer.

## 3. When to invoke this skill
- Before committing to a new third-party plugin/SDK/library as a foundational dependency (not a one-off utility).
- When Technical Architect escalates a repeated technical failure that traces back to a specific third-party dependency, to determine whether to replace it.
- Negative trigger: don't use this to review the quality/correctness of this project's own code — that's `code-reviewer`'s job.
- Negative trigger: don't use this for a trivial, easily-swappable utility with no gameplay-critical surface — the risk isn't worth formalizing; use ordinary judgment.

## 4. How to use this skill
1. Check maintenance signal: recent commit/release activity, how quickly the maintainer has historically responded to breaking issues, whether it's a single-maintainer project or backed by a company/community with succession plans.
2. Check license terms: is the license compatible with this project's commercial plans (some "free" SDKs restrict commercial use, impose revenue share above a threshold, or require attribution incompatible with store requirements)?
3. Check integration depth / lock-in: how deeply does this project's code call into the dependency? A dependency called from one contained module is low lock-in; one whose API shapes core Shared Core data structures is high lock-in.
4. Check exit cost: if this vendor disappeared tomorrow, what would it take to replace it — score with `tco-reversibility-scoring`'s exit-cost bucket.
5. Check platform reach: does it support every platform this project ships to, including future planned platforms in the GDD?
6. Weigh gameplay criticality: a rendering/physics/netcode-foundational dependency deserves far more scrutiny than a one-off analytics helper — apply more weight to lock-in and exit cost the more foundational the dependency is.
7. Conclude with a clear verdict: keep as-is / keep with a mitigation (e.g. wrap it behind an internal interface to reduce lock-in) / replace now / replace on a defined timeline.

## 5. Specific goals / tasks this skill performs
- Produce a keep/mitigate/replace verdict for any foundational third-party dependency, backed by maintenance signal, license, lock-in, and exit-cost checks.
- Catch vendor risk before it becomes a repeated production failure, not just after.
- Out of scope: reviewing this project's own code quality (`code-reviewer`); day-to-day SDK integration work (`tech-lead-sdk-platform`).

## 6. Output format
```
## Vendor Risk Assessment — <dependency name>
- Maintenance signal: active / slowing / stalled / abandoned
- License compatibility: pass / concern (detail)
- Integration depth / lock-in: low / medium / high
- Exit cost: <from tco-reversibility-scoring>
- Platform reach: pass/fail per committed platform
- Gameplay criticality: low / medium / high
- Verdict: keep / keep with mitigation / replace now / replace on <timeline>
```

## 7. Examples
**Example 1**
- Input: three consecutive Code Review failures traced back to an unmaintained third-party physics plugin.
- Output: maintenance signal = abandoned, gameplay criticality = high; verdict = replace now, recorded as a CTO standard for how future plugin choices get vetted.

**Example 2**
- Input: an actively-maintained ad mediation SDK with an acceptable license, evaluated before integration.
- Output: maintenance signal = active, lock-in = low (wrapped behind an internal interface), exit cost = low; verdict = keep, no mitigation needed.

## 8. Edge cases & guardrails
- A dependency "working fine today" is not evidence against replacing it if maintenance signal has genuinely stalled — the risk concerns the future, not the present state.
- Don't recommend "replace now" without weighing the real cost of the replacement itself — "keep with mitigation" (wrap it behind an interface) is sometimes the responsible call even for a risky dependency, if replacement cost is currently prohibitive.
- If this assessment is triggered by a 3-strikes escalation from Technical Architect, the verdict becomes a CTO standard going forward — record it via `engineering-standard-adr-authoring`.
