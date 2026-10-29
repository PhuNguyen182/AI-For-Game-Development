---
name: solution-comparison-report
description: "Turn screened candidates into one dated, sourced recommendation: fixed axes, deciding axis, runner-up and its flip condition, staleness trigger. Use when 2+ candidates survive screening."
user-invocable: false
---

# Solution Comparison Report

Not for: finding candidates (`technology-scouting-sweep`), grading sources (`source-credibility-grading`), adoption gates (`practical-fit-screening`), scoring a strategic bet (`tco-reversibility-scoring`).

## Steps
1. **Compare only candidates that passed screening** — a disqualified option in the matrix fakes the winner's margin. One survivor: still state what it was compared against and its cost. All failed the must-haves: return `NO VIABLE CANDIDATE`, name the must-have each fails, outline what in-house would take.
2. **Fix the axes before filling any cell** — feature must-haves first, then maintenance, integration cost, performance, exit cost.
3. **Name the single deciding axis** — where candidates genuinely differ for this feature. No such axis: declare a tie and pick the lower-risk option.
4. **At equal fit prefer the maintained, already-adopted option**; replacing something in the project requires stating what it fails to do. Stars, downloads and blog recency are context, never the deciding axis.
5. **Mark every claim not measured on this project's hardware `unverified`**; a claim that decides the call becomes a spike request.
6. **Name the runner-up with the condition that flips the call** (e.g. "X, unless AOT rules out Y's codegen, which only a device test settles").
7. **Pin the recommendation to a version and date it** — an undated call reads as current forever.
8. **Route by commitment**: hard-to-reverse or paid → `cto` (recommend, do not decide); needs measurement → `rd-engineer`; accepted → `technical-architect`; vendor SDK to wire → `sdk-platform-engineer`.

## Output
```
## Solution Comparison — <capability> (English)
- Candidates compared: <screened survivors only>
- Axes fixed before comparison: <list>
| Candidate | <must-have> | Maintenance | Integration cost | Performance | Exit cost |
|---|---|---|---|---|---|
| <name @version> | <fact — source tier> | <last release> | <effort> | <figure — measured/unverified> | Low/Med/High |
- Deciding axis: <axis and why> — or "none: genuine tie"
- Recommendation: <name @version> — <deciding axis tied to choice>
- Runner-up: <name @version> — flips if <condition>
- Unverified: <claims, each with the spike that settles it>
- Picture taken: <date> — restate if <release/version that invalidates it>
- Decision: RECOMMENDED / TIE — LOWER RISK CHOSEN / NO VIABLE CANDIDATE
- Routed to: <role>
```
On request only, add `Known limitations`, `Latent concerns`, `Future remediation` (each with its re-evaluation trigger).

## Example
- "Pick the one with more stars" → declined: both clear the must-haves and differ on exit cost, the deciding axis; stars reported as context.
