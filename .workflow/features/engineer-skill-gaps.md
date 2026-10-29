# Engineer skill gaps

- Status: Closed
- CP: closed 2026-10-29
- Size: M · Risk flag: no — guidance docs only; they describe real-money IAP and save migration, so review is recommended (+ `security-reviewer` on skills 2 and 4)
- Profile: n/a — framework repo; `CLAUDE.md` is the per-project template
- Feature root: `.claude/skills/`

## Request (verbatim)
> tiếp tục

Context: continues the engineer-group audit of 2026-10-29. Its "not done" list named these missing skills: save versioning/migration, server-side IAP receipt validation + currency ledger, Firebase Unity SDK, ATT/UMP consent ordering, server-authoritative validation (netcode), UI safe area + localization, Core↔scene integration (gameplay), float determinism + Core testing without Unity (csharp).

## GD decisions
- 2026-10-29 Scope: all 8 skills in this round.
- 2026-10-29 Server-side code: vendor-neutral procedure in SKILL.md; one reference per vendor (Firebase Functions/Firestore, UGS Cloud Code/Economy/Cloud Save).
- 2026-10-29 Firebase Unity SDK skill: setup (EDM4U, `CheckAndFixDependenciesAsync`, config files) + Analytics, Remote Config, Crashlytics, Auth. Firestore/Functions live in the backend skills.
- 2026-10-29 Firebase config files (security-reviewer, Firebase docs fetched by the main session): client-safe when the API key is restricted to Firebase APIs; Gemini/billable-API keys and service-account files stay secret. `secret-and-supply-chain-scan` steps 3–4 updated; `core.md` unchanged (its vendor-documented rule already covers it).
- 2026-10-29 Gates: review yes, QA yes.
- 2026-10-29 CP4: closed; GD accepted gaps 1–4 below (no runtime run, Unverified vendor facts, post-review fixes security-checked only, listed limitations).
- 2026-10-29 BUG-0001: remove the optional Firebase-before-consent path (GD).
- 2026-10-29 Kept removals from the audit (review round 1 asked why): `zstring-zero-allocation-strings` off csharp-engineer's list — display-string building is Client work, Core builds no strings per tick; `unity:setup-multiplayer-services` off backend-engineer's list — it covers Sessions/Lobby/Relay (netcode), not Cloud Save/Economy.
- 2026-10-29 CP2 approved: 10 skills per the spec, with the architect's assumptions (IAP without subscriptions, no RTL, no fixed-point library named).

## Spec
Acceptance criteria by `technical-architect`, 2026-10-29. 8 gaps → 10 skills (6 and 8 split: different triggers, >120 lines combined). All `user-invocable: false`.

**1. `save-data-versioning-migration`** — backend-engineer, csharp-engineer. Refs: `version-envelope-and-chain.md`, `golden-save-fixtures.md`.
- Header with schema version + checksum; chain of sequential pure vN→vN+1 steps; a shipped step is never edited.
- A save newer than the build is refused, never overwritten. Atomic write (temp + swap); pre-migration backup kept.
- One golden fixture per shipped version, no player PII; it feeds `release` step 8. Agrees with memorypack step 11.
- DTOs + chain in `Game.Core.Save` (pure C#); file I/O and cloud sync in `Game.Client.*`.

**2. `iap-server-receipt-ledger`** — backend-engineer, sdk-platform-engineer. Refs: `google-play-developer-api.md`, `app-store-server-api.md`, `firebase-functions-firestore.md`, `ugs-cloud-code-economy.md`.
- Never credits from a client-sent product/amount or a local `CrossPlatformValidator` result.
- Idempotency key = store transaction id; grant + ledger entry in one transaction; client confirms only after server ack.
- Refund/void reverses the grant; verification failure fails closed; server credentials by secret-store id only.
- `Unverified:` line in each vendor reference for anything not checked against the source.

**3. `firebase-unity-sdk`** — sdk-platform-engineer. Refs: `setup-edm4u.md`, `analytics.md`, `remote-config.md`, `crashlytics.md`, `auth.md`.
- Every call gated on `CheckAndFixDependenciesAsync` → `DependencyStatus.Available`; all Firebase packages on one version.
- Remote Config in-build defaults; Analytics collection off until consent; Auth sends the ID token for server verification, never a uid in a payload.
- Config files handled per `secret-and-supply-chain-scan` (open question below).

**4. `consent-att-init-order`** — sdk-platform-engineer. Refs: `google-ump.md`, `ios-att-and-privacy-manifest.md`, `child-audience-flags.md`.
- Order consent → ATT → SDK init; no ad/analytics SDK starts before consent resolves; ATT requested only while app active.
- Audience unstated → `Needs-decision` (matches ad-mediation step 8); privacy-options entry point required; store policy via WebFetch.

**5. `server-authoritative-validation`** — netcode-engineer. Refs: `sender-identity-per-stack.md`, `rate-limits-and-rejection.md`.
- Identity/ownership never from payload; validate via `Game.Core.*` before any state change; per-connection rate limit with stated budget.
- Rejection answers with authoritative state, leaks nothing; untrusted reads use `*Safe` APIs; Output has `Rejection behaviour:`.

**6a. `mobile-safe-area`** — ui-engineer. Ref: `device-simulator-checks.md`.
- `Screen.safeArea` on one content root, backgrounds full-bleed; re-applied only on safe-area/orientation/resolution change; UI Toolkit via panel-space conversion; verified per target device in Device Simulator.

**6b. `unity-localization-text`** — ui-engineer. Refs: `string-tables-and-smart-strings.md`, `font-fallback-and-expansion.md`.
- Await `LocalizationSettings.InitializationOperation` before first read; no hard-coded player-facing strings; one fallback font per script with atlas memory cost; pseudo-locale expansion check; RTL stated as a limitation.

**7. `core-scene-integration`** — gameplay-engineer. Refs: `tick-and-interpolation.md`, `input-and-physics-into-core.md`.
- One named tick owner (default: a VContainer `IFixedTickable`, else one MonoBehaviour; multiplayer: the netcode stack); Core gets injected time, never `Time.deltaTime`.
- Views read Core state, never write it; interpolation between snapshots is render-only; input sampled into a per-tick command struct; physics results reach Core as plain data.

**8a. `core-determinism`** — csharp-engineer. Refs: `float-and-fixed-point.md`, `stable-hashing-and-ordering.md`, `replay-test.md`.
- Step 1 gate: is cross-machine agreement needed at all; float vs fixed-point → `technical-architect` (one system) or `cto` (library); no library named.
- Forbids persisting `string.GetHashCode` and hash-collection order deciding an outcome; replay test compares a per-tick state hash.

**8b. `core-tests-without-unity`** — csharp-engineer, qa-automation-engineer. Ref: `dotnet-test-mirror.md`.
- Core asmdef `noEngineReferences`; `Game.Core.Tests` in Edit Mode by default; dotnet mirror links the same sources with pinned language version, only when tech-stack.md or an ADR adopts it; a test passing in only one runner is not a pass.

**Cross-cutting**
- Both templates met (description ≤250, `Not for:`, `Docs:` pin, decision-ordered steps, every reference triggered and used, ≤120 lines, refs ≤250 lines). `/verify-layer` exits 0; agent bodies ≤25 lines.
- Bordering lines to change: `ad-mediation-monetization-platform` ledger `Routed to:` → `backend-engineer`; `unity-test-framework` step 2 + `Not for:` allow the dotnet mirror; `qa-automation-engineer` description adds dotnet test runs.
- Repoint `Not for:` in `memorypack-serialization`, `firebase-app-distribution`, `netcode-for-gameobjects`, `unity-transport`, `anti-cheat-strategy` to the new names.

**Assumptions:** IAP covers consumables + non-consumables (subscriptions out); RTL out; no fixed-point library named; text-expansion figures `Unverified:` unless sourced.

**Open question (security):** is the API key in `google-services.json` / `GoogleService-Info.plist` client-safe? → `security-reviewer` before skill 3 is written; until then skill 3 treats the files as secret (`core.md`).

## Log
| # | Agent | Changed | Verified | Attempts | Limitations / Needs GD |
|---|---|---|---|---|---|
| 1 | security-reviewer | none — verdict: Firebase client config conditionally client-safe | Firebase docs fetched by main session | 1/2 | Main session updated `secret-and-supply-chain-scan` steps 3–4 |
| 2 | general-purpose (author) | `core-determinism/` (4 files), `core-tests-without-unity/` (2) | own files verify-layer 0/0 | 1/3 | Unverified: Mono/IL2CPP hash randomization, IL2CPP float flags, csc.rsp on Unity 6 |
| 3 | general-purpose (author) | `server-authoritative-validation/` (3), `core-scene-integration/` (3) | own files verify-layer clean | 1/3 | Unverified: NGO server-side InvokePermission enforcement, NfE owner check, MagicOnion force-disconnect |
| 4 | general-purpose (author) | `mobile-safe-area/` (2), `unity-localization-text/` (3) | own files verify-layer clean | 1/3 | Localization pinned 1.5.13; Unity 6.7 built-in runtime gated in step 1 |
| 5 | general-purpose (author) | `firebase-unity-sdk/` (6), `consent-att-init-order/` (4) | own files verify-layer 0/0 | 1/3 | EDM4U archived 2026-10-26 → Unity EDM package; several member names Unverified |
| 6 | general-purpose (author) | `save-data-versioning-migration/` (3), `iap-server-receipt-ledger/` (5) | verify-layer exit 0 | 1/3 | Needs GD (routed in skill): UGS custom grants cannot be single-transaction → `cto`; Apple refund webhook on UGS needs an outside receiver |
| 7 | main session | 9 agent on-demand lists; bordering lines in ad-mediation, unity-test-framework, memorypack, firebase-app-distribution, NGO, unity-transport, anti-cheat-strategy, qa-automation description | full `/verify-layer` OK (2 pre-existing warnings); secret-shape grep over skills: no hits outside the scanner's own pattern list | 1/3 | — |
| 8 | review round 1 | security-reviewer: Findings (4 High, 4 Med, 4 Low); code-reviewer A (save, IAP, Firebase, consent, validation): Request changes (1 High, 9 Med, 7 Low); code-reviewer B (rest + bordering): Approve (15 Low) | read-only | 1 | Main session fixed SEC-1 (scanner allowlist), B-13/14/15, backend-engineer description; rest sent to authors |
| 9 | 5 authors (round 1 fixes) | all round-1 items in their folders | full `/verify-layer` exit 0 (2 pre-existing warnings) | 2/3 | Apple host kept `api.storekit.apple.com` (author confirmed against Apple docs; reviewer's claim was outdated). New Unverified: productsv2 vs v1, REFUND_PRORATED on one-time, Economy endpoint paths, Firebase reading IABTCF itself, Unity SDK honouring native Crashlytics off keys |
| 10 | review round 2 | security: 12/12 resolved, R2-1 Medium (UGS client redeem bypasses void tombstone), R2-2 Low; code-reviewer A: 17/17 resolved, N1–N3 Medium (Play partial-refund flag, Firebase static before bootstrap in consent order, UGS reversal double-apply), 2 Low | read-only | 2 | Main session decided R2-1: real-money redeem on UGS only via Cloud Code; sent to IAP and SDK authors, attempt 3/3 |
| 11 | review round 3 | security: Clear (R2-1, R2-2 resolved; 1 Low latent); code-reviewer A: N1–N3, R2-1, Lows resolved; R3-1 Medium (privacy-options withdrawal skipped ad signals) | read-only | 3 | Authors at 3/3; main session applied the reviewer's exact one-clause fix (consent SKILL:26, google-ump.md:73), confirmed by reading; `/verify-layer` OK. Review closed: code-reviewer B Approve, A resolved, security Clear |
| 12 | QA executor (general-purpose) | `.workflow/evidence/engineer-skill-gaps/attempt-1/qa-report.md` | verify-layer exit 0 (2 known warnings); line counts in limits; 59/60 criteria met; 14/14 vendor facts match (2 still Unverified, already marked); 12/13 consistency pairs | 1/3 | BUG-0001..0003 filed; OBS-1 (Apple refund transactionId vs restored/Family-Shared) → Unverified line |
| 13 | /fix BUG-0001..0005 + OBS-1 | consent (0001, 0002, 0005), mobile-safe-area + localization ref (0003), IAP Apple key → originalTransactionId (OBS-1, restore double-grant), Family-Shared rule (0004) | security re-check Clear on all; verify-layer exit 0 | fix 2/2 | OBS-1 turned out a real defect (restore double-grant), fixed |
| 14 | qa-lead (sign-off) | none | read the fixed lines; executor evidence accepted | 1/1 | Not signed off pending GD acceptance of gaps: no runtime/backend run; vendor facts still Unverified; no fresh review round on fix edits (security re-check covered them); Known limitations. BUG-0001..0005 confirmed closable → Closed |

## Bugs
| ID | Title | Severity | Status |
|---|---|---|---|
| BUG-0001 | Consent skill allows Firebase bootstrap before consent without GD acceptance | Medium | Closed |
| BUG-0002 | google-ump.md caveat omits Firebase re-apply on privacy-options close | Medium | Closed |
| BUG-0003 | mobile-safe-area defaults gate after per-device verify | Low | Closed |
| BUG-0004 | Apple Family-Shared refund fallback can reverse or tombstone the purchaser's grant | High | Closed |
| BUG-0005 | Consent caveat claims Crashlytics stops in-session on withdrawal | Medium | Closed |

## Known limitations
- (CP4, GD-accepted) No skill was run on a Unity Editor, build, device, live backend or store sandbox; closing this needs a real project (backlog pilot).
- (CP4, GD-accepted) Vendor facts still Unverified, each marked `Unverified:` in its reference: voidedReason/voidedSource enums, NGO InvokePermission enforcement side, Apple library verification of signedTransactionInfo, ConsentType casing, `com.unity.external-dependency-manager` id, native Crashlytics/Analytics off keys under the Unity SDK.
- (CP4, GD-accepted) Fixes made after review round 3 (R3-1, BUG-0001..0005, OBS-1) were security re-checked and QA-read, not code-reviewed again.
- Crashlytics withdrawal takes effect next launch (Analytics and ad networks stop in-session).
- Whether an Apple Family-Shared transaction carries the purchaser's originalTransactionId is Unverified; the ledger rule holds either way.
- UGS refund race (security latent, Low): redeem and void can interleave so a grant stands without a reversal; the orphan alert still fires for manual reconciliation. Fix trigger: real refund volume on UGS (one conditional Cloud Save write, or re-check orphans after mapping).
- UGS custom reversal is non-atomic: a stale `pending` decrement is reconciled by hand, never auto-retried.
- R3-1 fix written by the main session from the reviewer's text and confirmed by reading, not by a fresh review round.
- Firebase App Check client wiring has no skill: the IAP Functions sample enforces App Check, so a Unity client needs App Check integration written per vendor docs.
- Crashlytics/Analytics first-launch opt-in depends on native off keys whose effect under the Unity SDK is Unverified; skills route the unconfirmed case to `Needs-decision`.
- IAP skill excludes subscriptions (renewal, grace period, RTDN) — GD-accepted at CP2.
- Localization skill excludes RTL scripts — GD-accepted at CP2.
- Skills are written against vendor docs; no Unity project or backend runs them in this round.
