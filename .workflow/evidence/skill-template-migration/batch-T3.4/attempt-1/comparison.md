# Comparison: batch T3.4, attempt 1

- **Base:** `bdf5c9ec70bf217ee9ed2763abd75fa4280b717c`.
- **Verdict:** fail. Failing skills: `firebase-unity-sdk`, `iap-server-receipt-ledger`, `consent-att-init-order`, `crash-anr-reporting-gate`, `server-authoritative-validation`.
- **Other 11 skills:** every Base criterion kept or moved as listed below. Kept lines are not listed.
- **Author's cut claims:** each fact named as moved is in its reference. Of the 18 facts tested, 15 pass the trigger test. Three do not: the Analytics key pin, the UGS reversal limit, and the Apple JWS refresh in step 3's closed list.

## Findings

Line numbers: Base at the Base sha, current in the working tree. Every `SKILL.md` line below is under 200 chars and keeps step numbers. Sizes after all fixes are under "Body size".

| Skill | Check | Base text | Current text | Why it fails | Exact fix |
|---|---|---|---|---|---|
| `firebase-unity-sdk` | 1, 2 (consent check; selection lost) | `:26` "Build-time off key on both platforms (Android `firebase_analytics_collection_enabled` = `false`, iOS `FIREBASE_ANALYTICS_COLLECTION_ENABLED` = `NO`)" | `SKILL.md:49` "build-time off keys on both platforms, per [analytics.md]" | The fact is in `analytics.md:22`, `:26`, and the link fires. The pin is not. That table also lists `firebase_analytics_collection_deactivated` (`:23`) and `FIREBASE_ANALYTICS_COLLECTION_DEACTIVATED` (`:27`), both "permanent for that app version", and says nowhere which pair this step means. A deactivated key can never follow consent. Base named the pair; only `SKILL.md` made that choice. | Replace `:49` with two lines: ``6. **Analytics collection is off in the build and follows `AnalyticsStorage` after consent resolves:** per [analytics.md](references/analytics.md).`` and ``   - **Build-time off key, both platforms:** Android `firebase_analytics_collection_enabled` = `false`, iOS `FIREBASE_ANALYTICS_COLLECTION_ENABLED` = `NO`.`` |
| `firebase-unity-sdk` | 8 (text added to the step) | `:28` "A zero fetch interval only in development builds." | `SKILL.md:59` "development builds only, behind a development-only scripting define." | Base `SKILL.md` never said this; the define is already at `remote-config.md:32`. It says the fact twice and spends 44 chars in a skill that needs them for the row above. | Replace `:59`: ``   - **Zero fetch interval:** development builds only.`` |
| `iap-server-receipt-ledger` | 1, 2 (brief "Remove or move"; trigger test) | `:49` "UGS: a reversal's decrement is not atomic with its event entry — stale `pending` events alert and are reconciled by hand, never auto-retried" | `references/ugs-cloud-code-economy.md:72` only; `SKILL.md:54`-`:61` has no UGS line and never names the backend reference | The brief says a domain limit in that line "becomes a `## Never` bullet or a step". It became neither. Step 8 points only at the platform reference, so at reversal time nothing leads to the backend's Reversal row (`ugs:72`, `firebase-functions-firestore.md:44`). The row loads only because step 5 opened that file earlier. The UGS limit also left the output a reader sees. | Insert after `:61`: ``   - **Reversal write:** per the backend reference.`` and ``   - **UGS:** a reversal's decrement is not atomic with its event entry; stale `pending` events alert and are reconciled by hand, never auto-retried; report it in `Limitations`.`` |
| `iap-server-receipt-ledger` | 1, 2 (closed list dropped an action) | `:23` "refreshed through Get Transaction Info when the JWS is older than the stated bound" | `SKILL.md:34` "which lists the Play state and product-id checks and the Apple signature-chain and payload checks" | The fact is at `app-store-server-api.md:19` and the step loads that file, so it is not lost. The summary reads as a complete list and omits the one item that is an action. It changes the grant source, and a stale JWS can already be refunded. | Insert after `:34`: ``   - **Apple JWS older than the stated bound:** refresh through Get Transaction Info and grant from that verified response.`` |
| `iap-server-receipt-ledger` | 2 (plain word; anchor) | `:28` "a scheduled Voided Purchases API poll"; `:26` "the step 8 scheduled poll" | `SKILL.md:55` "Play Voided Purchases poll"; `:50` "the step 8 scheduled poll" | `:50` cites a scheduled poll that step 8 no longer calls scheduled. That poll is also the store-finish reconciler. | Replace `:55`: ``   - **Sources:** per platform reference: Play scheduled Voided Purchases poll (plus RTDN when reversal must beat it); Apple v2 `REFUND`, `REFUND_REVERSED` reinstates.`` |
| `consent-att-init-order` | 2 (orphan reference) | `:21` "then Firebase `SetConsent` + collection from the per-type sources ... — skipped when the status is not `Available`" | `SKILL.md:37` "**(d) not `Available`:** skipped." | The split lost the subject. The bootstrap has already awaited by then, so what is skipped is `SetConsent` + collection. As written it can read as "(d) is skipped", which takes the bootstrap with it. | Replace `:37`: ``   - **(d) not `Available`:** Firebase `SetConsent` + collection skipped.`` |
| `consent-att-init-order` | 6, 8 (adapt target contradicts the skill) | `:21` "owned by one bootstrap"; fence comment "Client startup" named no file | `references/google-ump.md:20` and `scripts/StartupConsentFlow.cs:2` give a new file `Platform/StartupConsentFlow.cs` holding "members of the client startup class" | The fence is members, not a class, so the file cannot exist alone. A project that already has a startup class would gain a second sequence owner, against step 3. T3.3 ruled that a fragment's target names its host. Path segments otherwise follow `csharp-standards`. | Replace the opening of `google-ump.md:20`, up to the first `;`: ``  - **Adapt into:** the one bootstrap class that owns SKILL.md step 3's sequence, or `Assets/_Project/Scripts/Platform/StartupConsentFlow.cs` when the project has none`` Replace `StartupConsentFlow.cs:2`: `// Adapt into: the one bootstrap class that owns the startup sequence, or Assets/_Project/Scripts/Platform/StartupConsentFlow.cs when none exists (members only)` |
| `crash-anr-reporting-gate` | 5 (ask fix narrowed) | `:20` "Otherwise unconfirmed counts as absent. \"Set up a while ago\" is a No; ask rather than assume." | `SKILL.md:32` "a No."; `:39` "whether the gate passed earlier, or by what evidence, unconfirmed" | Base's ask covers the service's confirmation, the subject of `:20` and of step 3. "Whether the gate passed earlier" covers only step 4's shortcut, so "set up a while ago" no longer clearly triggers it. "Rather than assume" is gone, and step 4 does not point at step 8. The spec's Missing input class requires that pointer. | Replace `:32`: ``   - **"Set up a while ago":** a No; never assume, per step 8.`` Replace `:39`: ``8. **Missing input:** whether the service is reporting, or whether an earlier pass still holds, unconfirmed → dispatched agent `Blocked` or `Needs-decision`; main session `AskUserQuestion`.`` |
| `server-authoritative-validation` | 6 (`## Scripts`) | Fence at `rate-limits-and-rejection.md:20`: a whole class | No `## Scripts` section; author's reason is saving chars | Complete, compilable type: own namespace, three constructor args, header states the cost rule. It is usable without the reference, so the template lists it, as `FirebaseBootstrap.cs` and the T3.3 samples are. Size is no reason to omit it; the 8,000 is soft. | Insert before `:25` (`## Steps`): ``## Scripts`` then ``- **[ConnectionRateLimiter.cs](scripts/ConnectionRateLimiter.cs):** adapt into `Assets/_Project/Scripts/Networking/Server/ConnectionRateLimiter.cs` → integer token bucket on server ticks.`` then a blank line |
| `server-authoritative-validation` | 6, 8 (invented claim in header) | Fence `sender-identity-per-stack.md:22` named no location | `scripts/UseItemRpc.cs:2` "the server-side NetworkBehaviour that receives the item-use Rpc" | Base never says "server-side". `[Rpc(SendTo.Server)]` is declared on a `NetworkBehaviour` that the calling client compiles too, so a `<Feature>/Server` reading breaks the call. `sender-identity-per-stack.md:23` is correct and disagrees with the header. | Replace `UseItemRpc.cs:2`: `// Adapt into: the NetworkBehaviour that owns the Rpc (method only)` |

## Body size

Chars after the frontmatter, by Python, on a simulated copy with every fix above. The dispatch states 7,984 and 7,994; the 2-char gap is not material.

| Skill | Now | After fixes |
|---|---|---|
| `iap-server-receipt-ledger` | 7,986 | 8,350 |
| `firebase-unity-sdk` | 7,996 | 8,069 |
| `server-authoritative-validation` | 7,835 | 8,035 |
| `consent-att-init-order` | 7,962 | 7,997 |
| `crash-anr-reporting-gate` | 3,970 | 4,016 |

- **Three bodies pass 8,000:** restore anyway, per the template and the dispatch.
- **Consequence for AC11:** it requires no `file(s):` line, and `verify.ps1:114` counts `body > 8000` on that line. Now it reads `1 file(s)` for `feature`. With these fixes it stays alive past T4 unless AC11 is amended or those bodies are moved further. Not verified: how T5's `Soft` rename counts it.

## Hard tests from the dispatch

### Facts cut from `SKILL.md`

| Fact | Base | Now in | Word for word in substance | Trigger at the moment required | Result |
|---|---|---|---|---|---|
| Play state checks, response product id equals hint | iap `:23` | `google-play-developer-api.md:17`, `:19`, `:23` | yes | `SKILL.md:34` "per the platform reference"; bullet `:20` | pass |
| Apple JWS chain, bundle id, environment, type, revocation | iap `:23` | `app-store-server-api.md:14`, `:27`, `:29`, `:31`, `:33` | yes | `:34`; bullet `:21` | pass |
| Apple JWS refresh | iap `:23` | `app-store-server-api.md:19` | yes, plus default 24 h | loads, but `:34` omits it | finding |
| Restore: new `transactionId`, keeps original | iap `:24` | `app-store-server-api.md:25`, `:26`; `SKILL.md:39` keeps "a restore keeps it" | yes | rule stays in step 4; step 3 already loaded the file | pass |
| `purchaseToken` globally unique | iap `:24` | `google-play-developer-api.md:30`; `orderId` ban at `SKILL.md:39` | yes | as above | pass |
| UGS client-side redeem not supported | iap `:25` | `ugs-cloud-code-economy.md:9`, `:46` | yes, plus why | `SKILL.md:41` "per the backend reference"; `:47` keeps "made from the Cloud Code module"; bullet `:23` | pass |
| Voided poll 30-day window | iap `:28` | `google-play-developer-api.md:48` | yes, plus "or voids are lost" | `:55` "per platform reference"; bullet `:20` | pass |
| `includeQuantityBasedPartialRefund=true` | iap `:28` | `google-play-developer-api.md:50`, `:58`; `firebase-functions-firestore.md:42`; `ugs:70` | yes | same | pass |
| Match id, Apple `data.signedTransactionInfo` | iap `:28` | `app-store-server-api.md:53`; `google-play-developer-api.md:55`; `SKILL.md:56` "the grant key's id" | yes | same | pass |
| UGS never auto-retried | iap `:49` | `ugs:72` | yes | none at step 8 | finding |
| Apple local validation no-op | iap `:22`, `:54` | `app-store-server-api.md:7` | yes; ban stays at `SKILL.md:32` | iOS verification | pass |
| One version, one method, one manager | firebase `:22` | `setup-edm4u.md:19`-`:22`; title `SKILL.md:34` | yes | `:34` link; bullet `:21` | pass |
| EDM4U archive date | firebase `:22` | `setup-edm4u.md:29` ("read-only from 2026-10-26") | yes | `:34` | pass |
| Analytics off keys | firebase `:26` | `analytics.md:22`, `:26` | yes | link fires; pair not selected | finding |
| 500-type, 25-property limits | firebase `:27` | `analytics.md:68`, `:69` | yes | `SKILL.md:55` names the file | pass |
| Remote Config default and loading-screen strategy | firebase `:28` | `remote-config.md:36`-`:40`, `:43` | yes | title `:56` names the table | pass |
| Crashlytics collects from first launch | firebase `:29` | `crashlytics.md:23` | yes | `:60` unconditional link; output `:85` keeps "default-on" | pass |
| Crashlytics native off keys | firebase `:29` | `crashlytics.md:27`, `:28` | yes; no competing key there | `:61` | pass |

### Removed `## Scripts` entries, and the rest of the batch

| File | Usable without its reference | Decision | Reached through |
|---|---|---|---|
| `redeemPurchase.js` | no: four project functions, and `firebase-functions-firestore.md:11`, `:17` hold the App Check gap and the rule that clients cannot write the ledger; adapting without them leaves a client-writable ledger | omit is correct | iap `SKILL.md:41`, `:22` |
| `StartupConsentFlow.cs` | no: member fragment; seven project members and the `_isAttResolved` initial state are stated only in `google-ump.md:20`, `:24` | omit is correct | consent `SKILL.md:52` |
| `ConnectionRateLimiter.cs` | yes | list it: finding | SAV `SKILL.md:61` |
| `UseItemRpc.cs` | no: method fragment; six project members named only in `sender-identity-per-stack.md:24` | omit is correct | SAV `SKILL.md:42` |
| `SerializableTypes.cs` | no: a field line that cannot sit at file level (`serialization.md:32`) | omit is correct | NGO `SKILL.md:50` |
| `FastBufferExtensions.cs` | no: `Health` demo; registration is in the same section of the reference | omit is correct | NGO `SKILL.md:50` |
| `ServerUpdateLoop.cs` | no: fields declared elsewhere (`core-driver-lifecycle.md:66`) | omit is correct | transport `SKILL.md:30` |
| `ServerUpdateJob.cs` | no: demo body; scheduling caveats in the reference | omit is correct | transport `SKILL.md:35` |
| `FirebaseBootstrap.cs` | yes | listed, correct | firebase `SKILL.md:28` |

### Output fields removed

- **`Verified via` (`netcode-for-entities` `:58`):** survives at `SKILL.md:67`. "Or not run" is the envelope's `Not verified`.
- **`Verification` (`unity-transport` `:46`):** the run is step 9 (`SKILL.md:41`). "Or how confirmed" is the envelope's `Verified`. No domain limit lost; envelope field per the template.

### Adapt targets

| File | Target | Result |
|---|---|---|
| `FirebaseBootstrap.cs` | `Platform/DataControllers/` | taken from the Base fence comment; pass |
| `ConnectionRateLimiter.cs` | `Networking/Server/` | matches the Base namespace and `rate-limits-and-rejection.md` "limiter lives in `<Feature>/Server`"; pass |
| `ServerUpdateLoop.cs`, `ServerUpdateJob.cs` | `Networking/Server/` | PascalCase, `Server/` holds the netcode track; pass |
| `SerializableTypes.cs`, `FastBufferExtensions.cs` | `Networking/` | feature root, needs `UnityEngine` per `naming-convention.md:52`; pass |
| `redeemPurchase.js` | `functions/index.js` | outside the C# rules; no boundary touched; pass |
| `StartupConsentFlow.cs` | `Platform/` | naming passes; contradicts step 3; finding |
| `UseItemRpc.cs` | host only | reference correct, header wrong; finding |

### Other named items

- **Sub-steps (a)–(e):** every letter stays in a nested title at `SKILL.md:32`-`:38`, same subjects. (d) `:37` lost its object; finding. "(c) request it here" adds no fact.
- **`netcode-for-entities` step 13:** same meaning as Base; strict class, reason kept at `:69`.
- **`ugs-cloud-code-economy.md:72` pointer:** names the envelope's real field, `Limitations`. Pass, and keep it with the step 8 fix.
- **Apple sentence, `app-store-server-api.md:7`:** moved; "so a local result proves nothing" restates Base's "a client signal", no new fact. Pass.

## Cuts

| Skill | Base text | Class |
|---|---|---|
| `netcode-for-entities` `:61`, `netcode-for-gameobjects` `:48`, `unity-transport` `:50`, `server-authoritative-validation` `:47`, `magiconion-rpc-networking` `:39`, `iap-server-receipt-ledger` `:51`, `unity-test-framework` `:52`, `unity-profiler-diagnostics` `:51` | "On request only, add `Latent concerns` and `Future remediation`, each with its trigger." | Batch brief "Remove or move"; plain "each with its trigger", no named trigger lost |
| `crash-anr-symbolication` `:40`, `risk-based-test-planning` `:40`, `playtest-scenario-execution` `:42`, `performance-budget-verification` `:42` | Same line with `Known limitations` | Same |
| `netcode-for-gameobjects` `:45`, `:46` | `Verified`, `Known limitations` | Envelope field; step 9 |
| `server-authoritative-validation` `:44`, `:45` | `Verified`, `Known limitations` | Envelope field; step 9 `Not run` at `SKILL.md:72` |
| `consent-att-init-order` `:47`, `:48` | `Verified`; "Crashlytics withdrawal takes effect next launch" | Envelope field; limit stays at step 8 `SKILL.md:66` |
| `firebase-unity-sdk` `:49`, `:50` | `Verified`, `Known limitations` | Envelope field; `Verified: not run` stays at step 9 `SKILL.md:65` |
| `iap-server-receipt-ledger` `:48` | `Verified` | Envelope field; step 10 `SKILL.md:66` |
| `iap-server-receipt-ledger` `:49` | "subscriptions out" | Stays at `SKILL.md:14`, `:28`. The UGS half is a finding |
| `iap-server-receipt-ledger` `:11` | Parenthetical glosses of `core.md` Security and `csharp.md` Boundaries | Project rule cited by name; steps 2, 3 and 9 keep the rules |
| `magiconion-rpc-networking` `:37`, `unity-transport` `:48`, `unity-test-framework` `:49`, `:50`, `unity-profiler-diagnostics` `:49`, `netcode-for-entities` `:59` | `Verified`, `Known limitations: <...>` | Envelope field; no domain content |
| `crash-anr-reporting-gate` `:40`, `crash-anr-fault-domain-triage` `:49` | `Known limitations: <what this gate did not establish>`, `<what the samples do not establish>` | Envelope field; a prompt, not a limit |

- **Common knowledge cuts:** none in this batch.
- **`Never` bullets deleted:** none. `crash-anr-fault-domain-triage` `:32` split into two at `SKILL.md:51`, `:52`, each keeping its reason.

## Moves

The cut-fact table above lists every move in `iap-server-receipt-ledger` and `firebase-unity-sdk`, except:

| Skill | Base | Now |
|---|---|---|
| `firebase-unity-sdk` | `:24` "it triggers initialization outside the gate" | `setup-edm4u.md:62`, `crashlytics.md:15`; `SKILL.md:42` links it |
| `netcode-for-entities` | `:58` | `SKILL.md:67` |

## Moved code

Bodies compared with `git show <Base>:<reference>` under `core.autocrlf=false`, bytes against the file after its header. All 9 fences listed in `batches.md` are moved, none trimmed, each byte-identical including the final newline. All files use LF.

| Base reference | File | Header lines | Reference link | Result |
|---|---|---|---|---|
| `consent-att-init-order/references/google-ump.md:19` | `StartupConsentFlow.cs` | 3 | `:19` | body passes; target is a finding |
| `firebase-unity-sdk/references/setup-edm4u.md:51` | `FirebaseBootstrap.cs` | 3 | `:51` | pass |
| `iap-server-receipt-ledger/references/firebase-functions-firestore.md:29` | `redeemPurchase.js` | 3 | `:29` | pass |
| `netcode-for-gameobjects/references/serialization.md:31` | `SerializableTypes.cs` | 3 | `:31` | pass |
| `netcode-for-gameobjects/references/serialization.md:95` | `FastBufferExtensions.cs` | 3 | `:81` | pass |
| `server-authoritative-validation/references/rate-limits-and-rejection.md:20` | `ConnectionRateLimiter.cs` | 3 | `:20` | pass |
| `server-authoritative-validation/references/sender-identity-per-stack.md:22` | `UseItemRpc.cs` | 3 | `:22` | body passes; header is a finding |
| `unity-transport/references/core-driver-lifecycle.md:65` | `ServerUpdateLoop.cs` | 3 | `:65` | pass |
| `unity-transport/references/jobs-and-concurrent-api.md:24` | `ServerUpdateJob.cs` | 3 | `:24` | pass |

- **Facts the fences alone carried:** stated in the references or kept at the cited `SKILL.md` step. Each comment was read against its reference; none lost.
- **Scope of edits:** the 8 reference diffs hold only the fence-to-link swap; the other 2 are the Apple sentence and the UGS pointer.
- **Orphans after the swap:** a search for "above", "below", "the sample" and "the code" in the 8 references finds none pointing at a removed fence.

## Tokens

`token-survival.ps1` from the PowerShell tool: "TOTAL 16 skill(s), 3113 tokens, 41 missing", matching the author's report: 28 deleted by rule, 11 description compounds, 2 bold changes.

| Miss | Result |
|---|---|
| 28 `Latent concerns`, `Future remediation`, `Known limitations` in 12 skills | Confirmed; see Cuts |
| 11 description compounds: `ICommandData/IInputComponentData`, `NetworkObject/Behaviour/Manager`, `LoadAndShowConsentFormIfRequired`, `SetConsent/SetAnalyticsCollectionEnabled`, `SetDefaultsAsync/FetchAndActivateAsync`, `get/consume/acknowledge`, `crash/ANR` twice, `Edit/Play`, `GC/frame`, `ProfilerMarker/ProfilerRecorder` | Confirmed; each part at the author's citation. `purchases.products.get` is also at iap `SKILL.md:90` |
| `netcode-for-entities` step 13 bold | Confirmed; see Other named items |
| `firebase-unity-sdk` step 7 bold | Confirmed; only `;` became `:` |
| iap "1 found only in scripts/" | Resolved, which the author could not name: `` `${proof.store}:${proof.ledgerId}` ``. `firebase-functions-firestore.md:32` states the same id as `<store>:<ledgerId>` |

## Anchors

Every `anchors.md` row for these skills resolves to the same subject. Step numbers and subjects were compared by script against Base for all 16 skills; differences are trailing punctuation, a title that absorbed its own sentence, or a title split at its colon (`unity-transport` step 10), with the rest kept after it.

- **File anchors:** all 15 resolve.
- **`netcode-for-entities` step 13:** retitled `Missing input` per the inventory; no row cites it.
- **`crash-anr-reporting-gate` step 8:** new, after the last step.

## Ask

`ask-check.ps1`: 62 hits, 38 allowlisted, 4 resolved, 20 open, none in these 16 skills.

- **`netcode-for-entities:40`, `netcode-for-gameobjects:24`:** fix applied per inventory.
- **`crash-anr-reporting-gate:20`:** class applied, wording narrowed; finding.
- **Allowlisted fragments:** still match.

## Sections and scope

- **Sections:** all 16 have `## Steps`, as their class needs.
- **Frontmatter:** unchanged from `HEAD` in all 16.
- **`verify.ps1 -File`:** no skill-format WARN on any of the 16. Whole layer exit 0, 21 warnings.
- **`git status`:** only this batch's files, plus untracked `.workflow/`.
