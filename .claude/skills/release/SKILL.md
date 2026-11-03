---
name: release
description: "Release candidate per platform: gate table, store checklist, signing. Use when preparing a release."
argument-hint: "<platforms> [--dry-run]"
---

# /release

- **Invocation:** invoking `/release` is the GD's build request for the platforms named.
- **`--dry-run`:** no tag, push or upload, and no writes — step 2 reports the next version instead of setting it, and step 4's bug status moves are reported, not written.
- **Dry-run brief:** step 4's brief states each deferred bug's repro steps in plain words, with no `Verify:` line; the run reports that outcome, not a `Repro:` line, and the hook charges nothing.
- **Attempts:** unsized: 2 attempts per dispatch.
- **Risk flag:** risk flag is always set.

## Gate — all must pass, or the GD accepts the gap by name
| # | Step | Owner | Pass |
|---|---|---|---|
| 0 | Content | main session | Release content committed; every feature in it closed at CP4 |
| 0b | Unchecked work | main session | Every feature in `<last tag>..HEAD` whose file says "not reviewed" or "not QA'd", every `Accepted` High or Highest bug (`bugs.py list --status Accepted --priority High --priority Highest`, plus `.workflow/DEBT.md` and each feature root's `DEBT.md`: purge can remove an old one from the DB), every commit outside a closed feature (S work, no-feature `/fix`) — each listed as a named gap |
| 1 | Open bugs | main session | No High or Highest unsettled, `Backlog` included (`bugs.py list --open --priority High --priority Highest`), except a `Resolved` bug noted `awaits device verification` (`/fix` step 6), left for step 4 — re-checked after step 4 |
| 2 | Version bump | main session | `bundleVersion` + build number / version code incremented |
| 3 | Build per platform | `build-release-engineer` | Release config, IL2CPP, artifact exists |
| 4 | Smoke test | `build-release-engineer` | Launch, core loop, purchase/ad screens open, quit/resume; the brief carries `Verify: BUG-####` per bug row 1 deferred (dispatch → `Review`); its `Repro: … gone` → `Complete`, `reproduces` → `Reopen`, no line → `Resolved` |
| 5 | Performance | `performance-qa-engineer` | Budget met on the profile's lowest device, real build |
| 6 | Build size | `build-release-engineer` | Within `CLAUDE.md` budget; store over-cellular limits |
| 7 | Analytics + IAP | `build-release-engineer` | Events seen in the vendor debug view; sandbox purchase + restore |
| 8 | Save migration | `qa-automation-engineer` | Previous release's save loads in this build's code |
| 9 | Store checklist | `build-release-engineer` | See below |
| 10 | Signing | `build-release-engineer` | Referenced keystore alias / profile exists; no secret in repo |
| 11 | Secrets | `security-reviewer` | `secret-and-supply-chain-scan` clear on the release diff |
| 12 | Changelog | main session | From `git log <last tag>..HEAD` (first release: all history), player-facing wording |

- **Serial steps:** steps 3–8 hold the Editor or the device: run them serially.
- **Parallel steps:** 9, 10, 11 are read-only and run in parallel with anything.
- **Review status:** review status comes from each feature file (row 0b), never assumed.
- **Release diff:** the release diff gets the security scan (11, brief `Target: <last tag>..HEAD`), not a second `/review`.
- **Crash bugs:** a `Resolved` crash bug awaiting a device build is verified by step 4's device run.
- **Bug queries:** rows 0b and 1, per skill `bugs`. No `.workflow/bugs.jsonl` → say so; not a pass. Python absent or a CLI error → not a pass.

## Store checklist
- **Android:** target API level current, AAB, permissions justified, Data safety form matches SDKs, content rating, 64-bit.
- **iOS:** privacy manifest + Nutrition Labels match SDKs, ATT prompt before tracking, export compliance, minimum iOS version.
- **Both:**
  - **Identity:** app identity (bundle id, product and company name are not template defaults).
  - **Age rating:** age rating.
  - **Consent:** COPPA/GDPR consent path when `CLAUDE.md` says so.
  - **Ads:** ads labelled.
  - **Loot boxes:** loot-box odds disclosed where required.

## Finish — `AskUserQuestion`
- **Tag, push, submit:** none of them runs before this `AskUserQuestion`.
- **Show:** the gate table with results.
- **Journal:** row 4 moved a status → add "journal uncommitted": `.workflow/bugs.jsonl` waits for the GD's commit order, and a tag omits those moves until then.
- **Options:** tag + push (recommended only when every row passes or the GD accepted each gap by name in this run; never in a dry run) / fix failures first / stop.
- **Fix failures first:** each failed row goes to its route (`/fix`, `/review`, the owning agent), then re-run only the failed rows.
  - **Round count:** +1 `release` round, cap 2, recorded as `- Release rounds: n/2` in `.workflow/release-<version>.md`, then the stop rule.
- **Release file:** `.workflow/release-<version>.md` is the gate table with results, written at every Finish; not in a dry run.
- **Store upload:** store upload or submission is always a separate, explicit GD request.
