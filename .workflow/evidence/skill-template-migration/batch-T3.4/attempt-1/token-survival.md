# Token survival explanations (T3.4 attempt 1)

Run: `token-survival.ps1 -Base bdf5c9ec70bf217ee9ed2763abd75fa4280b717c` with the 16 T3.4 skills. Final output: "TOTAL 16 skill(s), 3113 tokens, 41 missing". The tool printed "0 found only in scripts/" for every skill except iap-server-receipt-ledger, which printed "1 found only in scripts/" (it did not print which token; the moved `redeemPurchase.js` holds it). Every miss is explained below.

## Deleted by rule (batch brief "Remove or move"): 28 misses
- 16 misses: `Latent concerns` and `Future remediation` (2 tokens each) in 8 skills: netcode-for-entities, netcode-for-gameobjects, unity-transport, server-authoritative-validation, magiconion-rpc-networking, iap-server-receipt-ledger, unity-test-framework, unity-profiler-diagnostics. The "On request only, add ..." line after `## Output` was deleted in each.
- 12 misses: `Known limitations`, `Latent concerns` and `Future remediation` (3 tokens each) in crash-anr-symbolication, risk-based-test-planning, playtest-scenario-execution, performance-budget-verification. The same "On request only" line, deleted.
- Also deleted, not flagged by the tool: the `Verified:` and `Known limitations:` lines inside `## Output` fences (envelope owns them) in every skill that had them. Domain content in them:
  - iap-server-receipt-ledger: "subscriptions out" is in the `Not for:` bullet. "UGS: a reversal's decrement is not atomic with its event entry, stale `pending` events alert and are reconciled by hand, never auto-retried" is stated in `references/ugs-cloud-code-economy.md` (Reversal row); its pointer "(SKILL.md Output, Known limitations)" now reads "(report it in the return's `Limitations`)". "Crashlytics withdrawal takes effect next launch" (consent-att-init-order) is in step 8.
  - netcode-for-entities `Verified via: <emulation settings and Profiler tabs read>` moved into step 12 as "Report: the emulation settings and the Profiler tabs read, in `Verified`".
  - unity-transport `Verification:` and netcode-for-gameobjects `Verified:` are covered by steps 9 (multi-client run).
  - crash-anr-reporting-gate `Known limitations: what this gate did not establish`: no domain-specific limit.

## Description symbols (frontmatter unchanged in T3.4; lost in T2): 11 misses
The tool printed `symbol [SKILL.md:3]` for slash compounds in the Base description. Each part survives:
- netcode-for-entities `ICommandData/IInputComponentData`: `ICommandData` is in the current description; `IInputComponentData` is in the Example.
- netcode-for-gameobjects `NetworkObject/Behaviour/Manager`: `NetworkObject`, `NetworkBehaviour`, `NetworkManager` appear separately in steps 2 and 3.
- consent-att-init-order `LoadAndShowConsentFormIfRequired`: step 3 (b) keeps `ConsentForm.LoadAndShowConsentFormIfRequired`; the tool did not match the bare name at description position.
- firebase-unity-sdk `SetConsent/SetAnalyticsCollectionEnabled`: step 6 keeps both as `SetConsent` and `SetAnalyticsCollectionEnabled(...)`. `SetDefaultsAsync/FetchAndActivateAsync`: step 8 keeps `SetDefaultsAsync`, and `FetchAndActivateAsync` stays in `references/remote-config.md`.
- iap-server-receipt-ledger `get/consume/acknowledge`: steps 3 and 6 keep consume and acknowledge; `purchases.products.get` is in the Play reference.
- crash-anr-reporting-gate and crash-anr-symbolication `crash/ANR`: "crash" and "ANR" appear separately in the title and steps.
- unity-test-framework `Edit/Play`: step 2 keeps "Edit Mode" and "Play Mode".
- performance-budget-verification `GC/frame`: `GC` is in the current description and "frame budget" is in step 1.
- unity-profiler-diagnostics `ProfilerMarker/ProfilerRecorder`: steps 1, 9 and Never keep both as separate backticked words.

## Bold title changes: 2 misses
- netcode-for-entities step 13. The tool printed `bold [SKILL.md:40]: Tick rate, build topology or predicted-vs-interpolated unspecified -> ask`. The ask inventory (`netcode-for-entities:40`, class Strict) required a `Missing input` step without the assumption branch. Step 13 now reads "Missing input: tick rate, build topology or predicted-vs-interpolated unspecified -> dispatched agent `Blocked` or `Needs-decision`; main session `AskUserQuestion`", with the reason "gameplay code comes to depend on the guess" kept as a nested bullet.
- firebase-unity-sdk step 7. The tool printed `bold [SKILL.md:27]: Events follow the schema `sdk-platform-engineer` owns;`. The title is "Events follow the schema `sdk-platform-engineer` owns:"; only the trailing semicolon became the template's colon. The rest of the sentence ("no PII in event params, user properties or `SetUserId`") follows the title.

## Earlier misses fixed in this run
- unity-transport step 10: `Next: cto` was split into a nested bullet; restored to "return `Needs-decision`, `Next: cto` (foundation and topology) or `technical-architect` (feature spec)".
- server-authoritative-validation step 4: `InvokePermission = RpcInvokePermission.Owner` restored as one backticked title.
- magiconion-rpc-networking step 12, crash-anr-reporting-gate step 7, performance-budget-verification step 8, consent-att-init-order steps 5 and 7, firebase-unity-sdk step 8: bold titles restored to the Base text; the tool no longer flags them.
