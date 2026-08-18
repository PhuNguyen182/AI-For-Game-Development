---
name: live-ops-content-pipeline
description: >
  Framework for deciding whether a dedicated remote-config/live-ops content
  platform (Firebase Remote Config, PlayFab Title Data, or a custom config
  service) is warranted, and which one, so events and economy tuning can
  ship on a cadence without an app store release. Use this whenever the CTO
  is asked to choose the infrastructure behind live content/event cadence.
  Do not use this for designing what the events or economy tuning actually
  are — that's a GD/design decision. Do not confuse this with the live-ops
  agent group's crash/ANR stability work (crash-anr-investigator) — that is
  post-release stability triage from production crash telemetry, a
  completely different concern from content-cadence infrastructure.
---

# Live-Ops Content Pipeline

## 1. Objective
Give the CTO a consistent framework for choosing the infrastructure that lets the game update events, economy tuning, and other content on a cadence without requiring an app store release for every change.

## 2. Role
Act as a live-service infrastructure-focused CTO.

## 3. When to invoke this skill
- Deciding the remote-config/live-ops content platform for a game that plans an ongoing content/event cadence.
- Negative trigger: don't use this for designing what the events/economy tuning actually are — that's a GD/design decision.
- Negative trigger: don't confuse this with the `live-ops` agent group's crash/ANR stability work (`crash-anr-investigator`) — that's post-release stability triage from production crash telemetry, a completely different concern from content-cadence infrastructure.

## 4. How to use this skill
1. Establish the actual cadence need: how often does the GDD expect content/economy changes to ship (weekly events? monthly balance passes? rare hotfixes only)? A low-cadence game may not need a dedicated live-ops platform at all — a simple versioned config file loaded at startup can suffice (KISS/YAGNI).
2. If a dedicated platform is warranted, shortlist realistic options: Firebase Remote Config (good for simple flag/value tuning, tightly coupled to Firebase analytics), PlayFab Title Data (good if already using PlayFab for backend), or a custom config service (full control, more build/maintenance cost).
3. Check the requirement for targeting/segmentation (e.g. A/B testing a balance change on a player segment before global rollout) — not every option supports this at the same depth.
4. Score shortlisted options with `tco-reversibility-scoring` — this choice is usually Medium reversibility if config-consuming code reads through a thin internal abstraction, Low if game code calls the vendor SDK directly all over the codebase.
5. Check the update-safety story: can a bad remote config value be rolled back quickly without a client update? This is a real operational risk factor, not just a cost line.
6. Decide, and set the convention for how config values should be consumed in code (e.g. always through one config-access module, never scattered SDK calls) as a standard for Technical Architect/Engineers to follow.

## 5. Specific goals / tasks this skill performs
- Decide whether a dedicated live-ops content platform is warranted at all, and which one, based on actual cadence need.
- Ensure the chosen approach has a safe rollback story for bad remote values.
- Out of scope: designing event/economy content itself; post-release crash/ANR live-ops (a different domain, owned by `crash-anr-investigator`).

## 6. Output format
```
## Live-Ops Content Pipeline Decision
- Cadence need: ...
- Dedicated platform warranted: yes/no
- Options considered: ...
- Segmentation/A-B support required: yes/no, and which options meet it
- Rollback safety: ...
- TCO/Reversibility score: ...
- Decision: ...
- Standard set: <how code must consume config values going forward>
```

## 7. Examples
**Example 1**
- Input: a mobile mid-core game with weekly events.
- Output: Firebase Remote Config recommended, with a standard requiring all config reads to go through one wrapper module.

**Example 2**
- Input: a PC hardcore niche title with rare balance patches only.
- Output: no dedicated platform needed; a versioned config file loaded at startup is sufficient.

## 8. Edge cases & guardrails
- Don't recommend a dedicated live-ops platform just because it's common industry practice — justify it against the GDD's actual cadence plan (YAGNI).
- Never let this skill's scope bleed into crash/ANR live-ops — if the request is actually about stability/crash telemetry, redirect to `crash-anr-investigator`.
- A rollback-unsafe option should be disqualified or explicitly flagged as a residual risk, not silently accepted for its cost/feature advantages alone.
