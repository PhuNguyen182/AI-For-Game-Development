// Shape of the Firebase Functions 2nd gen redeemPurchase callable with a Firestore ledger transaction.
// Adapt into: the Cloud Functions source (functions/index.js)
// Unverified: run only under stubs of Firebase and the project code, never against Firebase, Firestore or a store.
// Shape only. verifyWithStore, finishWithStore, flagConflict and CATALOG are project code.
const {createHash} = require("crypto");
const {onCall, HttpsError} = require("firebase-functions/https");
const logger = require("firebase-functions/logger");
const {defineSecret} = require("firebase-functions/params");
const {initializeApp} = require("firebase-admin/app");
const {getFirestore, FieldValue} = require("firebase-admin/firestore");

initializeApp();
// Secret id only; the value lives in Cloud Secret Manager.
const appStoreKey = defineSecret("APP_STORE_SERVER_API_KEY");
const REJECTED = "Purchase could not be verified.";
// A Play ledger id holds the purchase token, a replayable proof: logs get this hash, never the id.
// The hash is for correlation, not concealment of an enumerable id; a project needing concealment uses an HMAC whose key lives in the secret store.
const ledgerHash = (ledgerId) => createHash("sha256").update(ledgerId).digest("hex").slice(0, 16);
// onCall logs any other thrown error whole as "Unhandled error", and a Firestore error or a request URL can hold the token.
// So an error log gets only code, name, stage and ledgerHash once known, never err.message or err.stack.
const failClosed = (err, ctx) => {
  if (err instanceof HttpsError) {
    throw err;
  }
  logger.error("redeem failed", {code: err?.code, name: err?.name, ...ctx});
  throw new HttpsError("internal", "INTERNAL");
};

const redeem = async (request, ctx) => {
  if (!request.auth) {
    throw new HttpsError("unauthenticated", "Sign-in required.");
  }
  const uid = request.auth.uid;
  // Store checks only (state, product id, package, signature); on a failed check logs stage "verify" and a reason from a fixed list,
  // never the proof, then throws HttpsError("failed-precondition", REJECTED). An unexpected exception propagates, so failClosed logs it.
  // Consumption state is returned in proof.consumed, not judged here.
  const proof = await verifyWithStore(request.data, appStoreKey);
  ctx.stage = "ledger";
  const db = getFirestore();
  const ledgerRef = db.collection("iapLedger").doc(`${proof.store}:${proof.ledgerId}`);  // Play purchaseToken | Apple originalTransactionId
  ctx.ledgerHash = ledgerHash(ledgerRef.id);
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
    ctx.stage = "flag";
    // Both players, outside the transaction. The flag record holds the id only in a store clients cannot read; its alert or log carries ledgerHash.
    await flagConflict(ledgerRef.id, outcome.owner, uid, ledgerHash(ledgerRef.id));
  }
  if (outcome.result !== "granted") {
    throw new HttpsError("failed-precondition", REJECTED); // same reason as an invalid proof
  }
  try {
    await finishWithStore(proof);                          // consume/acknowledge on Play; no-op on Apple
    await ledgerRef.update({finished: true});
  } catch (err) {
    // Grant is committed; the scheduled reconciler retries entries with finished == false.
    logger.warn("store finish deferred", {code: err?.code, name: err?.name, stage: "finish", ledgerHash: ledgerHash(ledgerRef.id)});
  }
  return {status: "granted", grant: outcome.grant};
};

exports.redeemPurchase = onCall({enforceAppCheck: true, secrets: [appStoreKey]}, (request) => {
  const ctx = {stage: "verify"};
  return redeem(request, ctx).catch((err) => failClosed(err, ctx));
});
