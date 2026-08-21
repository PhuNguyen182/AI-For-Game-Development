---
name: analytics-telemetry-platform
description: >
  Build-vs-buy framework for the analytics/telemetry pipeline — a managed
  platform (Firebase Analytics), a managed platform with raw export (Firebase
  plus BigQuery), or a custom event pipeline into a warehouse the team owns —
  decided on data portability, COPPA/GDPR exposure, and whether crash/ANR
  telemetry is inside or outside the same vendor commitment. Use when
  choosing the analytics stack, a domain with no other owner on the team.
  Not for: event instrumentation once a platform is chosen
  (`tech-lead-sdk-platform`), reading results or choosing metrics
  (`producer`, `advisor`), production crash triage
  (`crash-anr-investigator`), the scoring rubric
  (`tco-reversibility-scoring`), player-data persistence
  (`backend-build-vs-buy`), remote-config cadence
  (`live-ops-content-pipeline`).
---

# Analytics / Telemetry Platform — pipeline build-vs-buy decision

## 1. Objective
Give the CTO explicit ownership of the analytics/telemetry infrastructure decision — a domain no other role on the team owns — so it becomes a deliberate build-vs-buy call instead of whichever SDK was integrated first.

## 2. Role
Act as a data-infrastructure-aware CTO, not a data analyst: this skill decides the pipeline, never what to conclude from the data once it lands.

## 3. When to invoke this skill
- Choosing the analytics/telemetry stack: a managed platform, a managed platform with raw export enabled, or a custom event pipeline.
- A vendor analytics SDK is about to be integrated without the portability and privacy questions having been asked.
- Negative trigger: the platform is chosen and the work is instrumenting events — that is `tech-lead-sdk-platform`'s integration work.
- Negative trigger: the question is what the numbers mean or which metrics matter for a design call — a GD/`producer`/`advisor` concern once the pipeline exists.
- Negative trigger: the question is production crash/ANR triage from live telemetry — that is `crash-anr-investigator`, a different concern from choosing the pipeline.

## 4. How to use this skill
1. **Establish what the data is actually needed for before shortlisting anything** — basic retention/funnel dashboards, or deep custom analysis feeding balance and monetization decisions. The second needs raw event export into a warehouse the team controls; the first does not, and paying for it is waste.
2. **Shortlist across all three shapes** — managed platform with dashboards only, managed platform with export enabled (Firebase plus BigQuery), fully custom pipeline. Skipping the middle option is the common error: it buys most of the portability at a fraction of the custom build's cost.
3. **Test data portability as a hard pass/fail, not a scoring nicety** — can raw event data be exported in a usable form, or does it only exist inside the vendor's dashboard? An unexportable history is exactly the exit cost that makes reversibility Low.
4. **Check privacy and compliance exposure early enough to disqualify** — COPPA and GDPR obligations follow the audience the GDD targets, present or planned. A compliance failure removes an option outright regardless of how it scored on cost.
5. **Score the survivors with `tco-reversibility-scoring`, weighting portability heavily** — analytics history compounds in value, and losing access to it on a vendor switch is the cost teams most reliably underweight at signing time.
6. **State explicitly whether crash/ANR telemetry is inside this decision or handled separately** — Firebase Crashlytics is commonly assumed to come with Firebase Analytics. Say which it is; leaving it implied is how a game ships with no crash reporting at all.
7. **Factor migration and backfill cost when a prior platform already holds history** — the go-forward TCO is not the whole bill if two years of events have to be moved or abandoned.
8. **Write the decision in English**, per `language-and-comments.md`'s Working language section — it is a durable artifact `tech-lead-sdk-platform` implements against; the Vietnamese reply to the GD is the final message, not the document.
9. **Ask when the target audience's jurisdictions or the depth of analysis needed are unknown** — those two inputs decide compliance and portability respectively, which between them decide the whole call. Do not assume the permissive answer.

## 5. Specific goals / tasks this skill performs
- Own the analytics/telemetry infra build-vs-buy decision explicitly, closing a gap no role currently covers.
- Make data portability a weighted, pass/fail-capable factor rather than an afterthought.
- Disqualify options that fail the project's privacy/compliance obligations before cost is weighed.
- State crash/ANR telemetry coverage explicitly in every verdict.
- Out of scope: instrumentation implementation (`tech-lead-sdk-platform`), data interpretation (`producer`, `advisor`), crash triage (`crash-anr-investigator`).

## 6. Output format
```
## Analytics / Telemetry Platform Decision — <project>
- Data need: basic dashboards / deep custom analysis / both
- Options considered: <managed> / <managed + export> / <custom>
- Data portability: pass/fail per option — <what export format, if any>
- Privacy/compliance: pass/fail — <jurisdictions checked>
- Existing history to migrate: none / <volume and source>
- TCO / Reversibility: <score from tco-reversibility-scoring>
- Rule compliance: decision written in English, per Working language
- Decision: <option> — <one line tying portability and compliance to the choice>
- Crash/ANR telemetry: covered by this decision / handled separately by <what>
- Routed to: `tech-lead-sdk-platform` for instrumentation
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line decision rationale with all three fields:
```
- Known limitations: <what this pipeline will not answer>
- Latent concerns: <assumptions holding only at current event volume or current jurisdictions>
- Future remediation: <the trigger for each — the volume, region, or pricing change that forces a revisit>
```

## 7. Examples
**Example 1**
- Input: a mid-core mobile game needing balance-tuning-grade analysis.
- Output: Firebase Analytics with BigQuery export — dashboards for day-to-day, raw events for the balance work, and portability satisfied because the warehouse side is the team's own. Crash/ANR stated as separately covered by Crashlytics.

**Example 2**
- Input: "just use Firebase, everyone does — we can figure out the data questions later."
- Output: declined as stated. Firebase may well win, but the export decision is not deferrable: enabling BigQuery export later does not backfill events collected before it was switched on, so "later" silently costs the entire history up to that point. Re-run as a decision now, with export on or off chosen deliberately.

**Example 3**
- Input: a small hardcore PC title, retention metrics only, EU audience.
- Output: managed dashboards alone, no export — the deep-analysis requirement that would justify a warehouse does not exist (YAGNI). GDPR consent handling flagged as a hard requirement on the instrumentation, routed to `tech-lead-sdk-platform`.

## 8. Edge cases & guardrails
- Never default to a platform because it is already in the project — check portability and privacy for this specific game first, per §4.
- Never leave crash/ANR coverage implied — an unstated assumption here ships as no crash reporting.
- Never treat a compliance failure as a cost penalty; it disqualifies the option.
- Never recommend a custom warehouse pipeline for a project whose stated need is retention dashboards — that is speculative complexity YAGNI already forbids.
- If the target jurisdictions or the required depth of analysis are unknown, ask — both are load-bearing, and the permissive guess is the expensive one.
