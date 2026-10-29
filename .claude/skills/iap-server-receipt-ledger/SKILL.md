---
name: iap-server-receipt-ledger
description: "Server-side IAP grants: Play purchases.products get/consume/acknowledge, voided purchases, App Store signed transactions, REFUND notifications, ledger keyed by store transaction id, Firestore or UGS Economy. Use when crediting a real-money purchase."
user-invocable: false
---

# IAP Server Receipt Ledger

Not for: the client purchase flow and Unity IAP wiring (`unity:implement-in-app-purchases`), whether the ledger is managed or custom (`ad-mediation-monetization-platform`), backend vendor choice (`backend-build-vs-buy`), fraud posture beyond receipt checks (`anti-cheat-strategy`), a leaked store key (`secret-exposure-response`). Scope: consumables and non-consumables; subscriptions (renewals, grace periods, subscription notifications) are out.
Docs: Google Play Developer API v3 https://developers.google.com/android-publisher/api-ref/rest/v3 · App Store Server API https://developer.apple.com/documentation/appstoreserverapi — `verifyReceipt` and App Store Server Notifications v1 are deprecated: build on signed transactions and v2 notifications only.
Rules: `core.md` Security (authoritative outcomes never trust a client value; fail closed around signature, token and payment validation; credentials by secret-store id); `csharp.md` Boundaries (validate SDK callbacks and network messages).

| Reference | Read when |
|---|---|
| [google-play-developer-api.md](references/google-play-developer-api.md) | Verifying an Android purchase token, consuming or acknowledging it, or reversing a Play refund or chargeback |
| [app-store-server-api.md](references/app-store-server-api.md) | Verifying an iOS signed transaction or transaction id, or handling a `REFUND` / `REFUND_REVERSED` notification |
| [firebase-functions-firestore.md](references/firebase-functions-firestore.md) | The backend in `docs/tech-stack.md` is Firebase |
| [ugs-cloud-code-economy.md](references/ugs-cloud-code-economy.md) | The backend is Unity Gaming Services (Economy real-money purchases or Cloud Code) |

## Steps
1. **Gate on decisions already made** — backend in `docs/tech-stack.md` or its ADR, ledger authority per `ad-mediation-monetization-platform` step 5. Absent → `Blocked` (backend-engineer Inputs). A subscription product in the request → `Needs-decision` to the GD: out of this skill's scope.
2. **Fix the contract: the client sends store proof, nothing else** — Android purchase token (product id only as a lookup hint), iOS signed transaction or transaction id, plus its authenticated session. Product, quantity and grant come from the store response and the server catalog. Never credit from a client-sent product, amount or price, or from a local `CrossPlatformValidator` result (a client signal; Apple local validation is a no-op on StoreKit 2). The player comes from the verified auth token, never the payload.
3. **Verify with the store, failing closed**, per the platform reference: Play `purchases.products.get` state checks and a response product id equal to the catalog-checked hint; Apple JWS signature chain plus bundle id, environment, product type and revocation fields, refreshed through Get Transaction Info when the JWS is older than the stated bound. Consumption state is not judged here (step 5). Pending → no grant, answer `pending`. Signature invalid, check failed, store unreachable or any exception → no grant, no consume/acknowledge, answer retryable or final; never catch-and-grant.
4. **Key the ledger on the store transaction id** — Play `purchaseToken` (globally unique; `orderId` is absent on promo-code purchases, so never the key), Apple `originalTransactionId` (equals `transactionId` on a purchase; a restore gets a new `transactionId` but keeps the original). Ledger id `<store>:<id>`. Done when a replayed proof maps to the same ledger entry.
5. **Commit grant and ledger entry in one transaction**, per the backend reference, checks in this order: entry exists and `granted` for this player → return its stored grant (replay = same answer, no second credit); entry exists for another player → reject with the same generic reason as an invalid proof, and record a flag (ledger id, both players) outside the transaction; entry is a void tombstone (step 8) → reject; no entry and Play reports the token already consumed → reject; else create the entry, storing its ownership (Apple `inAppOwnershipType`; Play `PURCHASED`), and credit. On UGS the Economy redeem call, made from the Cloud Code module (client-side redeem is not supported), is the transaction; a custom grant across Cloud Save and Economy cannot be atomic → `Needs-decision`, `Next: cto`.
6. **Finish with the store after the commit, never inside it** — Play: consume (consumable) or acknowledge (non-consumable) from the server; unacknowledged purchases auto-refund after three days. Apple: nothing server-side. The entry records `finished: false` until the call succeeds; the step 8 scheduled poll is the reconciler that retries every `granted` entry not yet finished. The ledger already blocks a second grant.
7. **Client confirms only after the server's ack** — Unity IAP `ConfirmPurchase` only on `granted` or `already granted`; on a retryable error the order stays pending and the store re-delivers it on next launch. Final rejection → no confirm; whether to refund explicitly (Play `orders.refund`) is a money decision → `Needs-decision` to the GD.
8. **Reverse grants per void event** — Play: a scheduled Voided Purchases API poll inside its 30-day window with `includeQuantityBasedPartialRefund=true`, plus Real-time developer notifications when reversal must beat the poll interval; Apple: v2 `REFUND`, and `REFUND_REVERSED` reinstates. Verify the notification's signature or push identity first, failing closed. Match on the same id as the grant key (Play `purchaseToken`; Apple `originalTransactionId` from the verified `data.signedTransactionInfo`). Each event is its own entry, `<store>:<id>:void:<event id>` or `<store>:<id>:reinstate:<event id>` (event ids per platform reference), so partial refunds of a multi-quantity purchase each land once; the original entry keeps a running `reversedQuantity`, never deleted. A `PURCHASED` refund or void with no grant entry → store it as an orphan, alert, and write a tombstone under `<store>:<id>` so a later grant of that proof fails. Family exception: an event on a `FAMILY_SHARED` transaction, or an Apple `REVOKE`, reverses only an entry stored as `FAMILY_SHARED` whose player the event identifies, never a `PURCHASED` entry; with no such entry it alerts only and never writes a tombstone. A consumable already spent: negative balance, debt or flag only → `Needs-decision` to the GD.
9. **Credentials by secret-store id only** — Play service account, App Store Connect API key. Name the secret id in the backend's secret store, never a value, in code, repo, client or logs; list ids under `Config required:`. Run `secret-and-supply-chain-scan` on the diff.
10. **Verify by running, never by reading** — risk flag set (`routing.md`): sandbox purchase per store, the same proof replayed twice (one grant), a tampered JWS or wrong-package token rejected, a test refund reversed. Not run → `Verified: not run` and a `Known limitations` line; `release` step 7 owns the release-candidate sandbox check.

## Never
- Log a full purchase token, JWS or receipt — each is a replayable purchase proof; log the ledger id or a hash.
- Grant on a client "restore" without the same server verification — restore re-delivers proofs; the ledger key makes it a no-op.
- Credit a sandbox or license-test purchase in the production ledger — Apple `environment` `Sandbox`, Play `purchaseType` 0.

## Output
```
## IAP Receipt Ledger — <project / backend>
- Products: <id — consumable | non-consumable>, catalog source <...>
- Verification: Play <API> / Apple <JWS verify | Get Transaction Info>; fail-closed paths <...>
- Idempotency key: <store>:<purchaseToken | originalTransactionId> — ledger <collection / key>
- Atomic grant: <Firestore transaction | Economy redeem | Needs-decision>
- Store finish: server consume/acknowledge <...>; client confirm after ack
- Store finish retry: <scheduled job, cadence, `finished: false` query>
- Refund path: <voided poll cadence | RTDN | App Store v2 REFUND>; event keys <...>; orphan alert <where> — spent-consumable policy <GD decision>
- Config required: <secret-store ids, never values>
- Verified: <runs with result — or "not run">
- Known limitations: subscriptions out; UGS: a reversal's decrement is not atomic with its event entry — stale `pending` events alert and are reconciled by hand, never auto-retried; <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "Validate with `CrossPlatformValidator` on device and send `{productId, gems}` to the function" → declined: both values are forgeable on a modified client and Apple local validation is a no-op on StoreKit 2; the function takes the purchase token and reads product and quantity from `purchases.products.get`.
