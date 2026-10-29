# Bugs

Next ID: BUG-0006

| ID | Title | Severity | Status | Feature | Owner | Regression test |
|---|---|---|---|---|---|---|
| BUG-0001 | Consent skill allows Firebase bootstrap before consent without GD acceptance | Medium | Closed | engineer-skill-gaps | consent-att-init-order (sdk author) | Written repro (docs, no seam) |
| BUG-0002 | google-ump.md caveat omits Firebase re-apply on privacy-options close | Medium | Closed | engineer-skill-gaps | consent-att-init-order (main session R3-1 text) | Written repro (docs, no seam) |
| BUG-0003 | mobile-safe-area defaults gate placed after the per-device verify step | Low | Closed | engineer-skill-gaps | mobile-safe-area (ui author) | Written repro (docs, no seam) |
| BUG-0004 | Apple Family-Shared refund fallback can reverse or tombstone the purchaser's grant | High | Closed | engineer-skill-gaps | iap-server-receipt-ledger (backend author) | Written repro (docs, no seam) |
| BUG-0005 | Consent caveat claims Crashlytics stops in-session on withdrawal | Medium | Closed | engineer-skill-gaps | consent-att-init-order (sdk author) | Written repro (docs, no seam) |

## BUG-0001 — Consent skill allows Firebase bootstrap before consent without GD acceptance
- Repro: read `.claude/skills/consent-att-init-order/SKILL.md:21`, step 3 clause "Firebase bootstrap may move before (b) only when … off keys ship".
- Expected: spec 4 "no ad/analytics SDK starts before consent resolves" · Actual: an optional path lets Firebase Installations and Remote Config/Auth traffic precede consent; no GD acceptance recorded.
- Evidence: `.workflow/evidence/engineer-skill-gaps/attempt-1/qa-report.md` DEF-1.
- History: 2026-10-29 Open — QA executor. 2026-10-29 Fixed — sdk author (consent SKILL:21); security re-check: nothing starts before consent. 2026-10-29 Closed — qa-lead re-read the fixed lines (sign-off read-through).

## BUG-0002 — google-ump.md caveat omits Firebase re-apply on privacy-options close
- Repro: compare `consent-att-init-order/SKILL.md:26` (re-apply 3(d) Firebase consent and 3(e) ad signals on close) with `references/google-ump.md:73` (Firebase re-applied only "every launch").
- Expected: both re-applied on close · Actual: a reader following the reference leaves Firebase collecting until the next launch after a withdrawal.
- Evidence: qa-report.md DEF-2.
- Root cause: R3-1 fix text written by the main session named only `ApplyAdConsentSignals` for on-close.
- History: 2026-10-29 Open — QA executor. 2026-10-29 Fixed — sdk author (google-ump.md:70-89); security re-check: analytics stops in-session (Crashlytics → BUG-0005). 2026-10-29 Closed — qa-lead re-read the fixed lines (sign-off read-through).

## BUG-0003 — mobile-safe-area defaults gate placed after the per-device verify step
- Repro: read `mobile-safe-area/SKILL.md:25-26`: step 10 "target devices unstated → defaults" follows step 9 verification per target device.
- Expected: decision-ordered steps (skill template) · Actual: the gate that sets the device list comes after its use.
- Evidence: qa-report.md DEF-3.
- History: 2026-10-29 Open — QA executor. 2026-10-29 Fixed — ui author (mobile-safe-area SKILL:25-26; localization SKILL:27 ref). 2026-10-29 Closed — qa-lead re-read the fixed lines (sign-off read-through).

## BUG-0004 — Apple Family-Shared refund fallback can reverse or tombstone the purchaser's grant
- Repro: read `iap-server-receipt-ledger/references/app-store-server-api.md:65` and `SKILL.md:28`: FAMILY_SHARED refund/REVOKE with no entry → match by appAccountToken+productId; void with no entry → orphan + tombstone.
- Expected: a family REVOKE never reverses or blocks the purchaser's PURCHASED grant · Actual: fallback can land on the purchaser's entry; a tombstone can block their later grant.
- Evidence: security re-check after QA fixes, F-1.
- History: 2026-10-29 Open — security-reviewer. 2026-10-29 Fixed — backend author (ownership per entry; family events never touch PURCHASED; tombstones only from PURCHASED); security re-check Clear. 2026-10-29 Closed — qa-lead re-read the fixed lines (sign-off read-through).

## BUG-0005 — Consent caveat claims Crashlytics stops in-session on withdrawal
- Repro: `consent-att-init-order/references/google-ump.md:89` says withdrawal stops Firebase collection in the same session; `firebase-unity-sdk/references/crashlytics.md:29` says the Crashlytics flag takes effect next launch.
- Expected: caveat limited to Analytics, Crashlytics gap stated · Actual: overclaims.
- Evidence: security re-check, F-2.
- History: 2026-10-29 Open — security-reviewer. 2026-10-29 Fixed — sdk author (same-session stop limited to Analytics + ads; Crashlytics next launch in Known limitations); security re-check Clear. 2026-10-29 Closed — qa-lead re-read the fixed lines (sign-off read-through).
