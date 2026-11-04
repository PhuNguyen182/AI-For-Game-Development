# Rate Limits and Rejection

Synthesized from the stack pages listed in [sender-identity-per-stack.md](sender-identity-per-stack.md), plus NGO `api/Unity.Netcode.RpcTarget.html`; none of NGO 2.13, NfE 6.6 or MagicOnion documents a per-connection message rate limit, so the project supplies it.

## Budget

| Subject | Fact that decides |
|---|---|
| Unit | Messages per second per connection per entry point, plus a burst capacity; one token bucket per (connection, entry point) |
| Continuous input | One per tick: NGO `NetworkConfig.TickRate` (default 30 Hz, `netcode-for-gameobjects` → `transform-latency.md`) |
| NfE commands | Each packet resends older ticks redundantly (`netcode-for-entities` → `rpcs-and-commands.md`): count distinct ticks, never packets |
| Discrete actions | GDD maximum rate of the action (fire rate, cast rate); the Core cooldown still decides legality, the bucket only bounds cost |
| Burst | ≥ rate × worst expected jitter (s) + 1: evenly sent messages arrive clumped after a stall |
| Clock | Server tick count, not wall time: deterministic and testable; the limiter lives in `<Feature>/Server` code |
| Lifetime | Bucket created on connect, removed on disconnect; a missing bucket rejects (fail closed) |
| MagicOnion | Hub instance is per connection: keep the bucket in a hub field and no shared dictionary or lock is needed |
| Placement | First line of the handler, before the Core call and before any read the handler controls; a reject must cost O(1). NGO typed `[Rpc]` parameters are decoded by codegen before the body, so only fixed-size parameters keep that decode bounded; variable-length data uses a named custom message read after the limiter |
| Out of scope | Packet floods that never reach a handler (transport, relay, hosting DDoS protection): `unity-transport`, `backend-engineer` |

- **Sample:** [ConnectionRateLimiter.cs](../scripts/ConnectionRateLimiter.cs) — `ConnectionRateLimiter<TKey>` with `Add`, `Remove` and `TryConsume(connection, serverTick)`.
  - **Adapt into:** `Assets/_Project/Scripts/Networking/Server/ConnectionRateLimiter.cs`.
  - **Cost:** one message costs `tickRate` units; each server tick refills `ratePerSecond` units; capacity is `burst * tickRate`.
  - **Unknown connection:** `TryConsume` returns `false` (fail closed).

## Over budget and escalation

| Condition | Action |
|---|---|
| One message over budget | Drop it, no reply (a reply amplifies a flood); count it |
| Malformed payload | Reject and count; a genuine client never sends one, so its threshold is lower than the rate threshold |
| N rejections within a window of W ticks | Disconnect through the stack's member (sender-identity reference) with a generic reason; N, W stated in Output |
| Repeated pattern across sessions | Signal for the posture `anti-cheat-strategy` set; no ban or appeal logic here |

**Caveat:** a single rejection is normal under latency (a cooldown the client predicted as finished, a target that died in flight). Never disconnect on the first one.

## Rejection reply

| Case | Reply |
|---|---|
| Predicted action refused | Authoritative state of the affected entity, to the sender only. NGO: a server-written `NetworkVariable` already carries it; otherwise `[Rpc(SendTo.SpecifiedInParams)]` called with `this.RpcTarget.Single(sender, RpcTargetUse.Temp)` (cached target: never store it). NfE: the next snapshot of the predicted ghost corrects it, no message. MagicOnion: the method's return value or a `Client` receiver call |
| Request with a result | A closed enum reason code plus the authoritative value the request was about |
| Unknown, hidden or not-owned target | One shared code (`NotAllowed`): distinct codes let a client probe for entities it cannot see |
| Never in a reply | Values the sender cannot already see (other players' hidden state, RNG seed or draws, enemy cooldowns), exception text, stack traces, internal ids |

| Server log field | Rule |
|---|---|
| Connection id, entry point, reason code, server tick | Logged on every rejection |
| Raw payload, account id, player PII | Never logged (rule `core.md` Security) |
