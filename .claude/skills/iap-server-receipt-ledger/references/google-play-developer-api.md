# Google Play Developer API — One-Time Products

Sources (below the SKILL.md `Docs:` base): [a] `purchases.products`, [b] `purchases.products/get`, [c] `purchases.products/acknowledge`, [d] `purchases.products/consume`, [e] `purchases.voidedpurchases` and `/list`, [f] `purchases.productsv2/getproductpurchasev2`. Elsewhere: [g] https://developer.android.com/google/play/billing/security, [h] https://developers.google.com/android-publisher/voided-purchases, [i] https://developer.android.com/google/play/billing/rtdn-reference, [j] https://developers.google.com/android-publisher/getting_started.

Base URL `https://androidpublisher.googleapis.com/androidpublisher/v3/applications/{packageName}`; every call below needs OAuth scope `https://www.googleapis.com/auth/androidpublisher`. `{packageName}` is server configuration, never taken from the client.

## Access

| Subject | Fact that decides |
|---|---|
| Identity | A Google Cloud service account with the Play Developer API enabled in its project; linking the developer account to a Cloud project is no longer required [j] |
| Play Console permission | Invite the service account email in Users & permissions; grant "View financial data, orders, and cancellation survey responses" and "Manage orders and subscriptions" [j] |
| Credential | The backend runtime's own service account where it runs on Google Cloud, else a key held in the secret store and referenced by id — never in the repo or client (`core.md` Security) |

## Verify — `purchases.products.get`

`GET {base}/purchases/products/{productId}/tokens/{token}`, empty body [b]. `productId` comes from the client as a hint: check it against the server catalog before the call; the grant reads the response.

**Caveat:** `ProductPurchase.productId` is documented as "May not be present" [a]. Grant only when the response's product id is present and equals the catalog-checked hint. Absent → read `productLineItem[].productId` from `purchases.productsv2` (`GET {base}/purchases/productsv2/tokens/{token}` [f]) and require exactly one line item equal to the hint. Still absent or different → no grant (fail closed).

| Field | Fact that decides |
|---|---|
| `purchaseState` | `0` Purchased, `1` Canceled, `2` Pending [a]. Grant only on `0`; never on Pending [g] |
| `consumptionState` | `0` yet to be consumed, `1` consumed [a]. Not a verification failure: pass it to the ledger transaction, which returns an existing entry first and rejects `1` only when no entry exists (our own consume sets it after the grant) |
| `acknowledgementState` | `0` / `1` [a]; drives the finish call, not the grant |
| `purchaseType` | Absent for the standard billing flow; `0` Test (license tester), `1` Promo, `2` Rewarded [a]. `0` never reaches the production ledger |
| `quantity` | Absent means 1 [a]; grant = catalog amount × quantity |
| `obfuscatedExternalAccountId` | Present only if set at purchase [a]; when the client sets it, it must map to the authenticated player [g] |
| `orderId` | Absent on promo-code purchases: never a dedupe key [g] |
| `purchaseToken` | Globally unique: safe as the ledger primary key [g] |
| `refundableQuantity` | Quantity still refundable after partial and full refunds [a] |

## Finish

| Call | Fact that decides |
|---|---|
| `POST {base}/purchases/products/{productId}/tokens/{token}:consume` | Consumables; empty body, empty response [d] |
| `POST …/tokens/{token}:acknowledge` | Non-consumables; optional body field `developerPayload` [c] |
| Three-day rule | Not acknowledged within three days → automatically refunded; acknowledge from the server right after granting [g] |
| Failed checks | Do not grant, acknowledge or consume; Google recommends an explicit `orders.refund` with `revoke: true` over waiting for the auto-refund [g] |

## Voids — Voided Purchases API

`GET {base}/purchases/voidedpurchases` [e].

| Subject | Fact that decides |
|---|---|
| Window | `startTime` defaults to now − 30 days and cannot be older; poll at least that often or voids are lost [e][h] |
| `type` | `0` in-app only (default); `1` adds subscriptions and requires keying on `orderId` [e] |
| `includeQuantityBasedPartialRefund` | Default `false`; `true` adds records carrying `voidedQuantity` for multi-quantity purchases [e]. Set `true` on every call (poll and RTDN fetch), or partial refunds never appear |
| Paging | `maxResults` default and max 1000; follow `nextPageToken` [h] |
| Quota per package | 6,000 queries per day (resets midnight Pacific), 30 queries per 30 seconds [h] |
| `voidedSource` | `0` User, `1` Developer, `2` Google [e] |
| `voidedReason` | `0` Other, `1` Remorse, `2` Not_received, `3` Defective, `4` Accidental_purchase, `5` Fraud, `6` Friendly_fraud, `7` Chargeback, `8` Unacknowledged_purchase [e] |
| Record keys | `purchaseToken` (ledger match), `orderId`, `purchaseTimeMillis`, `voidedTimeMillis` [e] |
| Coverage | Refunds, cancellations and chargebacks; only revoked orders appear [h] |

**Caveat:** poll with `includeQuantityBasedPartialRefund=true`, a stored high-water mark on `voidedTimeMillis` and an overlap window. Key each record `play:<purchaseToken>:void:<voidedTimeMillis>`, so overlap duplicates collapse and repeated partial voids of one token stay distinct. Amount: `voidedQuantity` when present, else the quantity not yet reversed (full void); net it against the original entry's `reversedQuantity`.

## Voids — Real-time developer notifications

| Subject | Fact that decides |
|---|---|
| Delivery | Cloud Pub/Sub topic; each message has one base64 `data` field decoding to a `DeveloperNotification` [i] |
| `voidedPurchaseNotification` | `purchaseToken`, `orderId`, `productType` (`1` subscription, `2` one-time), `refundType` (`1` full, `2` quantity-based partial; a purchase can be partially voided more than once) [i] |
| `oneTimeProductNotification` | `notificationType` `1` purchased, `2` canceled; sent only after opting in to one-time product events [i] |
| Signal only | Notifications carry no purchase status: call the API before acting [i]; dedupe on `messageId` [i]. On a void, fetch Voided Purchases (`includeQuantityBasedPartialRefund=true`) for a short recent window and process its records with the key above, so both sources write identical keys |
| When | Only when reversal must land faster than the poll interval; the Voided Purchases API stays the reconciler [h] |

Unverified: the response when the hint `productId` does not match the token's product; whether `purchases.productsv2.getproductpurchasev2` supersedes `purchases.products.get` (neither page says so), and how often `ProductPurchase.productId` is absent in practice; behaviour of `consume`/`acknowledge` when repeated on an already finished token; whether a keyless runtime service account is accepted by every hosting option.
