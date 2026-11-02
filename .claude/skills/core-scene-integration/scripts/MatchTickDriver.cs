// IFixedTickable tick owner: the only call site that advances MatchSimulation, with command, snapshot and contact handling per tick.
// Adapt into: Assets/_Project/Scripts/Match/DataControllers/MatchTickDriver.cs
// Unverified: not compiled or run (no Unity project in this repo).
using _Project.Scripts.Match.Core;
using _Project.Scripts.Match.DataModels;
using VContainer.Unity;

namespace _Project.Scripts.Match.DataControllers
{
    // The only call site that advances MatchSimulation (_Project.Scripts.Match.Core).
    public sealed class MatchTickDriver : IFixedTickable
    {
        private readonly MatchSimulation _simulation;
        private readonly CommandSampler _sampler;
        private readonly ContactBuffer _contacts;
        private readonly BodyApplier _bodies;
        private readonly MatchSnapshots _snapshots;
        private readonly float _stepSeconds;
        private int _tick;

        public MatchTickDriver(
            MatchSimulation simulation,
            CommandSampler sampler,
            ContactBuffer contacts,
            BodyApplier bodies,
            MatchSnapshots snapshots,
            TickSettings settings)
        {
            this._simulation = simulation;
            this._sampler = sampler;
            this._contacts = contacts;
            this._bodies = bodies;
            this._snapshots = snapshots;
            this._stepSeconds = settings.StepSeconds;
        }

        public void FixedTick()
        {
            PlayerCommand command = this._sampler.Consume();
            this._snapshots.ShiftCurrentToPrevious();
            this._simulation.Tick(this._tick, this._stepSeconds, command, this._contacts.Pending);
            this._contacts.Clear();
            // Core-owned quantities reach kinematic bodies before the physics step that follows.
            this._bodies.Apply(this._simulation.State);
            this._snapshots.CaptureCurrent(this._simulation.State);
            this._tick++;
        }
    }
}
