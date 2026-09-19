---
name: solution-comparison-report
description: >
  Turns screened candidates into one dated, sourced recommendation. Fixes
  comparison axes before the matrix is filled, names the single deciding
  axis, picks the practical optimum for today, names the runner-up with the
  condition that would flip the call, separates documented claims from
  unmeasured ones, pins the recommendation to a version, and routes by what
  it commits the project to: `cto` for a hard-to-reverse or paid bet,
  `rd-engineer` for a spike, `technical-architect` for a Tech Spec. Use once
  candidates pass screening. Not for: finding candidates
  (`technology-scouting-sweep`), grading sources
  (`source-credibility-grading`), the adoption gates
  (`practical-fit-screening`), scoring a strategic bet
  (`tco-reversibility-scoring`).
---

# Solution Comparison Report — ranking screened candidates into one recommendation

## 1. Objective
Produce a recommendation someone can act on: one option, the reason it wins, the runner-up, and the condition that would change the answer — without manufacturing a winner where the candidates genuinely tie, presenting an unmeasured claim as measured, or letting a recommendation read as current a year after the picture was taken.

## 2. Role
Act as the synthesis step of the research track — the point where screened candidates stop being a list and become a single defensible call, framed so the role that owns the decision can take it without redoing the research.

## 3. When to invoke this skill
- Two or more candidates cleared `practical-fit-screening` and must become one answer.
- One candidate survived and the report must still state what it was compared against and what it costs.
- Every candidate failed the feature's must-haves and the finding needs to be delivered as a finding.
- Negative trigger: candidates are still being collected — that's `technology-scouting-sweep`.
- Negative trigger: a source's trustworthiness is in question — that's `source-credibility-grading`.
- Negative trigger: candidates have not passed the licence, platform and version gates — that's `practical-fit-screening`.
- Negative trigger: the decision is a strategic, hard-to-reverse bet needing total-cost and reversibility scoring — that's `tco-reversibility-scoring`, run by `cto`.

## 4. How to use this skill
1. **Compare only candidates that passed screening** — carrying a disqualified option into the matrix makes the winner's margin look earned when the field was never real.
2. **Fix the comparison axes before filling a single cell** — the feature's must-haves first, then maintenance, integration cost, performance profile, exit cost. Axes chosen after the data is visible get chosen to fit the preferred answer.
3. **Name the single deciding axis explicitly** — the one where the candidates genuinely differ and the difference matters for this feature. Everything else is context.
4. **Declare a tie when there is no deciding axis, and recommend the lower-risk option on that basis** — a manufactured winner is worse than an honest tie, because it hides that the choice was free.
5. **Prefer the boring, maintained, already-adopted option at equal fit, per coding-principles.md's KISS section** — a second library doing what an existing one nearly does is complexity bought without a requirement.
6. **Separate documented claims from measured ones in every cell** — anything not measured on this project's hardware is `unverified`, per performance-and-algorithms.md's Verification section, and a claim that decides the call becomes a spike request rather than a conclusion.
7. **Name the runner-up together with the condition that would flip the call** — "X, unless the mobile build's AOT rules out Y's codegen, which only a device test settles". A recommendation with no flip condition cannot be revisited intelligently.
8. **Pin the recommendation to a version and stamp the date the picture was taken** — "the best option today" has a shelf life, and an undated recommendation is read as current for as long as it survives in the repository.
9. **Route by what the recommendation commits the project to** — hard-to-reverse or paid goes to `cto`; needs measurement goes to `rd-engineer`; accepted and ready to specify goes to `technical-architect`; a vendor SDK to wire in goes to `tech-lead-sdk-platform`.
10. **Return "no recommendation" as a valid result when every candidate fails the must-haves** — say what building it in-house would take instead, since an unmet requirement is the finding.
11. **Write the report in English, per language-and-comments.md's Working language section** — it is a durable artifact; only the final message back to the GD is Vietnamese.

## 5. Specific goals / tasks this skill performs
- One recommendation, pinned to a version, dated, with its deciding axis named.
- A comparison matrix over screened candidates only, on axes fixed in advance.
- A runner-up carrying the condition that would flip the call.
- Every unmeasured claim marked `unverified` and, where load-bearing, converted into a spike request.
- An explicit route to the role that owns the next step.
- Out of scope: candidate discovery (`technology-scouting-sweep`), source trust (`source-credibility-grading`), adoption gates (`practical-fit-screening`), strategic cost and reversibility scoring (`tco-reversibility-scoring`).

## 6. Output format
```
## Solution Comparison — <capability>
- Candidates compared: <names — screened survivors only>
- Axes fixed before comparison: <must-haves, then maintenance, integration, performance, exit cost>
| Candidate | <must-have> | Maintenance | Integration cost | Performance | Exit cost |
|---|---|---|---|---|---|
| <name @version> | <fact — source tier> | <last release, contributors> | <effort> | <figure — measured/unverified> | <Low/Med/High> |
- Deciding axis: <the axis that separates them, and why it matters here> — or "none: genuine tie"
- Recommendation: <name @version> — <one line tying the deciding axis to the choice>
- Runner-up: <name @version> — flips if <the condition>
- Unverified: <claims needing measurement, each with the spike that would settle it>
- Picture taken: <date> — restate if <the release or version bump that invalidates it>
- Decision: RECOMMENDED / TIE — LOWER RISK CHOSEN / NO VIABLE CANDIDATE
- Routed to: <cto / rd-engineer / technical-architect / tech-lead-sdk-platform>
```

**Extended report — emit ONLY when the requester asks for it.** It adds all three fields below the decision:
```
- Known limitations: <what the comparison does not cover — an axis nobody could source, a candidate not fully evaluated>
- Latent concerns: <a winner with one maintainer, a licence under review, an axis that only matters past a scale not yet reached>
- Future remediation: <the re-evaluation trigger for each concern — the scale, release or date that invalidates the call>
```

## 7. Examples
**Example 1**
- Input: two screened runtime mesh-cutting packages for a PC-and-mobile feature.
- Output: axes fixed on concave-mesh support, maintenance, integration cost and mobile allocation behaviour; deciding axis is concave support, which the feature requires and only one candidate has. Recommendation pinned to that version and dated, mobile allocation marked unverified, routed to `rd-engineer` for the device measurement before the Tech Spec is written.

**Example 2**
- Input: "just recommend the one with more stars, it is obviously better."
- Output: declined. Stars measure past adoption, not fit; here both candidates clear the must-haves and differ on exit cost, which is the deciding axis for a type that would appear across gameplay signatures. The lower-exit-cost option wins, and the star gap is reported as context.

**Example 3**
- Input: three candidates, all failing the feature's must-have of deterministic simulation.
- Output: `NO VIABLE CANDIDATE`, with the must-have each one fails, and an outline of what an in-house deterministic implementation would need. Routed to `cto`, since building it is a commitment beyond the research role.

## 8. Edge cases & guardrails
- Never manufacture a winner where the candidates tie on every axis that matters; say it is a tie and pick on risk.
- Never present a performance number you did not measure as measured — unverified is the honest label, per the Verification rule.
- Never let star count, download count or recency of a blog post stand in for the deciding axis.
- Never recommend replacing something already in the project without stating what the existing one fails to do.
- Never ship a recommendation without a version pin and a date; an undated call is read as current forever.
- Never carry a candidate that failed a hard gate into the matrix, however strong it looks on other axes.
- If the choice commits the project to something hard to reverse or paid, recommend but do not decide — route to `cto` with the evidence intact.
