---
name: analytics-telemetry-platform
description: >
  Build-vs-buy framework for the analytics/telemetry pipeline (a managed
  platform like Firebase Analytics, a managed platform with raw data export,
  or a fully custom event pipeline into a data warehouse), weighted by data
  portability and privacy/compliance requirements. Use this whenever the CTO
  needs to decide the analytics/telemetry stack — a domain that currently
  has no other clear owner in the team. Do not use this for the actual
  event-instrumentation implementation once a platform is chosen — that's
  tech-lead-sdk-platform's integration work. Do not use this for
  interpreting analytics results or deciding what metrics matter for a
  design decision.
---

# Analytics / Telemetry Platform

## 1. Objective
Give the CTO explicit ownership of the analytics/telemetry infrastructure decision — a domain with no other clear owner in the team — so it's a deliberate build-vs-buy call rather than something that falls through the cracks.

## 2. Role
Act as a data-infrastructure-aware CTO, not a data analyst — this skill decides the pipeline, not what to do with the data once it lands.

## 3. When to invoke this skill
- Deciding the analytics/telemetry stack: a vendor platform (Firebase Analytics, etc.), a custom event pipeline into a data warehouse, or a hybrid.
- Negative trigger: don't use this for the actual event-instrumentation implementation once a platform is chosen — that's `tech-lead-sdk-platform`'s integration work.
- Negative trigger: don't use this for interpreting analytics results or defining what metrics matter for a design decision — that's a GD/Producer/Advisor concern once the pipeline exists.

## 4. How to use this skill
1. Establish what the data is actually needed for: basic retention/funnel metrics (a managed platform's dashboards are enough), or deep custom analysis feeding balance/monetization decisions (may need raw event export into a warehouse the team controls).
2. Shortlist options: a managed platform (Firebase Analytics, with free dashboards but limited raw-data control), a managed platform with data export enabled (e.g. Firebase + BigQuery export), or a fully custom event pipeline.
3. Check data ownership/portability: can raw event data be exported in a usable form, or is it locked inside the vendor's dashboard? This is a direct reversibility factor.
4. Check privacy/compliance requirements (COPPA/GDPR-relevant if the game has or may have players in relevant jurisdictions) — this can disqualify an option regardless of cost.
5. Score shortlisted options with `tco-reversibility-scoring`, weighting data portability heavily — analytics history has real long-term value, and losing access to historical data on a vendor switch is a cost most teams underweight.
6. Decide, and state whether the choice covers crash/ANR telemetry needs too, or whether that's handled separately (e.g. Firebase Crashlytics, per `tech-lead-sdk-platform`) — avoid assuming one vendor decision silently covers both.

## 5. Specific goals / tasks this skill performs
- Own the analytics/telemetry infra build-vs-buy decision explicitly, closing the gap that no role currently owns it.
- Make data portability/export capability an explicit, weighted factor, not an afterthought.
- Out of scope: instrumentation implementation, data interpretation, and crash/ANR reporting infra (related but separate — confirm it's covered, don't assume).

## 6. Output format
```
## Analytics/Telemetry Platform Decision
- Data need: basic dashboards / deep custom analysis / both
- Options considered: ...
- Data portability/export: pass/fail per option
- Privacy/compliance check: pass/fail
- TCO/Reversibility score: ...
- Decision: ...
- Crash/ANR telemetry coverage: covered by this decision / handled separately by <what>
```

## 7. Examples
**Example 1**
- Input: a mid-core mobile game needing balance-tuning-grade analysis.
- Output: Firebase Analytics + BigQuery export recommended, satisfying both dashboard convenience and data portability.

**Example 2**
- Input: a small hardcore PC title with basic retention needs only.
- Output: Firebase Analytics dashboards alone recommended, no export needed given no deep analysis requirement.

## 8. Edge cases & guardrails
- Don't default to "just use Firebase" without checking the data-portability and privacy requirements for this specific project.
- If historical analytics data already exists from a prior platform, factor migration/backfill cost into the decision, not just the go-forward TCO.
- Confirm explicitly whether crash/ANR telemetry is in scope of this decision or already handled — never leave that ambiguous in the output.
