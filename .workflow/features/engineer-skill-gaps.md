# Engineer skill gaps

- State: records.py feature show engineer-skill-gaps

## Request (verbatim)
> tiếp tục

Context: continues the engineer-group audit of 2026-10-29. Its "not done" list named these missing skills: save versioning/migration, server-side IAP receipt validation + currency ledger, Firebase Unity SDK, ATT/UMP consent ordering, server-authoritative validation (netcode), UI safe area + localization, Core↔scene integration (gameplay), float determinism + Core testing without Unity (csharp).

## GD decisions

- Rows: records.py csv render decisions --feature engineer-skill-gaps

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

- Rows: records.py csv render log --feature engineer-skill-gaps

## Bugs

- Bugs: bugs.py list --feature engineer-skill-gaps

## Known limitations

- Rows: records.py csv render limitations --feature engineer-skill-gaps
