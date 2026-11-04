# Crashlytics

Sources: [a] `/crashlytics/unity/get-started`, [b] `/crashlytics/unity/customize-crash-reports` (both under https://firebase.google.com/docs), [c] https://github.com/firebase/firebase-unity-sdk/blob/main/crashlytics/src/Crashlytics.cs, [d] https://firebase.google.com/docs/crashlytics/android/customize-crash-reports, [e] https://firebase.google.com/docs/crashlytics/ios/customize-crash-reports.

## API (`Firebase.Crashlytics.Crashlytics`, static) [c]

| Member | Fact that decides |
|---|---|
| `ReportUncaughtExceptionsAsFatal` | Default `false`; `true` reports every uncaught C# exception as fatal, counting toward crash-free users and velocity alerts; upstream recommends `true` for new apps |
| `IsCrashlyticsCollectionEnabled` | Get/set; `true` when the platform flag is enabled or unset. The runtime override persists across launches and takes effect on the next launch [b] |
| `LogException(Exception)` | Non-fatal report |
| `Log(string)` | Breadcrumb sent with the next crash; 64 kB per session, oldest dropped [b] |
| `SetCustomKey(string, string)` | Max 64 pairs, ≤1 kB each; extra values dropped [b] |
| `SetUserId(string)` | An id, token or hashed value — never PII [b] |
| Early access | Touching any member before `CheckAndFixDependenciesAsync` initializes via `FirebaseApp.DefaultInstance`; exception handlers register only once the SDK is initialized [c] |

**Caveat:** with collection disabled, reports are kept on the device and sent if collection is enabled later [b] — opt-out is not deletion.

**Caveat:** opt-in reporting lowers the accuracy of event counts [b].

## Collection off until consent

By default Crashlytics collects for every user from the first launch [b]; the Unity page documents only the runtime override, which takes effect on the next launch. Off-until-consent therefore needs the native build-time keys:

| Platform | Key | Fact |
|---|---|---|
| Android manifest `<application>` | `<meta-data android:name="firebase_crashlytics_collection_enabled" android:value="false" />` | Turns off automatic collection [d] |
| iOS `Info.plist` | `FirebaseCrashlyticsCollectionEnabled` = `false` | Turns off automatic collection [e] |
| Runtime | `Crashlytics.IsCrashlyticsCollectionEnabled = true` after consent, `false` on withdrawal | Persists across launches; `false` takes effect on the next launch [b] |

## Symbols [a]

| Platform | Fact that decides |
|---|---|
| Android IL2CPP | `firebase crashlytics:symbols:upload --app=<FIREBASE_APP_ID> <symbols path>`; app id, not the package name; Mono builds skip this |
| Android symbols path | Exported project: `unityLibrary/symbols`; direct build: the symbols zip (enable "Create symbols.zip") |
| Android generator | `--generator=breakpad` (default); `csym` is legacy |
| Android NDK crashes | Included from Crashlytics Unity SDK 8.6.1 |
| iOS | The Editor plugin configures the exported Xcode project to generate and upload symbols each build |

Matching uploaded symbols to the crashing build is `crash-anr-symbolication`'s check.

## Verification [a]

| Step | Pass |
|---|---|
| Throw a `System.Exception` from a test script on a device build | Exception visible in `adb logcat` / Xcode console |
| Crashlytics dashboard | Report within minutes; none after five → enable debug logging |
| Analytics enabled | Breadcrumb logs appear with the crash |

Unverified: that the native off keys [d][e] are honoured by the Unity SDK's native layer (documented for native Android/iOS only) — confirm on a device build that no report reaches the console before consent; whether an opt-in set mid-session covers the rest of that session.
