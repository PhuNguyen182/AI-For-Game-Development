# Firebase: Cloud Functions (2nd gen) + Firestore Ledger

Sources (under https://firebase.google.com/docs/): [a] `functions/callable`, [b] `app-check/cloud-functions`, [c] `functions/config-env`, [d] `firestore/manage-data/transactions`, [e] `firestore/security/get-started`, [f] `functions/pubsub-events`, [g] `functions/schedule-functions`. Elsewhere: [h] Node Firestore `Transaction` https://docs.cloud.google.com/nodejs/docs/reference/firestore/latest/firestore/transaction.

## Endpoint

| Subject | Fact that decides |
|---|---|
| `onCall` from `firebase-functions/https` | Callable trigger: deserializes the body and validates Firebase Auth (and App Check) tokens the client SDK attaches automatically [a] |
| `request.auth.uid` | The player. `request.auth` absent → `throw new HttpsError("unauthenticated", …)`; never read a uid from `request.data` |
| `enforceAppCheck: true` | Rejects requests with missing or invalid App Check tokens [b]. Needs App Check on the client, which no skill in this layer covers: a `Known limitations` line until one does |
| `consumeAppCheckToken: true` | Replay protection, beta, Node only; one extra network round trip per call [b] |
| `HttpsError(code, message, details)` | The only error shape the client sees as-is; any other thrown error reaches the client as `INTERNAL` [a] |
| Unity client | `FirebaseFunctions` → `GetHttpsCallable("name").CallAsync(data)`; failures surface as `FunctionsException` [a] |
| Secrets | `defineSecret("NAME")` from `firebase-functions/params`, bound per function through the `secrets` option, `.value()` read only inside the handler at runtime [c] |
| `functions.config()` | Deprecated since `firebase-functions` 6.0.0; new deploys using it fail after March 2027 [c] |
| Security rules | Server client libraries bypass all Firestore Security Rules [e]: rules must deny client writes to the ledger collection and every wallet/inventory field the function writes |

## Ledger transaction

| Subject | Fact that decides |
|---|---|
| `db.runTransaction(fn)` | Reads before writes; reruns `fn` on concurrent edits of documents it read; writes nothing on failure [d] |
| Side effects | Do not modify application state inside the transaction function [d]: no store API call, consume or acknowledge in `fn` — it may run more than once |
| `tx.get(ref)` | Server SDK read holding a pessimistic lock on the document [h] |
| `tx.create(ref, data)` | Fails the transaction if the document already exists [h] — the idempotency guard on `<store>:<id>` |
| Limits | Lock deadline 20 s, total 270 s, 60 s idle timeout, 10 MiB request [d] |

```js
// Shape only. verifyWithStore, finishWithStore, flagConflict and CATALOG are project code.
const {onCall, HttpsError} = require("firebase-functions/https");
const logger = require("firebase-functions/logger");
const {defineSecret} = require("firebase-functions/params");
const {initializeApp} = require("firebase-admin/app");
const {getFirestore, FieldValue} = require("firebase-admin/firestore");

initializeApp();
// Secret id only; the value lives in Cloud Secret Manager.
const appStoreKey = defineSecret("APP_STORE_SERVER_API_KEY");
const REJECTED = "Purchase could not be verified.";

exports.redeemPurchase = onCall({enforceAppCheck: true, secrets: [appStoreKey]}, async (request) => {
  if (!request.auth) {
    throw new HttpsError("unauthenticated", "Sign-in required.");
  }
  const uid = request.auth.uid;
  // Store checks only (state, product id, package, signature); throws HttpsError("failed-precondition", REJECTED).
  // Consumption state is returned in proof.consumed, not judged here.
  const proof = await verifyWithStore(request.data, appStoreKey);
  const db = getFirestore();
  const ledgerRef = db.collection("iapLedger").doc(`${proof.store}:${proof.ledgerId}`);  // Play purchaseToken | Apple originalTransactionId
  const walletRef = db.collection("wallets").doc(uid);

  const outcome = await db.runTransaction(async (tx) => {
    const existing = await tx.get(ledgerRef);
    if (existing.exists) {
      if (existing.get("status") !== "granted") {
        return {result: "rejected"};                      // void tombstone
      }
      if (existing.get("uid") !== uid) {
        return {result: "conflict", owner: existing.get("uid")};
      }
      return {result: "granted", grant: existing.get("grant")};
    }
    if (proof.consumed) {
      return {result: "rejected"};                        // consumed, never granted here
    }
    const lines = CATALOG.grantFor(proof.productId, proof.quantity);
    tx.create(ledgerRef, {uid, store: proof.store, productId: proof.productId, quantity: proof.quantity,
      ownership: proof.ownership, reversedQuantity: 0, grant: lines, status: "granted", finished: false,
      createdAt: FieldValue.serverTimestamp()});
    tx.set(walletRef, {gems: FieldValue.increment(lines.gems)}, {merge: true});
    return {result: "granted", grant: lines};
  });

  if (outcome.result === "conflict") {
    await flagConflict(ledgerRef.id, outcome.owner, uid);  // both players, outside the transaction
  }
  if (outcome.result !== "granted") {
    throw new HttpsError("failed-precondition", REJECTED); // same reason as an invalid proof
  }
  try {
    await finishWithStore(proof);                          // consume/acknowledge on Play; no-op on Apple
    await ledgerRef.update({finished: true});
  } catch (err) {
    // Grant is committed; the scheduled reconciler retries entries with finished == false.
    logger.warn("store finish deferred", {ledgerId: ledgerRef.id});
  }
  return {status: "granted", grant: outcome.grant};
});
```

## Refund and void handlers

| Trigger | Fact that decides |
|---|---|
| Play RTDN | `onMessagePublished("<topic>", handler)` from `firebase-functions/pubsub`; JSON body at `event.data.message.json` [f]. Re-query the Play API before acting (`google-play-developer-api.md`) |
| Play voided-purchase poll | `onSchedule("<cron or App Engine syntax>", handler)` from `firebase-functions/scheduler`; needs the Cloud Scheduler API enabled, billed [g]. Every Voided Purchases call sets `includeQuantityBasedPartialRefund=true` (`google-play-developer-api.md`) |
| App Store notifications v2 | An HTTPS `onRequest` endpoint (`firebase-functions/https`) whose URL is set in App Store Connect; verify `signedPayload` before any write (`app-store-server-api.md`) |
| Reversal write | One transaction per void event: `tx.get` the original and the event entry `<store>:<id>:void:<event id>` (event ids per platform reference); event exists → no-op; else create it, decrement the wallet by the netted amount and add it to the original's `reversedQuantity`. No original and the event is a `PURCHASED` refund or void → create the event entry with `status: "orphan"` plus a tombstone at `<store>:<id>` with `status: "voided-before-grant"` (the grant path then rejects that proof), and alert. A `FAMILY_SHARED` or `REVOKE` event touches only an original with `ownership: "FAMILY_SHARED"` and the identified player's `uid`, never a `PURCHASED` one; otherwise alert only, no tombstone. Reinstatement mirrors it with `:reinstate:<event id>`, capped at `reversedQuantity` |
| Store finish reconciler | The scheduled poll above also queries `status == "granted"` and `finished == false` and retries consume/acknowledge; a composite index on both fields |

Unverified: the retry semantics of Pub/Sub-triggered functions (`retry` option, at-least-once delivery); that `onRequest` imports from `firebase-functions/https` in the installed SDK version (older code uses `firebase-functions/v2/https`); that the Play Developer API accepts the function's runtime service account without a key file once it is invited in Play Console.
