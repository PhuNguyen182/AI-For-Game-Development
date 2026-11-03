# Firebase: Cloud Functions (2nd gen) + Firestore Ledger

Sources (under https://firebase.google.com/docs/): [a] `functions/callable`, [b] `app-check/cloud-functions`, [c] `functions/config-env`, [d] `firestore/manage-data/transactions`, [e] `firestore/security/get-started`, [f] `functions/pubsub-events`, [g] `functions/schedule-functions`. Elsewhere: [h] Node Firestore `Transaction` https://docs.cloud.google.com/nodejs/docs/reference/firestore/latest/firestore/transaction, [i] SDK source https://github.com/firebase/firebase-functions/blob/master/src/common/providers/https.ts, [j] a reported `create()` failure https://github.com/firebase/firebase-functions-test/issues/214, [k] `gaxios` source https://github.com/googleapis/gaxios/blob/main/src/common.ts.

## Endpoint

| Subject | Fact that decides |
|---|---|
| `onCall` from `firebase-functions/https` | Callable trigger: deserializes the body and validates Firebase Auth (and App Check) tokens the client SDK attaches automatically [a] |
| `request.auth.uid` | The player. `request.auth` absent → `throw new HttpsError("unauthenticated", …)`; never read a uid from `request.data` |
| `enforceAppCheck: true` | Rejects requests with missing or invalid App Check tokens [b]. Needs App Check on the client, which no skill in this layer covers: a `Known limitations` line until one does |
| `consumeAppCheckToken: true` | Replay protection, beta, Node only; one extra network round trip per call [b] |
| `HttpsError(code, message, details)` | The only error shape the client sees as-is; any other thrown error reaches the client as `INTERNAL` [a] and is logged whole as `Unhandled error` [i] |
| Errors in logs | A Firestore message can carry the doc path, so the token (`ALREADY_EXISTS: Document already exists: projects/…/documents/…` [j]); a `gaxios` error keeps its request URL and redacts a `token` query parameter, not a path segment [k]. Never let one reach `onCall` or a log: catch it, log only the fields under **Any other error** below, throw an `HttpsError` |
| Unity client | `FirebaseFunctions` → `GetHttpsCallable("name").CallAsync(data)`; failures surface as `FunctionsException` [a] |
| Secrets | `defineSecret("NAME")` from `firebase-functions/params`, bound per function through the `secrets` option, `.value()` read only inside the handler at runtime [c] |
| `functions.config()` | Deprecated since `firebase-functions` 6.0.0; new deploys using it fail after March 2027 [c] |
| Security rules | Server client libraries bypass all Firestore Security Rules [e]: rules must deny client reads and writes on the ledger, its event entries and the flag records, which hold the raw id, and client writes to every wallet/inventory field the function writes |

## Ledger transaction

| Subject | Fact that decides |
|---|---|
| `db.runTransaction(fn)` | Reads before writes; reruns `fn` on concurrent edits of documents it read; writes nothing on failure [d] |
| Side effects | Do not modify application state inside the transaction function [d]: no store API call, consume or acknowledge in `fn` — it may run more than once |
| `tx.get(ref)` | Server SDK read holding a pessimistic lock on the document [h] |
| `tx.create(ref, data)` | Fails the transaction if the document already exists [h] — the idempotency guard on `<store>:<id>` |
| Limits | Lock deadline 20 s, total 270 s, 60 s idle timeout, 10 MiB request [d] |

- **Sample:** [redeemPurchase.js](../scripts/redeemPurchase.js) — shape only; `verifyWithStore`, `finishWithStore`, `flagConflict` and `CATALOG` are project code.
  - **Adapt into:** the Cloud Functions source (`functions/index.js`).
  - **Secret:** `defineSecret("APP_STORE_SERVER_API_KEY")` holds the id only; the value lives in Cloud Secret Manager.
  - **Ledger doc id:** `<store>:<ledgerId>` (Play purchaseToken or Apple originalTransactionId), created with `tx.create`.
  - **Inside the transaction:** existing entry not `granted` → `rejected`; entry of another `uid` → `conflict`; `proof.consumed` with no entry → `rejected`; otherwise create the entry and increment the wallet.
  - **Outside the transaction:** `flagConflict` for both players, given the id and its `ledgerHash`: the flag record holds the id only in that rule-denied store, its alert or log carries `ledgerHash`; every non-`granted` outcome throws `failed-precondition` with the same message as an invalid proof.
  - **Finish:** `finishWithStore` then `finished: true`; on failure the grant stays committed, a warning is logged with the **Any other error** fields (stage `finish`) and the scheduled reconciler retries entries with `finished == false`.
  - **Any other error:** `failClosed` logs only `code`, `name`, `stage` (`verify`, `ledger`, `flag`) and, once the ledger id is known, `ledgerHash`, never `err.message` or `err.stack`, then throws `INTERNAL`, so `onCall` never logs the object.

## Refund and void handlers

| Trigger | Fact that decides |
|---|---|
| Play RTDN | `onMessagePublished("<topic>", handler)` from `firebase-functions/pubsub`; JSON body at `event.data.message.json` [f]. Re-query the Play API before acting (`google-play-developer-api.md`) |
| Play voided-purchase poll | `onSchedule("<cron or App Engine syntax>", handler)` from `firebase-functions/scheduler`; needs the Cloud Scheduler API enabled, billed [g]. Every Voided Purchases call sets `includeQuantityBasedPartialRefund=true` (`google-play-developer-api.md`) |
| App Store notifications v2 | An HTTPS `onRequest` endpoint (`firebase-functions/https`) whose URL is set in App Store Connect; verify `signedPayload` before any write (`app-store-server-api.md`) |
| Reversal write | One transaction per void event: `tx.get` the original and the event entry `<store>:<id>:void:<event id>` (event ids per platform reference); event exists → no-op; else create it, decrement the wallet by the netted amount and add it to the original's `reversedQuantity`. No original and the event is a `PURCHASED` refund or void → create the event entry with `status: "orphan"` plus a tombstone at `<store>:<id>` with `status: "voided-before-grant"` (the grant path then rejects that proof), and alert. A `FAMILY_SHARED` or `REVOKE` event touches only an original with `ownership: "FAMILY_SHARED"` and the identified player's `uid`, never a `PURCHASED` one; otherwise alert only, no tombstone. Reinstatement mirrors it with `:reinstate:<event id>`, capped at `reversedQuantity` |
| Store finish reconciler | The scheduled poll above also queries `status == "granted"` and `finished == false` and retries consume/acknowledge; a composite index on both fields |

Unverified: that every Firestore failure carries the doc path ([j] shows one `ALREADY_EXISTS`; Google's error-code page shows none, and [a] does not mention the `Unhandled error` log, which rests on [i]); which HTTP client the project's Play call uses; the retry semantics of Pub/Sub-triggered functions (`retry` option, at-least-once delivery); that `onRequest` imports from `firebase-functions/https` in the installed SDK version (older code uses `firebase-functions/v2/https`); that the Play Developer API accepts the function's runtime service account without a key file once it is invited in Play Console.
