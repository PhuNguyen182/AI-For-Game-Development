// Integer token bucket on server ticks: one message costs tickRate units, each tick refills ratePerSecond.
// Adapt into: Assets/_Project/Scripts/Networking/Server/ConnectionRateLimiter.cs
// Unverified: not compiled or run (no Unity project in this repo).
using System;
using System.Collections.Generic;

namespace _Project.Scripts.Networking.Server
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
