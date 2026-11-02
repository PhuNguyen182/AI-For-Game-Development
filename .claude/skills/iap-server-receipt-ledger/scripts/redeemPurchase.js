// Shape of the Firebase Functions 2nd gen redeemPurchase callable with a Firestore ledger transaction.
// Adapt into: the Cloud Functions source (functions/index.js)
// Unverified: not compiled or run (no Unity project in this repo).
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
