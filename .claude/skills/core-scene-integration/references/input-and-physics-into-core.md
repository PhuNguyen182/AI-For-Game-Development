# Input and Physics into Core

Sources (below the SKILL.md `Docs:` base): [fu] `script-reference/unityengine/monobehaviour/fixedupdate`, [eo] `manual/scripting/managing-update-order/execution-order`, [sim] `script-reference/unityengine/physics/simulate`, [rcc] `script-reference/unityengine/physics/reusecollisioncallbacks`. Input System Update Modes: `unity-input-system` → `migration-and-settings.md`.

## Input → per-tick command struct

| Subject | Fact that decides |
|---|---|
| Command struct | A plain `Game.Core.*` struct: axes as numbers, buttons as a flags enum; no `InputAction`, no `Vector2`. The same struct is what a replay records and what netcode later sends |
| Dynamic Update Mode (default) + tick in `FixedUpdate` | Reading `WasPressedThisFrame()` inside the tick fires twice in a frame with two fixed steps and never in a frame with zero [fu]: latch instead |
| Latch | Frame loop ORs press edges into the pending command and overwrites held axes with the latest value; the tick takes the command and clears the edges |
| Latency | VContainer runs `IFixedTickable` before `ITickable` in a frame (`vcontainer-dependency-injection` step 8), so a press latched in frame N reaches the tick of frame N+1 or later: one frame, accepted |
| Fixed Update Mode | Input events process per fixed step, so the tick may read actions directly; then never also read them in `Update` |
| Manual Update Mode | The owner calls `InputSystem.Update()` itself: replay or a test harness owning the clock |
| Camera look | Stays per-frame on the view side unless it decides an outcome; an aim direction that decides a hit enters the command at the fire tick |

```csharp
using Game.Core.Match;
using UnityEngine;
using VContainer.Unity;

namespace Game.Client.Match
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
```

## Physics → Core as plain data

| Subject | Fact that decides |
|---|---|
| Core-owned quantity | Core computes it; the owner applies it to a kinematic body with `MovePosition`/`MoveRotation` (`unity-3d-physics` step 3). Never read the Transform back as truth |
| Physics-owned quantity | A simulated body decides it; the owner reads it after the step and passes it to Core as a value. Core never writes it |
| Queries a rule needs | The owner runs the raycast or overlap before the Core tick with the non-allocating APIs (`unity-3d-physics`) and converts each hit to a Core struct (entity id, distance, point) |
| Contacts | `OnCollision*`/`OnTrigger*` fire during the physics step after `FixedUpdate` [eo], or inside `Physics.Simulate` in Script mode [sim]: append to a preallocated buffer, Core reads it on the next tick, then it is cleared |
| `Collision` instance | With `Physics.reuseCollisionCallbacks` on, one `Collision` object is reused for every callback [rcc]: copy the needed values inside the callback, never store the reference |
| Entity identity | A client component or map holds the Core entity id per collider; Core never sees `Collider` or `GameObject` |
| Vector type | Core uses its own struct or `System.Numerics`; conversions live in `Game.Client.*`. Whether Core math must agree across machines: `core-determinism` |

**Caveat:** a contact buffer cleared anywhere except right after the tick that read it either drops contacts (cleared before) or double-applies them (two ticks in one frame read the same buffer).

Unverified: whether `WasPressedThisFrame()` in Fixed Update Mode means "this fixed step" for every device type.
