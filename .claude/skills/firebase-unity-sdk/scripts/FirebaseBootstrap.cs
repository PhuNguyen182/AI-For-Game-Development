// The single Firebase init gate: awaits CheckAndFixDependenciesAsync and exposes IsAvailable.
// Adapt into: Assets/_Project/Scripts/Platform/DataControllers/FirebaseBootstrap.cs
// Unverified: not compiled or run (no Unity project in this repo).
// Assets/_Project/Scripts/Platform/DataControllers/FirebaseBootstrap.cs — the only caller of CheckAndFixDependenciesAsync.
using System.Threading;
using Cysharp.Threading.Tasks;
using Firebase;
using UnityEngine;

namespace _Project.Scripts.Platform.DataControllers
{
    public sealed class FirebaseBootstrap
    {
        public bool IsAvailable { get; private set; }

        public async UniTask<bool> InitializeAsync(CancellationToken token)
        {
            DependencyStatus status = await FirebaseApp.CheckAndFixDependenciesAsync()
                .AsUniTask()
                .AttachExternalCancellation(token);
            this.IsAvailable = status == DependencyStatus.Available;
            if (!this.IsAvailable)
            {
                Debug.LogError($"Firebase unavailable: {status}");
            }

            return this.IsAvailable;
        }
    }
}
