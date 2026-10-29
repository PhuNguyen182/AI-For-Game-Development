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
| Clock | Server tick count, not wall time: deterministic and testable; the limiter lives in `Game.Server.*` |
| Lifetime | Bucket created on connect, removed on disconnect; a missing bucket rejects (fail closed) |
| MagicOnion | Hub instance is per connection: keep the bucket in a hub field and no shared dictionary or lock is needed |
| Placement | First line of the handler, before the Core call and before any read the handler controls; a reject must cost O(1). NGO typed `[Rpc]` parameters are decoded by codegen before the body, so only fixed-size parameters keep that decode bounded; variable-length data uses a named custom message read after the limiter |
| Out of scope | Packet floods that never reach a handler (transport, relay, hosting DDoS protection): `unity-transport`, `backend-engineer` |

```csharp
using System;
using System.Collections.Generic;

namespace Game.Server.Networking
{
    // Integer token bucket on server ticks: one message costs tickRate units, each tick refills ratePerSecond.
    public sealed class ConnectionRateLimiter<TKey> where TKey : IEquatable<TKey>
    {
        private readonly int _tickRate;
        private readonly int _ratePerSecond;
        private readonly int _capacity;
        private readonly Dictionary<TKey, Bucket> _buckets = new Dictionary<TKey, Bucket>();

        public ConnectionRateLimiter(int tickRate, int ratePerSecond, int burst)
        {
            this._tickRate = tickRate;
            this._ratePerSecond = ratePerSecond;
            this._capacity = burst * tickRate;
        }

        public void Add(TKey connection, int serverTick)
        {
            this._buckets[connection] = new Bucket(this._capacity, serverTick);
        }

        public void Remove(TKey connection)
        {
            this._buckets.Remove(connection);
        }

        public bool TryConsume(TKey connection, int serverTick)
        {
            if (!this._buckets.TryGetValue(connection, out Bucket bucket))
                return false;

            long refilled = bucket.Units + ((long)(serverTick - bucket.LastTick) * this._ratePerSecond);
            int units = (int)Math.Min(this._capacity, refilled);
            bool isAllowed = units >= this._tickRate;
            this._buckets[connection] = new Bucket(isAllowed ? units - this._tickRate : units, serverTick);
            return isAllowed;
        }

        private readonly struct Bucket
        {
            public readonly int Units;
            public readonly int LastTick;

            public Bucket(int units, int lastTick)
            {
                this.Units = units;
                this.LastTick = lastTick;
            }
        }
    }
}
```

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
