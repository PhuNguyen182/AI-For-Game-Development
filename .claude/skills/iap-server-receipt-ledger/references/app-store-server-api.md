# App Store Server API and Notifications v2 — One-Time Purchases

Sources (under https://developer.apple.com/documentation/): [a] `appstoreserverapi/get-transaction-info`, [b] `appstoreserverapi/jwstransaction`, [c] `appstoreserverapi/jwsdecodedheader`, [d] `appstoreserverapi/jwstransactiondecodedpayload` and its field pages (`type`, `environment`, `inappownershiptype`, `revocationtype`, `appaccounttoken`), [e] `appstoreserverapi/generating-json-web-tokens-for-api-requests`, [f] `appstoreservernotifications/notificationtype`, [g] `appstoreservernotifications/responsebodyv2decodedpayload`, [h] `appstoreservernotifications/responding-to-app-store-server-notifications`, [i] `appstoreserverapi/get-refund-history`, [j] `appstorereceipts` (deprecation), [k] `appstoreserverapi/simplifying-your-implementation-by-using-the-app-store-server-library`. [m] `appstoreserverapi/transactionid`, [n] `appstoreserverapi/originaltransactionid`. Library: [l] https://github.com/apple/app-store-server-library-node (README).

## What the client sends

Unity IAP on StoreKit 2 exposes the transaction's JWS (`unity:implement-in-app-purchases` → Receipt Validation). Send that string or its `transactionId`; never a decoded payload.

## Verify the signed transaction

| Subject | Fact that decides |
|---|---|
| `JWSTransaction` | JWS Compact Serialization: header, payload, signature, Base64URL, period-separated [b] |
| `x5c` header | Chain in order: leaf signing certificate, Apple WWDR intermediate (extension OID `1.2.840.113635.100.6.2.1`), Apple root [c]. Validate it to a pinned Apple root, never trust the chain the token carries by itself |
| App Store Server Library | Apple's open-source library in Swift, Java, Python, Node: `verifyAndDecodeTransaction`, `verifyAndDecodeNotification` [k]; use it over hand-rolled JWS code |
| `SignedDataVerifier(appleRootCAs, enableOnlineChecks, environment, bundleId, appAppleId)` | Node constructor; `appAppleId` required for Production [l] |
| Root certificates | From https://www.apple.com/certificateauthority/ (Apple Root Certificates) [l]; public, not a secret |

**Caveat:** a client-supplied JWS verified offline proves Apple signed it at `signedDate`, not that it is unrefunded now. `signedDate` older than the stated bound (default 24 h; the project may tighten it) → call Get Transaction Info and grant from that verified response instead. Later refunds arrive by notification.

## Decoded payload checks [d]

| Field | Fact that decides |
|---|---|
| `transactionId` | Unique per transaction; equals `originalTransactionId` on a purchase, differs on a restore [m]. Not the ledger key: a restored non-consumable would get a second entry |
| `originalTransactionId` | Generated at the successful purchase and kept by restores [n]; `REFUND` names it [f]. Ledger key, for the grant and for every refund event on it |
| `bundleId` | Must equal the app's bundle id |
| `productId` | Must be in the server catalog; drives the grant |
| `type` | `Consumable`, `Non-Consumable`, `Auto-Renewable Subscription`, `Non-Renewing Subscription`; subscriptions are out of scope → reject |
| `quantity` | Units purchased; grant = catalog amount × quantity |
| `environment` | `Sandbox` or `Production`; the production ledger rejects `Sandbox` |
| `appAccountToken` | UUID the app sets at purchase; when used, it must map to the authenticated player |
| `revocationDate`, `revocationReason`, `revocationType`, `revocationPercentage` | Present → refunded or revoked: no grant. `revocationType` `REFUND_FULL`, `REFUND_PRORATED` (see `revocationPercentage`, milliunits), `FAMILY_REVOKE`, `ASSIGNMENT_REVOKE` |
| `inAppOwnershipType` | `PURCHASED`, `FAMILY_SHARED`, `ASSIGNED`; stored on the ledger entry. A family-shared non-consumable grants entitlement to the beneficiary — product decision, state it |

## Get Transaction Info (server-side lookup)

| Subject | Fact that decides |
|---|---|
| Endpoint | `GET https://api.storekit.apple.com/inApps/v1/transactions/{transactionId}`; sandbox `https://api.storekit-sandbox.apple.com/…` [a]. Apple's current page and the library's `PRODUCTION_URL`/`SANDBOX_URL` [l] both use these hosts; older material shows `api.storekit.itunes.apple.com` |
| Coverage | Any transaction id including original ids; consumable, non-consumable and subscription types; also transactions the app already finished [a] |
| Response | `signedTransactionInfo` — a JWS: verify it like a client JWS |
| Errors | 400 invalid request, 401 invalid JWT, 404 transaction id not found, 429 rate limit, 500 retry later [a] |
| Auth | Bearer JWT, ES256; header `alg`, `kid` (key id), `typ` `JWT`; claims `iss` (issuer id), `iat`, `exp` (≤ 60 min after `iat`), `aud` `appstoreconnect-v1`, `bid` (bundle id); Apple says to generate a new JWT per request [e] |
| Key | The App Store Connect private key: secret store, by id; needed only for API calls, not for JWS verification |

## Notifications v2

| Subject | Fact that decides |
|---|---|
| Body | `signedPayload` (JWS) → `verifyAndDecodeNotification` [g][l] |
| Decoded payload | `notificationType`, `subtype`, `data` (holds `signedTransactionInfo` — verify it too), `version` `"2.0"`, `signedDate`, `notificationUUID` (unique per notification; identifies duplicates) [g] |
| `REFUND` | Refunded consumable, non-consumable or subscription; transaction carries `revocationDate`, `revocationReason` [f]. Match on `originalTransactionId` from the verified `data.signedTransactionInfo` (the grant key); write `apple:<originalTransactionId>:void:<revocationDate>` — the same key whether the event came by notification or by Refund History. Amount: `REFUND_FULL` → the quantity not yet reversed; `REFUND_PRORATED` → `quantity × revocationPercentage / 100000`, rounded down, flagged |
| `REFUND_REVERSED` | A refund reversed after a customer dispute: reinstate what the refund revoked [f]; write `apple:<originalTransactionId>:reinstate:<notificationUUID>`, capped at the entry's `reversedQuantity` |
| `REFUND_DECLINED` | Refund request declined: no ledger change [f] |
| `CONSUMPTION_REQUEST` | Customer asked for a refund of a consumable; Apple requests consumption data (Send Consumption Information) [f] |
| `ONE_TIME_CHARGE` | Customer bought a consumable, non-consumable or non-renewing subscription; usable as a server-side purchase signal [f] |
| `REVOKE` | Family Sharing or organization entitlement withdrawn [f]. Reverses only an entry stored as `FAMILY_SHARED` whose player the event identifies (`appAccountToken` mapped to that player); never a `PURCHASED` entry; no such entry → alert only, no tombstone |
| Response | HTTP 200–206 = received; 40x/50x = retry. v2 retries five times at 1, 12, 24, 48, 72 h after the previous attempt; sandbox sends once only [h] |
| Missed notifications | Get Notification History; refunds per customer via Get Refund History `GET /inApps/v2/refund/lookup/{anyTransactionId}`, pages of up to 20, `revision` token [h][i] |
| Deprecated | `verifyReceipt` and Notifications v1 [j][h] |

**Caveat:** answer 200 only after the reversal entry commits; 5xx on a transient failure so Apple retries; 4xx, a log line and no ledger change on a signature failure (fail closed).

Unverified: whether a Family-Shared non-consumable's transaction carries the purchaser's `originalTransactionId` or its own — the rule above does not depend on it: a `FAMILY_SHARED` or `REVOKE` event acts only on a `FAMILY_SHARED` entry of the identified player, else alerts, and never tombstones; numeric values of `revocationReason`; whether `REFUND_PRORATED` ever applies to a one-time purchase; the Send Consumption Information endpoint and its response deadline; whether the Node library's API client names its Get Transaction Info method `getTransactionInfo`.
