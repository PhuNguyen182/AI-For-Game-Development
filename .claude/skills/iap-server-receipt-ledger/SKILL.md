---
name: iap-server-receipt-ledger
description: "Server IAP grants: Play purchases.products, App Store transactions, REFUND, ledger. Use when crediting a purchase."
user-invocable: false
---

# IAP Server Receipt Ledger

- **Not for:** the client purchase flow and Unity IAP wiring (`unity:implement-in-app-purchases`).
- **Not for:** whether the ledger is managed or custom (`ad-mediation-monetization-platform`).
- **Not for:** backend vendor choice (`backend-build-vs-buy`).
- **Not for:** fraud posture beyond receipt checks (`anti-cheat-strategy`).
- **Not for:** a leaked store key (`secret-exposure-response`).
- **Not for:** subscriptions: renewals, grace periods, subscription notifications; this skill covers consumables and non-consumables.
- **Docs:** Google Play Developer API v3 https://developers.google.com/android-publisher/api-ref/rest/v3 · App Store Server API https://developer.apple.com/documentation/appstoreserverapi
  - **Deprecated:** `verifyReceipt` and App Store Server Notifications v1; build on signed transactions and v2 notifications only.
- **Rules:** `core.md` Security and `csharp.md` Boundaries.

## References
- **[google-play-developer-api.md](references/google-play-developer-api.md):** Verifying an Android purchase token, consuming or acknowledging it, or reversing a Play refund or chargeback.
- **[app-store-server-api.md](references/app-store-server-api.md):** Verifying an iOS signed transaction or transaction id, or handling a `REFUND` / `REFUND_REVERSED` notification.
- **[firebase-functions-firestore.md](references/firebase-functions-firestore.md):** The backend in `docs/tech-stack.md` is Firebase.
- **[ugs-cloud-code-economy.md](references/ugs-cloud-code-economy.md):** The backend is Unity Gaming Services (Economy real-money purchases or Cloud Code).

## Steps
1. **Gate on decisions already made:** backend in `docs/tech-stack.md` or its ADR, ledger authority per `ad-mediation-monetization-platform` step 5.
   - **Absent:** `Blocked` (backend-engineer Inputs).
   - **Subscription product in the request:** `Needs-decision` to the GD; out of this skill's scope.
2. **Fix the contract: the client sends store proof, nothing else:**
   - **Proof:** the Android purchase token (product id only as a lookup hint), the iOS signed transaction or transaction id, plus its authenticated session.
   - **Grant source:** product, quantity and grant come from the store response and the server catalog.
   - **Never credit from:** a client-sent product, amount or price, or a local `CrossPlatformValidator` result (a client signal).
   - **Player:** from the verified auth token, never the payload.
3. **Verify with the store, failing closed:** per the platform reference, which lists the Play state and product-id checks and the Apple signature-chain and payload checks.
   - **Apple JWS older than the stated bound:** refresh through Get Transaction Info and grant from that verified response.
   - **Consumption state:** not judged here (step 5).
   - **Pending:** no grant, answer `pending`.
   - **Signature invalid, check failed, store unreachable or any exception:** no grant, no consume/acknowledge, answer retryable or final; never catch-and-grant.
4. **Key the ledger on the store transaction id:** ledger id `<store>:<id>`.
   - **Id:** Play `purchaseToken` (never `orderId`, absent on promo-code purchases); Apple `originalTransactionId` (a restore keeps it).
   - **Done when:** a replayed proof maps to the same ledger entry.
5. **Commit grant and ledger entry in one transaction:** per the backend reference, checks in this order.
   - **Entry exists and `granted` for this player:** return its stored grant (replay = same answer, no second credit).
   - **Entry exists for another player:** reject with the same generic reason as an invalid proof, and record a flag (ledger id, both players) outside the transaction.
   - **Entry is a void tombstone (step 8):** reject.
   - **No entry and Play reports the token already consumed:** reject.
   - **Otherwise:** create the entry, storing its ownership (Apple `inAppOwnershipType`; Play `PURCHASED`), and credit.
   - **UGS:** the Economy redeem call made from the Cloud Code module is the transaction; a custom grant across Cloud Save and Economy cannot be atomic → `Needs-decision`, `Next: cto`.
6. **Finish with the store after the commit, never inside it:** the entry records `finished: false` until the call succeeds.
   - **Store call:** Play consume (consumable) or acknowledge (non-consumable) from the server; unacknowledged purchases auto-refund after three days; Apple nothing server-side.
   - **Retry:** the step 8 scheduled poll is the reconciler that retries every `granted` entry not yet finished; the ledger already blocks a second grant.
7. **Client confirms only after the server's ack:** Unity IAP `ConfirmPurchase` only on `granted` or `already granted`.
   - **Retryable error:** the order stays pending and the store re-delivers it on next launch.
   - **Final rejection:** no confirm; whether to refund explicitly (Play `orders.refund`) is a money decision → `Needs-decision` to the GD.
8. **Reverse grants per void event:** verify the notification's signature or push identity first, failing closed.
   - **Sources:** per platform reference: Play scheduled Voided Purchases poll (plus RTDN when reversal must beat it); Apple v2 `REFUND`, `REFUND_REVERSED` reinstates.
   - **Event entry:** one per event on the grant key's id, so partial refunds each land once.
   - **Event keys:** `<store>:<id>:void:<event id>` or `<store>:<id>:reinstate:<event id>`; event ids per platform reference.
   - **Original entry:** keeps a running `reversedQuantity`, never deleted.
   - **`PURCHASED` refund or void with no grant entry:** store it as an orphan, alert, and write a tombstone under `<store>:<id>` so a later grant of that proof fails.
   - **Family exception:** a `FAMILY_SHARED` event or Apple `REVOKE` reverses only a `FAMILY_SHARED` entry of the identified player, never a `PURCHASED` one; none → alert only, no tombstone.
   - **Consumable already spent:** negative balance, debt or flag only → `Needs-decision` to the GD.
   - **Reversal write:** per the backend reference.
   - **UGS:** a reversal's decrement is not atomic with its event entry; stale `pending` events alert and are reconciled by hand, never auto-retried; report it in `Limitations`.
9. **Credentials by secret-store id only:** Play service account, App Store Connect API key.
   - **Name:** the secret id in the backend's secret store, never a value, in code, repo, client or logs; list ids under `Config required:`; run `secret-and-supply-chain-scan` on the diff.
10. **Verify by running, never by reading:** risk flag set (`routing.md`).
    - **Runs:** sandbox purchase per store, the same proof replayed twice (one grant), a tampered JWS or wrong-package token rejected, a test refund reversed.
    - **Not run:** `Verified: not run` and a `Known limitations` line.
    - **Release candidate:** `release` step 7 owns its sandbox check.

## Never
- **Logging proofs:** log a full purchase token, JWS or receipt — each is a replayable purchase proof; log the ledger id or a hash.
- **Ungated restore:** grant on a client "restore" without the same server verification — restore re-delivers proofs; the ledger key makes it a no-op.
- **Sandbox in production:** credit a sandbox or license-test purchase in the production ledger — Apple `environment` `Sandbox`, Play `purchaseType` 0.

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
```

## Example
- **"Validate with `CrossPlatformValidator` on device and send `{productId, gems}` to the function":** declined.
  - **Why:** both values are forgeable on a modified client.
  - **Did instead:** the function takes the purchase token and reads product and quantity from `purchases.products.get`.
