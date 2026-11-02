---
name: analytics-telemetry-platform
description: "Analytics build-vs-buy: Firebase, BigQuery export, custom pipeline. Use when choosing the analytics stack."
user-invocable: false
---

# Analytics / Telemetry Platform

- **Not for:** event instrumentation (`sdk-platform-engineer`).
- **Not for:** choosing metrics or reading results (GD with `researcher`).
- **Not for:** production crash triage (`crash-anr-investigator`).
- **Not for:** scoring rubric (`tco-reversibility-scoring`).
- **Not for:** player-data persistence (`backend-build-vs-buy`).
- **Not for:** remote-config cadence (`live-ops-content-pipeline`).

## Steps
1. **Target jurisdictions or needed analysis depth unknown → `Needs-decision` naming them:** they decide compliance and portability; do not assume the permissive answer.
2. **Establish the data need:** basic retention/funnel dashboards, or deep custom analysis for balance and monetization.
   - **Deep analysis:** needs raw export to a warehouse the team controls.
   - **Basic need only:** do not pay for deep analysis.
3. **Shortlist all three shapes:** managed dashboards only, managed + raw export (Firebase + BigQuery), custom pipeline.
   - **Middle shape:** managed + raw export buys most portability at a fraction of custom cost.
4. **Portability is pass/fail:** can raw events be exported usably, or live only in the vendor dashboard?
   - **Export timing:** export enabled later does not backfill earlier events, so decide export on/off now.
5. **Compliance gate:** COPPA/GDPR follow the GDD's present or planned audience; failure disqualifies, never a cost penalty.
   - **Consent handling:** required consent handling (e.g. GDPR) is a hard requirement handed to `sdk-platform-engineer` in Routed to.
6. **Score survivors with `tco-reversibility-scoring`:** weight portability heavily (history compounds; loss on switch is the most underweighted cost).
   - **Prior platform:** add migration/backfill cost if a prior platform holds history.
7. **State whether crash/ANR telemetry is inside this decision:** Crashlytics is not implied by Firebase Analytics; or name what handles it separately.
8. **Re-decision triggers:** on request, name what re-opens this decision: volume, region, pricing.

## Output
```
## Analytics / Telemetry Platform Decision — <project>
- Data need: basic dashboards / deep custom analysis / both
- Options considered: <managed> / <managed + export> / <custom>
- Data portability: pass/fail per option — <export format>
- Privacy/compliance: pass/fail — <jurisdictions checked>
- Existing history to migrate: none / <volume, source>
- TCO / Reversibility: <score>
- Decision: <option> — <portability and compliance tied to choice>
- Crash/ANR telemetry: covered here / handled separately by <what>
- Routed to: `sdk-platform-engineer`
```

## Example
- **"Just use Firebase, decide data questions later":** declined — export is not deferrable; BigQuery export does not backfill, so "later" forfeits all earlier history. Decide export on/off now.
