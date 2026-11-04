# Data Containers and Variable SOs

Sources: Manual `class-ScriptableObject.html`; `CreateAssetMenuAttribute`. Pattern shapes follow Ryan Hipple's "Game Architecture with Scriptable Objects" (Unite Austin 2017); not an official Unity subsystem.

| Shape | Structure | Use when |
|---|---|---|
| Data Container SO | One `[CreateAssetMenu]` asset with several related read-only fields (`SO_EnemyStats`: `maxHealth`, `moveSpeed`) | Related constants shared by many prefabs of one kind |
| Variable SO | One primitive behind a `Value` property (`FloatVariable`, `IntVariable`, `BoolVariable`) | One named quantity (master volume, difficulty multiplier) read or written by unrelated scripts without a static or singleton |
| Reference wrapper | `[Serializable] struct FloatReference` with `useConstant`, `constantValue`, a `FloatVariable` field, and `implicit operator float` | A designer picks per instance between the shared Variable and a local one-off value; the implicit conversion hides the choice from consumers |

- A Data Container is never mutated at runtime, so it needs no reset. A Variable written at runtime needs [dual-serialization.md](dual-serialization.md).
- A Variable's `Value` is one shared asset field, not per-instance state: a write changes what every reader sees next. Use only for values global to the system. Per-instance state (one enemy's current health) belongs on that component or in Core.
