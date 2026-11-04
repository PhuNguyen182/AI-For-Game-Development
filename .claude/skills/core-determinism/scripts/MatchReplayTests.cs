// Replay test: two fresh runs agree on a per-tick state hash, and a run matches a committed golden hash list.
// Adapt into: Assets/_Project/Scripts/Match/Tests/EditMode/MatchReplayTests.cs
// Unverified: not compiled or run (no Unity project in this repo).
using System.Collections.Generic;
using _Project.Scripts.Match.Core;
using NUnit.Framework;

namespace _Project.Scripts.Match.Tests.EditMode
{
    public sealed class MatchReplayTests
    {
        private const int TickCount = 3600;
        // Must equal the production TickSettings.StepSeconds.
        private const float StepSeconds = 1f / 60f;

        [TestCase(1u)]
        [TestCase(48271u)]
        public void Replay_SameSeedAndInputs_SameHashEveryTick(uint seed)
        {
            IReadOnlyList<ReplayFrame> frames = ReplayFixtures.Frames(seed, TickCount);
            ulong[] first = this.Run(seed, frames);
            ulong[] second = this.Run(seed, frames);

            for (int tick = 0; tick < TickCount; tick++)
            {
                Assert.That(second[tick], Is.EqualTo(first[tick]), $"First divergence at tick {tick}");
            }
        }

        [TestCase(1u)]
        public void Replay_MatchesGoldenHashes(uint seed)
        {
            IReadOnlyList<ReplayFrame> frames = ReplayFixtures.Frames(seed, TickCount);
            ulong[] golden = ReplayFixtures.GoldenHashes(seed);
            ulong[] actual = this.Run(seed, frames);

            for (int tick = 0; tick < TickCount; tick++)
            {
                Assert.That(actual[tick], Is.EqualTo(golden[tick]), $"Drift from golden at tick {tick}");
            }
        }

        private ulong[] Run(uint seed, IReadOnlyList<ReplayFrame> frames)
        {
            MatchSimulation simulation = new MatchSimulation(seed);
            ulong[] hashes = new ulong[frames.Count];
            for (int tick = 0; tick < frames.Count; tick++)
            {
                ReplayFrame frame = frames[tick];
                simulation.Tick(tick, StepSeconds, frame.Command, frame.Contacts);
                hashes[tick] = MatchStateHash.Compute(simulation.State);
            }

            return hashes;
        }
    }
}
