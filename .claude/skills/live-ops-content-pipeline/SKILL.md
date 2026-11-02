---
name: live-ops-content-pipeline
description: "Remote config for live tuning: Firebase/Unity Remote Config, PlayFab Title Data, rollback. Use to plan live-ops tuning."
user-invocable: false
---

# Live-Ops Content Pipeline

- **Not for:** designing events or economy (GD).
- **Not for:** shipping new assets (`unity-addressables`).
- **Not for:** event analytics (`analytics-telemetry-platform`).
- **Not for:** backend platform choice (`backend-build-vs-buy`).
- **Not for:** post-release crashes (`crash-anr-fault-domain-triage`).
- **Not for:** the scoring rubric (`tco-reversibility-scoring`).

## Steps
1. **Establish the cadence the GDD plans:** weekly events, monthly balance, occasional hotfix are different problems.
   - **Low end:** a versioned config file shipped in the build and loaded at startup suffices; a platform is complexity nobody asked for.
2. **Separate tuning from content delivery:** remote config carries values already in the build (drop rates, prices, event windows).
   - **New content:** new items, characters or maps are asset delivery: Addressables or a CDN.
   - **Wrong purchase:** a config platform bought to ship content leaves the release dependency in place.
3. **Require a safe in-build default for every remote key:** first run, offline and failed fetch all execute before any remote value arrives.
4. **Shortlist by segmentation depth:** each platform segments differently.
   - **Firebase Remote Config:** conditions and A/B bound to Google Analytics.
   - **Unity Remote Config:** campaign/segment rules inside Unity Gaming Services.
   - **PlayFab Title Data:** only when PlayFab is already the backend.
   - **Custom:** full control at real build and ops cost.
5. **Measure the rollback blast window in minutes:** publish propagation + client fetch interval + cached-value activation.
   - **Example:** "supports rollback" with a twelve-hour fetch cadence is a twelve-hour window.
6. **Require staged rollout and a named publish authority:** percentage stages limit a wrong economy value.
   - **Open console:** a console anyone can publish from is an unguarded write path into the live economy.
7. **Define schema versioning and old-client behaviour on an unknown or missing key:** live players run months-old builds against one payload.
8. **Score survivors with `tco-reversibility-scoring`:** Medium reversibility when all reads go through one internal access module, Low when vendor SDK calls are scattered.
9. **Set the standard: every config read through one access module:** record it via `engineering-standard-adr-authoring`.
10. **Cadence, segmentation needs or the config-console operator unstated → `Needs-decision` naming it:** each moves the shortlist; an unowned publish path is not the CTO's to assume.

## Never
- **Industry-standard argument:** recommending a platform because it is industry standard — justify it against the stated cadence, or ship the config file.

## Output
```
## Live-Ops Content Pipeline Decision — <game>
- Cadence: weekly events | monthly balance | hotfix only
- Scope: value tuning only | tuning + asset delivery (<Addressables/CDN>)
- Platform warranted: yes/no — <why>
- Options: <shortlist, segmentation depth>
- Segmentation/A-B required: yes/no — <options meeting it>
- In-build defaults: all keys | gap: <keys>
- Rollback blast window: <propagation + fetch + activation> = <time>
- Staged rollout / publish authority: <stages> / <owner> | unowned
- Schema versioning: <old-client behaviour>
- TCO / Reversibility: <score>
- Decision: <platform | versioned config file, no platform> — <cadence tie>
- Standard set: <config consumption rule>
- Routed to: <...>
```

## Example
- **"Put the new event's items into remote config so we skip the store release":** declined.
  - **Why:** config carries values, not assets.
  - **Did instead:** Addressables/CDN for items, remote config for schedule, drop rates, pricing.
