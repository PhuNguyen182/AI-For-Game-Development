---
name: release
description: "Prepare a release candidate per platform: version bump, builds, smoke test, perf on the profile's lowest device, build size, analytics/IAP sandbox check, save migration test, store checklist, signing, changelog — then ask before tag, push or submit."
argument-hint: "<platforms> [--dry-run]"
---

# /release

Invoking `/release` is the GD's build request for the platforms named. `--dry-run`: no tag, push or upload, and no writes — step 2 reports the next version instead of setting it. Unsized: 2 attempts per dispatch. Risk flag is always set.

## Gate — all must pass, or the GD accepts the gap by name
| # | Step | Owner | Pass |
|---|---|---|---|
| 0 | Content | main session | Release content committed; every feature in it closed at CP4 |
| 1 | Open bugs | main session | No Critical/High unsettled in `.workflow/bugs.md` (missing file → say so; not a pass) |
| 2 | Version bump | main session | `bundleVersion` + build number / version code incremented |
| 3 | Build per platform | `build-release-engineer` | Release config, IL2CPP, artifact exists |
| 4 | Smoke test | `build-release-engineer` | Launch, core loop, purchase/ad screens open, quit/resume |
| 5 | Performance | `performance-qa-engineer` | Budget met on the profile's lowest device, real build |
| 6 | Build size | `build-release-engineer` | Within `CLAUDE.md` budget; store over-cellular limits |
| 7 | Analytics + IAP | `build-release-engineer` | Events seen in the vendor debug view; sandbox purchase + restore |
| 8 | Save migration | `qa-automation-engineer` | Previous release's save loads in this build's code |
| 9 | Store checklist | `build-release-engineer` | See below |
| 10 | Signing | `build-release-engineer` | Referenced keystore alias / profile exists; no secret in repo |
| 11 | Secrets | `security-reviewer` | `secret-and-supply-chain-scan` clear on the release diff |
| 12 | Changelog | main session | From `git log <last tag>..HEAD` (first release: all history), player-facing wording |

Steps 3–8 hold the Editor or the device: run them serially. 9, 10, 11 are read-only and run in parallel with anything. Code was reviewed per feature; the release diff gets the security scan (11), not a second `/review`.

## Store checklist
- **Android:** target API level current, AAB, permissions justified, Data safety form matches SDKs, content rating, 64-bit.
- **iOS:** privacy manifest + Nutrition Labels match SDKs, ATT prompt before tracking, export compliance, minimum iOS version.
- **Both:** app identity (bundle id, product and company name are not template defaults), age rating, COPPA/GDPR consent path when `CLAUDE.md` says so, ads labelled, loot-box odds disclosed where required.

## Finish — `AskUserQuestion`
Show the gate table with results. Options: tag + push (recommended when all pass; never in a dry run) / fix failures first / stop. Store upload or submission is always a separate, explicit GD request.
