// ITickable command sampler: latches input per frame, MatchTickDriver consumes once per tick.
// Adapt into: Assets/_Project/Scripts/Match/DataControllers/CommandSampler.cs
// Unverified: not compiled or run (no Unity project in this repo).
using _Project.Scripts.Match.DataModels;
using UnityEngine;
using VContainer.Unity;

namespace _Project.Scripts.Match.DataControllers
{
    // Latches per frame; MatchTickDriver consumes once per tick.
    public sealed class CommandSampler : ITickable
    {
        private readonly PlayerControls _controls;
        private PlayerCommand _pending;

        public CommandSampler(PlayerControls controls)
        {
            this._controls = controls;
        }

        public void Tick()
        {
            Vector2 move = this._controls.Gameplay.Move.ReadValue<Vector2>();
            this._pending.MoveX = move.x;
            this._pending.MoveY = move.y;
            if (this._controls.Gameplay.Jump.WasPressedThisFrame())
                this._pending.Buttons |= CommandButtons.Jump;
        }

        public PlayerCommand Consume()
        {
            PlayerCommand command = this._pending;
            this._pending.Buttons = CommandButtons.None;
            return command;
        }
    }
}
