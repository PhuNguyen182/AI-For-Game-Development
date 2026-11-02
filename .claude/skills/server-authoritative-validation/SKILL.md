---
name: server-authoritative-validation
description: "Server checks on client RPCs: SenderClientId, SourceConnection, ConnectionId, rate limit. Use when server takes input."
user-invocable: false
---

# Server-Authoritative Validation

- **Not for:** anti-cheat posture, detection tiers and bans (`anti-cheat-strategy`).
- **Not for:** the RPC/command/hub API of each stack (`netcode-for-gameobjects`, `netcode-for-entities`, `magiconion-rpc-networking`, `unity-transport`).
- **Not for:** the rule a check calls (`csharp-engineer`, Core).
- **Not for:** the sync model behind prediction and reconciliation (`netcode-architecture-decision`).
- **Not for:** lag-compensation bounds and contract scope (`technical-architect`, Tech Spec).
- **Not for:** store receipts and currency grants (`iap-server-receipt-ledger`).
- **Not for:** account token design (`security-reviewer`).
- **Docs:** NGO https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/ · NfE https://docs.unity3d.com/Packages/com.unity.netcode@6.6/ · MagicOnion https://cysharp.github.io/MagicOnion/
  - **Pins:** NGO 2.13, NfE 6.6; swap the segment for the version in `Packages/manifest.json`. MagicOnion is unversioned; members read from `main` source.
  - **NGO legacy:** `[ServerRpc]` still compiles in 2.x and must be checked too.

## References
- **[sender-identity-per-stack.md](references/sender-identity-per-stack.md):** Writing a handler's first lines: which member names the sender.
  - **Also:** how to map it to an owned entity or account, how to drop the connection.
- **[rate-limits-and-rejection.md](references/rate-limits-and-rejection.md):** Setting a per-connection budget, or deciding what the sender gets back and what is logged when a check fails.

## Scripts
- **[ConnectionRateLimiter.cs](scripts/ConnectionRateLimiter.cs):** adapt into `Assets/_Project/Scripts/Networking/Server/ConnectionRateLimiter.cs` → integer token bucket on server ticks.

## Steps
1. **Confirm the server is authoritative for this outcome:** two cases are not validation tasks.
   - **Listen-server host:** its own input is the server and cannot be validated.
   - **NGO Distributed Authority:** no server decides owner-simulated state.
   - **Either case:** report the gap as `Needs-decision`, routed to `anti-cheat-strategy` via `cto`.
   - **Proceed only for:** a dedicated server, or a host whose gap the GD accepted (write it in `Known limitations`).
2. **List every client→server entry point the change touches:**
   - **NGO:** `[Rpc(SendTo.Server)]`, legacy `[ServerRpc]`, custom messages.
   - **NGO owner-authority state that bypasses every handler:** per `netcode-for-gameobjects` → `core-architecture.md`.
     - **Variable:** `NetworkVariable` with owner write permission.
     - **Components in owner mode:** `NetworkTransform`/`NetworkRigidbody`/`NetworkAnimator` (`AuthorityMode.Owner` or `OnIsServerAuthoritative()` returning `false`).
     - **Parenting:** `AllowOwnerToParent`.
   - **Fix for owner-authority state:** convert each to server authority plus an input Rpc, or, if owner authority must stay, report it under step 1's `Needs-decision`.
   - **NfE:** `IRpcCommand` receive systems and `IInputComponentData`/`ICommandData`.
   - **MagicOnion:** service and hub methods.
   - **UTP:** raw `Data` events.
   - **Done when:** each entry point maps to one handler that steps 3–8 apply to.
3. **Take the sender from the transport, never the payload:** per [sender-identity-per-stack.md](references/sender-identity-per-stack.md).
   - **Payload identity:** a payload field naming a player, owner, account or connection is deleted from the contract, and the written contract is updated in the same change.
   - **Done when:** no identity is read from message bytes.
4. **Authorize every entity the payload references:** resolve each reference server-side and compare its owner with the sender.
   - **NGO `InvokePermission = RpcInvokePermission.Owner`:** covers only the Rpc's own object, never a target named in the payload.
   - **Unresolvable reference:** a rejection, same code as not-owned.
5. **Make the decode cost fixed, then bounds-check it:**
   - **NGO decode:** codegen deserializes typed `[Rpc]` parameters before the body runs, so a `string` or array parameter is allocated at a client-chosen size before any limiter or cap can act.
   - **Rpc parameters:** client→server Rpc parameters are fixed-size (`FixedString*Bytes`, fixed-count `INetworkSerializeByMemcpy` structs).
   - **Variable-length client data:** goes through a named custom message (`netcode-for-gameobjects` → `serialization.md`, `state-sync.md`).
   - **Custom message handler:** reads with `TryBeginRead`/`ReadValueSafe` after the limiter.
   - **Variable-length typed parameter that must stay:** `Known limitations`: "decoded before rate limit".
   - **UTP:** check `DataStreamReader.HasFailedReads` after reading.
   - **Everywhere:** cap client-sent lengths before allocating, range-check enums and indices, reject non-finite floats.
   - **Done when:** a malformed payload produces a rejection, never an escaped exception or a client-sized allocation.
6. **Validate through Core before any state change:** the handler passes server state, server tick and the decoded intent to the Core rule and mutates only on its accept.
   - **Rules:** `core.md` Security (authoritative outcomes never trust a client value) and `csharp.md` Boundaries.
   - **Client time or tick:** at most a hint bounded by the Tech Spec; bound absent → `Needs-decision`, `Next: technical-architect`.
   - **No Core API for the check:** `Blocked`, `Next: csharp-engineer`; never write the rule in the handler.
7. **Apply a per-connection rate limit with a stated budget:** per [rate-limits-and-rejection.md](references/rate-limits-and-rejection.md).
   - **Key:** the step 3 identity.
   - **Placement:** checked before any decoding the handler controls (custom-message reads) and before Core; typed Rpc parameters are already decoded by then (step 5).
   - **Budget absent from the contract:** derive it from the tick rate or the GDD action rate and state it in Output.
8. **Reject with authoritative state, leak nothing:** per [rate-limits-and-rejection.md](references/rate-limits-and-rejection.md).
   - **Sender gets:** a closed reason code and only state it may already see.
   - **Server logs:** connection id, entry point, reason, tick.
   - **Disconnect:** the escalation threshold is stated in Output.
9. **Test every rejection path in a multi-client run:** forged identity, non-owned target, malformed and oversized payload, burst over budget, out-of-range value.
   - **Each test:** asserts server state unchanged.
   - **Tools:** NGO `NetcodeIntegrationTest`, NfE thin clients; `qa-automation-engineer` owns them when the author is not writing them.
   - **Not run:** `Verified: not run`.

## Never
- **Swallowed exceptions:** swallow a decode or validation exception and apply the message anyway — fail closed (rule `core.md` Security).
- **Client-side guards as validation:** count a client-side guard (disabled button, client `IsOwner` check) as validation — a modified client sends the message regardless.
- **Logging payloads:** log the raw payload, an account id or any player PII on rejection.

## Output
```
## Server-Authoritative Validation — <feature / entry points>
- Authority: dedicated server | host (host input unvalidated — GD-accepted) | none → Needs-decision
- Entry points: <handler — stack member> per entry point
- Sender identity: <member per stack>; payload identity fields: none
- Ownership: <referenced entity → owner compared to sender>
- Decode: <*Safe / HasFailedReads / caps>
- Core validation: <Core API called before mutation>
- Rate limit: <entry point — rate/s, burst, over-budget action>
- Rejection behaviour: <reply: reason code + authoritative state; log fields; escalation: N in window → disconnect via member>
```

## Example
- **"The client sends `{playerId, itemId, goldAfter}`; just check `playerId` matches the owner":** declined.
  - **Why:** `playerId` is forgeable and `goldAfter` is a client outcome.
  - **Did instead:** sender from `SenderClientId`, payload cut to `itemId`, gold computed by the Core rule on the server.
