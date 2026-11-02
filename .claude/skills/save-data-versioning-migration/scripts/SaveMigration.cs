// Migration chain contract: ISaveMigration, SaveMigration<TFrom,TTo> and SaveMigrationChain with one step per version gap.
// Adapt into: Assets/_Project/Scripts/Save/Core/SaveMigration.cs
// Unverified: not compiled or run (no Unity project in this repo).
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
