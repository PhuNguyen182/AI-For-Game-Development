# Version Envelope and Migration Chain

Sources (below the SKILL.md `Docs:` base, `?view=netstandard-2.1`): [a] `system.io.file.replace`, [b] `system.io.file.move`, [c] `system.io.filestream.flush`, [d] `system.security.cryptography.sha256`, [e] `system.buffers.binary.binaryprimitives`. Layout and chain shape synthesized from those APIs and `csharp.md`.

## Header layout

Fixed, little-endian, written with `BinaryPrimitives` [e] — never by the payload serializer, so a schema change can never move the version field.

| Offset | Field | Type | Fact that decides |
|---|---|---|---|
| 0 | Magic | 4 bytes, project constant | Wrong magic = not a save (or a pre-envelope legacy file: route it to a dedicated v0 reader step) |
| 4 | Envelope version | `ushort` | Versions the header itself; bump only if a header field is added |
| 6 | Schema version | `int` | Selects the frozen `SaveV{N}` deserializer and the first migration step |
| 10 | Save counter | `long` | +1 on every successful write; orders saves by recency (SKILL.md step 8) |
| 18 | Payload length | `int` | Checked against the remaining file length before any allocation |
| 22 | Hash | 32 bytes, SHA-256 [d] | Over header bytes 0–21 plus the payload, so a flipped schema or counter field reads as corrupt, not as too new |
| 54 | Payload | serializer bytes | MemoryPack or another serializer; deserialized only into the one frozen `SaveV{N}` the schema field selects — never a serializer that reads a type name from the bytes (SKILL.md Never) |

**Caveat:** `System.IO.Hashing` (CRC32/XxHash) is a separate NuGet package, not part of .NET Standard 2.1; `SHA256.Create()` is built in [d]. A new package goes through `security-reviewer` first (`core.md` Security).

## Load classification

Run in this order; the first match decides. File presence (first two rows) is checked in Client code; the rest is the classifier in `_Project.Scripts.Save.Core`, which takes bytes, never a path.

| # | Condition | Status | Action |
|---|---|---|---|
| 1 | No main file, valid temp file present | `RecoverTemp` | A swap was interrupted after the temp was complete: promote the temp, then classify again |
| 2 | No main file, no temp | `Empty` | New game |
| 3 | Length < 54 or wrong magic | `Corrupt` | Try the newest valid backup; none → surface to the player, keep the bytes, write nothing |
| 4 | Envelope version > known | `TooNew` | Checked before length and hash: a newer envelope may lay them out differently |
| 5 | Length field ≠ remaining bytes, or hash mismatch | `Corrupt` | As row 3 |
| 6 | Schema version > `CurrentSchemaVersion` | `TooNew` | Refuse: read-only session, saving and cloud upload disabled, prompt to update |
| 7 | Schema version < `MinSupportedVersion` | `Unsupported` | Refuse; dropping support is a GD decision, never a code default |
| 8 | Schema version < `CurrentSchemaVersion` | `NeedsMigration` | Backup, run the chain, validate, write, reload |
| 9 | Equal | `Current` | Deserialize, validate at the boundary (`csharp.md`) |

**Caveat:** a `TooNew` main file is never replaced by a backup restore, a migration or a new game — it is a newer build's valid save. Backup restore is for `Corrupt` only.

**Caveat:** a successful deserialize proves the bytes parsed, not that values are in range (`memorypack-serialization` step 9). Validate after the last step, before the runtime model sees the data.

## Chain contract

```csharp
using System;
using System.Collections.Generic;

namespace _Project.Scripts.Save.Core
{
    public interface ISaveMigration
    {
        int FromVersion { get; }

        object Apply(object source);
    }

    public abstract class SaveMigration<TFrom, TTo> : ISaveMigration
        where TFrom : class
        where TTo : class
    {
        public abstract int FromVersion { get; }

        public object Apply(object source)
        {
            return this.Migrate((TFrom)source);
        }

        protected abstract TTo Migrate(TFrom source);
    }

    public sealed class SaveMigrationChain
    {
        private readonly int _minSupportedVersion;
        private readonly ISaveMigration[] _steps;

        public SaveMigrationChain(int minSupportedVersion, int currentVersion, IReadOnlyList<ISaveMigration> steps)
        {
            if (steps.Count != currentVersion - minSupportedVersion)
            {
                throw new ArgumentException("Chain must have exactly one step per version gap.", nameof(steps));
            }

            this._minSupportedVersion = minSupportedVersion;
            this._steps = new ISaveMigration[steps.Count];
            for (int i = 0; i < steps.Count; i++)
            {
                if (steps[i].FromVersion != minSupportedVersion + i)
                {
                    throw new ArgumentException($"Step {i} must migrate from v{minSupportedVersion + i}.", nameof(steps));
                }

                this._steps[i] = steps[i];
            }
        }

        public object MigrateToCurrent(object source, int fromVersion)
        {
            object current = source;
            for (int i = fromVersion - this._minSupportedVersion; i < this._steps.Length; i++)
            {
                current = this._steps[i].Apply(current);
            }

            return current;
        }
    }
}
```

| Rule | Fact that decides |
|---|---|
| One frozen DTO per schema version | `SaveV1` … `SaveV{N}` in `_Project.Scripts.Save.DataModels.Versions`; the runtime model maps from the newest DTO only. A DTO is never a gameplay class (`memorypack-serialization` Never) |
| Deserialize once, serialize once | Bytes → `SaveV{stored}` → steps in memory → `SaveV{current}` → bytes; no intermediate bytes between steps |
| Steps are pure | Same input, same output; a default that depends on game rules calls the Core rule, never re-implements it |
| Chain built at startup and in a test | The constructor throws on a gap or duplicate, so a missing step fails the Edit Mode run, not a player's load |

## Atomic write (Client)

| Subject | Fact that decides |
|---|---|
| Temp file | Same directory as the save (`<name>.tmp`): `File.Replace` throws when source and destination are on different volumes [a] |
| `FileStream.Flush(true)` | Flushes intermediate OS buffers to disk as well as the stream buffer [c]; call it before the swap, or a power loss can leave a complete-looking rename of an empty file |
| `File.Replace(temp, save, backup)` | Swaps in the temp and moves the old save to `backup`; an existing backup is overwritten; `null` skips the backup [a] |
| `File.Replace` on a first save | Throws `FileNotFoundException` when the destination does not exist [a]: first save uses `File.Move(temp, save)` |
| `File.Move(src, dst, overwrite)` | .NET Core 3.0+ only; absent under .NET Standard 2.1 [b]. Two-argument `Move` throws `IOException` when the destination exists [b] |
| Copy-then-delete | Not atomic: a crash mid-copy leaves a partial destination [b]; never the swap |
| Rolling backup | `File.Replace`'s backup argument keeps the previous good save (`<name>.bak`) |
| Pre-migration backup | Separate copy of the original bytes, `<name>.v<N>.bak`, written before the first step runs; never overwritten by the rolling backup |
| Startup recovery | A leftover `.tmp` with a valid header and hash and no main file is promoted; any other leftover `.tmp` is deleted |

**Caveat:** `File.Replace` can throw `UnauthorizedAccessException` with "operation is not supported on the current platform" [a]. Catch that specific exception and fall back to `File.Delete(save)` + `File.Move(temp, save)` — not atomic, so the startup recovery row above is what makes it safe.

Unverified: that `File.Replace` maps to an atomic `rename(2)` and `Flush(true)` to `fsync` under IL2CPP on Android and iOS, and that `File.Replace` is supported on every target platform; WebGL persistence (IndexedDB-backed `persistentDataPath`) is not covered. Confirm with an interrupted-write test on each target device before claiming atomicity.
