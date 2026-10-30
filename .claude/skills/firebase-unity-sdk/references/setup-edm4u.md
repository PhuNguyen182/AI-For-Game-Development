# Setup, Dependency Manager and Init Gate

Sources (below the SKILL.md `Docs:` base unless a full URL): [a] `/setup`, [b] `/build-debug-guide`, [c] https://firebase.google.com/support/release-notes/unity, [d] https://github.com/googlesamples/unity-jar-resolver, [e] https://unity.com/blog/external-dependency-manager, [f] https://firebase.google.com/docs/projects/api-keys.

## Version floor (14.x)

| Subject | Fact that decides |
|---|---|
| Unity | 2022.3 LTS minimum from 14.0.0 [c]; the setup page still says 2021 LTS [a] — the release note is the newer, binding statement |
| Android | `minSdkVersion` 24 from 14.0.0; emulators need a Google Play image [a][c] |
| iOS | iOS 15; Xcode 26.2+ [a]; 14.0.0 requires Swift Packages for the Firebase iOS dependencies, not CocoaPods [c]; libraries ship as `.xcframework` with arm64 simulator support [c] |
| 13.x line | Still patched (13.17.1 shipped with 14.1.0) [c]; the fallback for projects below Unity 2022.3 |
| Auth 14.0.0 break | `UserMetadata.CreationTimestamp` / `LastSignInTimestamp` return `System.DateTime` (UTC), not `ulong` epoch ms [c] |

## One version, one method

| Check | Fact |
|---|---|
| Same version | Every Firebase product and the dependency manager at one version [b] |
| One install method | Exclusively `.unitypackage` or exclusively Unity Package Manager [b]; the setup page documents only `.unitypackage` (Assets > Import Package > Custom Package) [a] |
| Desktop libraries | `.unitypackage` installs: every `FirebaseCppApp` library under `Assets/Firebase/Plugins/x86_64/` must share one version [b] |
| One dependency manager | Exactly one copy in the project; other plugins (Play, Facebook) embed their own [b][d] |
| Mixed versions found | Remove every Firebase SDK and reinstall at one version [b] |

## Dependency manager

| Subject | Fact that decides |
|---|---|
| Google EDM4U | Repository read-only from 2026-10-26; no further updates or fixes [d]; last versions bundled by Firebase: 1.2.187 (13.7.0), 1.2.189 (13.17.0) [c] |
| Unity External Dependency Manager | Unity Registry package "External Dependency Manager", free for Unity 2022.3+, built on an EDM4U fork, same `*Dependencies.xml` format [e] |
| Switching | Unity's package asks which manager to use when EDM4U is present; nothing is deleted; switch back from Assets > External Dependency Manager [e] |
| Keep EDM4U when | Another SDK brought it in and has not moved to Unity's EDM yet [e] |
| `*Dependencies.xml` | Lives under an `Editor/` folder; iOS entries are `<iosPod>` or `<remoteSwiftPackage>`/`<swiftPackage>`, `replacesPod` prevents both [d] |
| EDM4U `.unitypackage` | Upstream marks it not recommended (conflicts); prefer UPM [d] |

**Caveat:** a `.unitypackage` from another vendor that embeds EDM4U re-adds a second copy on import; delete the embedded copy [d].

## Config files

| File | Fact |
|---|---|
| `google-services.json` (Android), `GoogleService-Info.plist` (iOS) | Anywhere under `Assets/`; no suffix like `(2)` in the file name [a] |
| `Assets/StreamingAssets/google-services-desktop.json` | Generated for Editor/desktop; must match the downloaded file [b] |
| API key inside them | Identifies the project, not secret when restricted to Firebase APIs; protection is Security Rules + App Check, not key secrecy [f] |
| Gemini Developer API | Never on a public or shared key; its key never in code or config [f] |

**Caveat:** commit eligibility is `secret-and-supply-chain-scan`'s verdict, not this file's.

## Init gate

```csharp
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
```

**Caveat:** never name the namespace `*.Firebase` — `Firebase.FirebaseApp` inside it then resolves against the project namespace and fails to compile.

| Subject | Fact that decides |
|---|---|
| `CheckAndFixDependenciesAsync()` | Returns `Task<DependencyStatus>`; only `Available` makes the SDK safe to use [a] |
| `ContinueWithOnMainThread` | `Firebase.Extensions`; the documented continuation when not using UniTask [a] |
| Early static access | Calling a Crashlytics method before the check triggers initialization through `FirebaseApp.DefaultInstance` (Crashlytics source comment) |

Unverified: that Firebase Unity 14.1.0 resolves cleanly under Unity's External Dependency Manager rather than EDM4U; that the Unity package id is `com.unity.external-dependency-manager` (seen only in a doc URL [e]).
