---
name: live-ops-content-pipeline
description: >
  Framework for deciding whether a dedicated remote-config platform is
  warranted for live content and economy tuning, and which one — Firebase
  Remote Config, Unity Remote Config, PlayFab Title Data, or a versioned
  config file — so events and balance ship without an app store release.
  Weighs cadence need, segmentation and A/B targeting, staged rollout and
  rollback safety, and schema versioning against config-consuming code. Use
  when choosing the infrastructure behind live content cadence.
  Not for: designing the events or economy themselves (GD), event analytics (`analytics-telemetry-platform`), backend platform choice (`backend-build-vs-buy`), post-release crash triage (`crash-anr-fault-domain-triage`), the scoring rubric (`tco-reversibility-scoring`).
---

# Live-Ops Content Pipeline — remote config for content and economy cadence

## 1. Objective
Decide what infrastructure, if any, the game needs to change events and economy values without shipping a build — so the choice matches the GDD's real cadence, keeps a bad value's blast window measured in minutes, and never buys a value-tuning service to solve an asset-delivery problem it structurally cannot solve.

## 2. Role
Act as a live-service infrastructure CTO who has run an economy on remote config in production, including the day a wrong value reached every client at once.

## 3. When to invoke this skill
- Choosing the remote-config or live-ops content platform for a game planning an ongoing event and balance cadence.
- Deciding whether a dedicated platform is warranted at all, against a GDD that may only need occasional patches.
- An existing config approach has produced an incident — a bad value, a slow rollback, or an old client breaking on a new key — and the platform choice itself is in question.
- Negative trigger: designing what the events, rewards, or economy curves actually are — that is the GD's design work, which this infrastructure only delivers.
- Negative trigger: which events get instrumented and where the data lands — that is `analytics-telemetry-platform`.
- Negative trigger: the backend service, auth, and player-data platform underneath — that is `backend-build-vs-buy`.
- Negative trigger: post-release crash and ANR triage from production telemetry — that is `crash-anr-fault-domain-triage`, an unrelated concern despite the shared "live-ops" label.
- Negative trigger: the cost/reversibility arithmetic itself — that rubric is `tco-reversibility-scoring`.

## 4. How to use this skill
1. **Establish the cadence the GDD actually plans before shortlisting any platform** — weekly events, monthly balance passes, and occasional hotfixes are three different problems. At the low end a versioned config file shipped with the build and loaded at startup is sufficient, and a dedicated platform is complexity nobody asked for (KISS/YAGNI).
2. **Separate value tuning from content delivery, because remote config only does the first** — changing a drop rate, a price, or an event window is tuning data already in the build; shipping a new item, character, or map is asset delivery and belongs to Addressables or a CDN. Buying a config platform to ship content is the most expensive way to discover it cannot.
3. **Require every remote value to have a safe in-build default** — first run, offline play, and a failed fetch all execute before any remote value arrives. Without defaults the config service stops being a tuning tool and becomes a launch dependency that takes the game down with it.
4. **Shortlist by segmentation depth rather than brand** — Firebase Remote Config offers conditions and A/B testing bound to Google Analytics; Unity Remote Config offers campaign and segment rules inside Unity Gaming Services; PlayFab Title Data is worth shortlisting only when PlayFab is already the backend; a custom service buys full control at real build and operations cost.
5. **Measure the rollback path in minutes, not in whether the vendor lists it** — the blast window is publish propagation plus the client's fetch interval plus cached-value activation. A platform that supports rollback but leaves a twelve-hour client fetch cadence has a twelve-hour window in which every player holds the bad value.
6. **Require staged rollout and a named publish authority before the platform is accepted** — a percentage rollout lets a wrong economy value reach one percent instead of everyone, and a console that anyone can publish from is an unguarded write path into the live economy.
7. **Define config schema versioning and what an old client does with an unknown or missing key** — live players run months-old builds while the service serves one payload to all of them, so a key added for the current build must degrade predictably on older ones rather than throwing.
8. **Score the surviving options with `tco-reversibility-scoring`** — this choice rates Medium reversibility when config reads go through one internal access module, and Low when vendor SDK calls are scattered across gameplay code, which makes step 9 a cost decision rather than a style preference.
9. **Set the consumption standard in code — every config read through one access module, never a scattered SDK call** — and record it via `engineering-standard-adr-authoring`, since this convention is what keeps the platform swappable later.
10. **Write the decision and its reasoning in English**, per `language-and-comments.md`'s Working language section — only the closing reply to the GD is Vietnamese.
11. **Ask before deciding when planned cadence, segmentation needs, or who operates the config console is unstated** — each one alone moves the shortlist, and an unowned publish path is a decision the CTO cannot make alone.

## 5. Specific goals / tasks this skill performs
- Decide whether a dedicated live-ops content platform is warranted at all, judged against the GDD's stated cadence.
- Choose among the realistic options by segmentation depth, rollback speed, and existing backend fit.
- Establish the rollback blast window as a measured number rather than a vendor feature checkbox.
- Define schema versioning and old-client behaviour before the first key is added.
- Set the code-side consumption standard that keeps the choice reversible.
- Out of scope: designing event and economy content (GD), analytics instrumentation (`analytics-telemetry-platform`), backend and player-data platform (`backend-build-vs-buy`), crash and ANR triage (`crash-anr-fault-domain-triage`), the scoring rubric (`tco-reversibility-scoring`).

## 6. Output format
```
## Live-Ops Content Pipeline Decision — <game>
- Planned cadence: weekly events | monthly balance | occasional hotfix only
- Scope check: value tuning only | tuning + asset delivery — <asset path, if any: Addressables/CDN>
- Dedicated platform warranted: yes/no — <why, against the cadence>
- Options considered: <shortlist, with the segmentation depth each offers>
- Segmentation/A-B required: yes/no — <which options meet it>
- In-build defaults: defined for every remote key | gap: <keys with no safe default>
- Rollback blast window: <publish propagation + fetch interval + activation> = <minutes/hours>
- Staged rollout: <percentage stages> — publish authority: <named owner> | unowned
- Schema versioning: <unknown-key and missing-key behaviour on older clients>
- TCO / Reversibility: <score from tco-reversibility-scoring>
- Rule compliance: decision written in English, per Working language
- Decision: <platform or "versioned config file, no platform"> — <one line tying cadence to the choice>
- Standard set: <how config values must be consumed in code>
- Routed to: <role or skill that acts on this next>
```

**Extended report — emit ONLY when the requester asks for it.** It replaces the one-line `Decision` rationale with all three fields:
```
- Known limitations: <what this pipeline cannot deliver — typically anything requiring new assets>
- Latent concerns: <what holds only at current cadence, player count, or client-version spread>
- Future remediation: <the re-open trigger for each — a cadence increase, a segmentation requirement, an incident>
```

## 7. Examples
**Example 1**
- Input: a mobile mid-core game with weekly events and monthly economy passes.
- Output: cadence warrants a dedicated platform. Firebase Remote Config chosen for its conditions and A/B support; rollback blast window measured at the client fetch interval and tightened by shortening it for economy keys specifically. Staged rollout defined at one, ten, then a hundred percent, with the live-ops producer named as publish authority. Standard set: all reads through one config access module. Recorded via `engineering-standard-adr-authoring`.

**Example 2**
- Input: "put the new event's items into remote config so we can ship content without an app store release."
- Output: declined as specified. Remote config carries values, not assets — new items need art, prefabs, and often new code paths, none of which a config payload delivers. The correct split is Addressables or a CDN for the content itself, with remote config carrying the event's schedule, drop rates, and pricing. Buying the config platform for the asset job would have left the release dependency exactly where it was.

**Example 3**
- Input: a PC hardcore title with rare balance patches and no event cadence.
- Output: no dedicated platform warranted; a versioned config file shipped with the build and loaded at startup covers the actual need at zero ongoing cost. The re-open trigger is stated explicitly — a move to a monthly-or-faster cadence, or any requirement to target a player segment — so the decision can be revisited on a condition rather than a hunch.

## 8. Edge cases & guardrails
- Never recommend a dedicated platform because it is industry-standard — justify it against the GDD's stated cadence, or ship the config file.
- Never let a remote-config purchase stand in for asset delivery, per §4 — the release dependency it was bought to remove will still be there.
- Never accept a platform without measuring the rollback blast window — "supports rollback" is not a number, and the number is what a bad economy value costs.
- Never ship a remote key with no safe in-build default — offline and first-run players execute that path before any value arrives.
- Never leave old-client behaviour on an unknown key undefined — the live population always spans build versions.
- Never let config reads scatter across gameplay code — that alone drops reversibility from Medium to Low and locks in the vendor.
- If cadence, segmentation needs, or the publish authority is unstated, ask — an unowned write path into the live economy is not a detail to assume.
