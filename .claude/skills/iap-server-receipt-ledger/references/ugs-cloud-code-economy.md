# UGS: Economy Real-Money Purchases + Cloud Code

Sources (under https://docs.unity.com/en-us/): [a] `economy/sdk/purchases`, [b] `economy/add-real-money-purchase`, [c] `cloud-code/modules/how-to-guides/access-control`, [d] `services/secret-manager/tutorials/integrations/cloud-code/modules`, [e] `triggers/overview`. [g] `services/access-control`, [h] `cloud-code/3.0.0/server-access-control`. Elsewhere: [f] Cloud Code JavaScript Economy SDK https://cloud-code-sdk-documentation.cloud.unity3d.com/economy/v2.0/configurationparameters.

## Pick the path

| Path | Fact that decides |
|---|---|
| Economy real-money purchase, redeemed from a Cloud Code module | Economy verifies the store proof and applies the rewards configured on the dashboard Real Money Purchase resource [a][b]; the client never names the reward. Verification, dedupe and grant are one service call: this satisfies step 5's single transaction. The module checks the void tombstone before redeeming, so SKILL.md step 8 holds. Client-side redeem (`EconomyService.Instance.Purchases` from the game) is not supported by this skill: it bypasses the tombstone (buy → refund while unredeemed → redeem) |
| Custom Cloud Code grant | Only when rewards need server logic Economy cannot express. Cloud Save and Economy are separate services with no shared transaction → SKILL.md step 5 `Needs-decision` |

## Economy redeem

Call from the Cloud Code module: the JavaScript `PurchasesApi` exposes Redeem Apple App Store Purchase and Redeem Google Play Purchase [f]. Member names below are from the client SDK page [a], which documents the arguments and results.

| Member | Fact that decides |
|---|---|
| `RedeemAppleAppStorePurchaseAsync(RedeemAppleAppStorePurchaseArgs)` | Args `RealMoneyPurchaseId`, `Receipt`, `LocalCost`, `LocalCurrency` [a] |
| `RedeemGooglePlayPurchaseAsync(RedeemGooglePlayStorePurchaseArgs)` | Args `RealMoneyPurchaseId`, `PurchaseData` (purchase JSON), `PurchaseDataSignature`, `LocalCost`, `LocalCurrency` [a] |
| `LocalCost`, `LocalCurrency` | Integer minor units (199 = USD 1.99) and ISO-4217 [a]; client-reported, never an input to the grant |
| Result `Verification.Status`, `Rewards` | Rewards hold the currency and inventory applied [a] |
| Exceptions | `EconomyAppleAppStorePurchaseFailedException` / `EconomyGooglePlayStorePurchaseFailedException`, both `EconomyException`; their own `Data` field (not `Exception.Data`) holds the result [a] |
| Google License Key | Set in the project's Development settings on the Unity Dashboard [b] |
| Product mapping | Same product ids configured in both stores and in the Real Money Purchase's per-store fields [b] |
| Subscriptions | Apple `INVALID_VERIFICATION_FAILED` with store code `21003` can mean the receipt holds an auto-renewable subscription, which Economy does not validate [a] |

## Status → action

| `Verification.Status` [a] | Action |
|---|---|
| `VALID` | Granted; write the mapping (below); client may `ConfirmPurchase` |
| `INVALID_ALREADY_REDEEMED` | Already granted to this player: write the mapping again (idempotent), confirm, no second credit |
| `VALID_NOT_REDEEMED` | Valid, seen before, not redeemed: no confirm; retry the redeem |
| `INVALID_ANOTHER_PLAYER` | Proof used by another player: reject, flag, no confirm |
| `INVALID_VERIFICATION_FAILED` | Fail closed: no grant, no confirm |
| `INVALID_PRODUCT_ID_MISMATCH` | Catalog mismatch: no grant, no confirm, fix configuration |
| `INVALID_CONFIGURATION` | Service misconfigured: no grant, no confirm, alert; the store re-delivers the pending order later |

## Lock down player writes

| Subject | Fact that decides |
|---|---|
| Default | With no policy, Access Control allows every authenticated API call from authenticated players [g] |
| `Action` | `Write` = POST, PUT, PATCH, DELETE on UGS APIs; `Read` = GET; `*` = both [g] |
| Deny all Economy writes | `{"Sid": "deny-economy-writes", "Effect": "Deny", "Action": ["Write"], "Principal": "Player", "Resource": "urn:ugs:economy:/**"}` [h] — covers balance set/increment/decrement, inventory add/update/delete and purchases. The narrower `urn:ugs:economy:/*/*crement` example [c] leaves set-balance and inventory open: not enough |
| No player Allow on purchases | Omit the `urn:ugs:economy:/**/purchases/*` Allow from the docs' example [h]: it also opens real-money redeem to the client and bypasses the void tombstone. Real-money redeem and virtual purchases go through the module; a narrower Allow for virtual purchases only once its URN is confirmed |
| Deny Cloud Save writes | `{"Effect": "Deny", "Action": ["Write"], "Principal": "Player", "Resource": "urn:ugs:cloud-save:/**"}` [h], so a player cannot write the mapping or void entries below; re-allow narrower paths (e.g. `/**/query` [h]) only as needed |
| Evaluation | The most specific matching rule wins; Deny beats Allow only between identical `Resource` values [g] |
| Apply | `ugs access upsert-project-policy project-policy.json`; a blocked call returns 403, code 56 [c] |
| Why | Under the default allow-all, a modified client writes its own balance or inventory through the public Economy API, so receipt verification protects nothing |

## Cloud Code module surface

| Member | Fact that decides |
|---|---|
| `[CloudCodeFunction("Name")]` | Exposes the method [c] |
| `IExecutionContext` | `ProjectId`, `PlayerId` (the authenticated caller — the identity source), `ServiceToken` [c] |
| `IGameApiClient` | Injected; `config.AddGameApiClient()` in an `ICloudCodeSetup` needs `com.unity.services.cloudcode.core` ≥ 0.0.4 and `…apis` ≥ 0.0.24 [c] |
| `ctx.ServiceToken` | Calls Economy as a trusted service, which the Deny policy above does not block [c] |
| `EconomyCurrencies.IncrementPlayerCurrencyBalanceAsync(ctx, ctx.ServiceToken, ctx.ProjectId, ctx.PlayerId, currencyId, new CurrencyModifyBalanceRequest(currencyId, amount))` | Server-side credit or reversal; balance responses carry a `writeLock` [c] |
| Secrets | `gameApiClient.SecretManager.GetSecret(ctx, "<secret-name>")`, value in `.Value`; Cloud Code access must be allowed per secret [d] |

## Refunds and voids

| Subject | Fact that decides |
|---|---|
| Economy | The Economy purchase docs describe no refund reversal [a][b]: reversal is project code |
| Player mapping | A void names only the store id: the module records `<store>:<id>` → player at redeem time |
| Mapping write | On `VALID` and on `INVALID_ALREADY_REDEEMED`, keyed by store id, same value every time (idempotent set); the client confirms only after the module returns, so a crash before the write re-delivers the order and the replay's `INVALID_ALREADY_REDEEMED` rewrites it |
| Play voids | Scheduler recurring schedule (cron only, minimum frequency once per hour, payload ≤ 1 KB) → Triggers → Cloud Code module polling the Voided Purchases API with `includeQuantityBasedPartialRefund=true` (`google-play-developer-api.md`) [e] |
| Apple REFUND | App Store posts notifications to a public HTTPS URL; host that receiver outside Cloud Code unless the project confirms otherwise → `Needs-decision`, `Next: cto` |
| Reversal | One Cloud Save entry per void event, `<store>:<id>:void:<event id>` / `:reinstate:<event id>` (event ids per platform reference), netted against a `reversedQuantity` on the mapping; then `DecrementPlayerCurrencyBalanceAsync` with `ctx.ServiceToken`. The mapping stores the ownership (Apple `inAppOwnershipType`). No mapping and the event is a `PURCHASED` refund or void → store it as an orphan, alert, and write a tombstone on the mapping key that makes the module refuse a later redeem of that proof. A `FAMILY_SHARED` or `REVOKE` event reverses only a `FAMILY_SHARED` mapping of the identified player, never a `PURCHASED` one; otherwise alert only, no tombstone. Event write and decrement are separate calls: write the event as `pending`, decrement, mark `applied`. Never auto-retry a `pending` decrement — a crash after the decrement and before the mark would charge twice; a `pending` event older than the retry window raises an alert for manual reconciliation (SKILL.md Output, Known limitations) |

Unverified: whether the Cloud Code C# `IGameApiClient` exposes the Economy redeem calls; whether Economy's Apple redeem accepts a StoreKit 2 JWS as `Receipt`; whether Economy verifies Google purchases only by signature against the License Key or also queries the Play Developer API, and whether it acknowledges or consumes server-side; the C# name `DecrementPlayerCurrencyBalanceAsync` and Economy's behaviour on a decrement below zero; whether a Cloud Code module can accept an unauthenticated webhook; Cloud Save `writeLock` semantics; the exact Economy endpoint paths behind the URNs (that real-money redeem and virtual purchases both sit under `/purchases/`, and a URN that matches virtual purchases alone).
