---
name: server-authoritative-validation
description: "Server checks on client RPCs, commands, hub calls: sender identity (NGO SenderClientId, NfE SourceConnection, MagicOnion ConnectionId), ownership, Core validation, per-connection rate limit, rejection. Use when a server applies client input."
user-invocable: false
---

# Server-Authoritative Validation

Not for: anti-cheat posture, detection tiers and bans (`anti-cheat-strategy`), the RPC/command/hub API of each stack (`netcode-for-gameobjects`, `netcode-for-entities`, `magiconion-rpc-networking`, `unity-transport`), the rule a check calls (`csharp-engineer`, Core), the sync model behind prediction and reconciliation (`netcode-architecture-decision`), lag-compensation bounds and contract scope (`technical-architect`, Tech Spec), store receipts and currency grants (`iap-server-receipt-ledger`), account token design (`security-reviewer`).
Docs: NGO https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/ · NfE https://docs.unity3d.com/Packages/com.unity.netcode@6.6/ · MagicOnion https://cysharp.github.io/MagicOnion/ (unversioned; members read from `main` source) — NGO pinned 2.13, NfE 6.6: swap the segment for the version in `Packages/manifest.json`; NGO legacy `[ServerRpc]` still compiles in 2.x and must be checked too.

| Reference | Read when |
|---|---|
| [sender-identity-per-stack.md](references/sender-identity-per-stack.md) | Writing a handler's first lines: which member names the sender, how to map it to an owned entity or account, how to drop the connection |
| [rate-limits-and-rejection.md](references/rate-limits-and-rejection.md) | Setting a per-connection budget, or deciding what the sender gets back and what is logged when a check fails |

## Steps
1. **Confirm the server is authoritative for this outcome** — a listen-server host's own input is the server and cannot be validated; NGO Distributed Authority has no server deciding owner-simulated state. Neither case is a validation task: report the gap as `Needs-decision`, routed to `anti-cheat-strategy` via `cto`. Proceed only for a dedicated server, or a host whose gap the GD accepted (write it in `Known limitations`).
2. **List every client→server entry point the change touches** — NGO `[Rpc(SendTo.Server)]`, legacy `[ServerRpc]`, custom messages; owner-authority state that bypasses every handler — `NetworkVariable` with owner write permission, `NetworkTransform`/`NetworkRigidbody`/`NetworkAnimator` in owner mode (`AuthorityMode.Owner` or `OnIsServerAuthoritative()` returning `false`), `AllowOwnerToParent` (`netcode-for-gameobjects` → `core-architecture.md`): convert each to server authority plus an input Rpc, or, if owner authority must stay, report it under step 1's `Needs-decision`; NfE `IRpcCommand` receive systems and `IInputComponentData`/`ICommandData`; MagicOnion service and hub methods; raw UTP `Data` events. Done when each entry point maps to one handler that steps 3–8 apply to.
3. **Take the sender from the transport, never the payload**, per [sender-identity-per-stack.md](references/sender-identity-per-stack.md). A payload field naming a player, owner, account or connection is deleted from the contract, and the written contract is updated in the same change. Done when no identity is read from message bytes.
4. **Authorize every entity the payload references** — resolve each reference server-side and compare its owner with the sender; NGO `InvokePermission = RpcInvokePermission.Owner` covers only the Rpc's own object, never a target named in the payload. An unresolvable reference is a rejection, same code as not-owned.
5. **Make the decode cost fixed, then bounds-check it** — NGO codegen deserializes typed `[Rpc]` parameters before the body runs, so a `string` or array parameter is allocated at a client-chosen size before any limiter or cap can act. Client→server Rpc parameters are fixed-size (`FixedString*Bytes`, fixed-count `INetworkSerializeByMemcpy` structs); variable-length client data goes through a named custom message whose handler reads with `TryBeginRead`/`ReadValueSafe` after the limiter (`netcode-for-gameobjects` → `serialization.md`, `state-sync.md`). A variable-length typed parameter that must stay → `Known limitations`: "decoded before rate limit". UTP: check `DataStreamReader.HasFailedReads` after reading. Everywhere: cap client-sent lengths before allocating, range-check enums and indices, reject non-finite floats. Done when a malformed payload produces a rejection, never an escaped exception or a client-sized allocation.
6. **Validate through Core before any state change** — the handler passes server state, server tick and the decoded intent to the Core rule and mutates only on its accept (rule `core.md` Security: authoritative outcomes never trust a client value; rule `csharp.md` Boundaries). A client time or tick is at most a hint bounded by the Tech Spec; bound absent → `Needs-decision`, `Next: technical-architect`. No Core API for the check → `Blocked`, `Next: csharp-engineer`; never write the rule in the handler.
7. **Apply a per-connection rate limit with a stated budget** — keyed by the step 3 identity, checked before any decoding the handler controls (custom-message reads) and before Core; typed Rpc parameters are already decoded by then (step 5), per [rate-limits-and-rejection.md](references/rate-limits-and-rejection.md). Budget absent from the contract → derive it from the tick rate or the GDD action rate and state it in Output.
8. **Reject with authoritative state, leak nothing** — the sender gets a closed reason code and only state it may already see; the server logs connection id, entry point, reason and tick, per [rate-limits-and-rejection.md](references/rate-limits-and-rejection.md). Escalation threshold to disconnect stated in Output.
9. **Test every rejection path in a multi-client run** — forged identity, non-owned target, malformed and oversized payload, burst over budget, out-of-range value; each asserts server state unchanged. NGO `NetcodeIntegrationTest`, NfE thin clients; tests owned by `qa-automation-engineer` when the author is not writing them. Not run → `Verified: not run`.

## Never
- Swallow a decode or validation exception and apply the message anyway — fail closed (rule `core.md` Security).
- Count a client-side guard (disabled button, client `IsOwner` check) as validation — a modified client sends the message regardless.
- Log the raw payload, an account id or any player PII on rejection.

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
- Verified: <rejection tests run, or "not run">
- Known limitations: <...>
```
On request only, add `Latent concerns` and `Future remediation`, each with its trigger.

## Example
- "The client sends `{playerId, itemId, goldAfter}`; just check `playerId` matches the owner" → declined: `playerId` is forgeable and `goldAfter` is a client outcome. Sender from `SenderClientId`, payload cut to `itemId`, gold computed by the Core rule on the server.
